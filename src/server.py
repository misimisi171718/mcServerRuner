from datetime import datetime
from typing import Dict,List
import subprocess as subp
import config as cfg
import time
from builtins import Exception
import prompt
import os

class NoServerPropertiesFile(Exception): ...
class ServerFailedToStart(Exception): ...
class ServerNotFount(Exception): ...

class Server:
	def __init__(self,name:str) -> None:
		self.name = name
		for dir in cfg.serverFolders:
			if (dir/name).is_dir():
				self.path = dir/name
				break
		try:
			self.path
		except AttributeError:
			raise ServerNotFount(f"no server named {name}") from None

	def start(self,debug:bool) -> None:
		self.backup()
		args = []
		if not debug:
			args += ["screen", "-S"]
			args += ["minecraft_"+self.name]
			args += ["-dm"]
		args += [cfg.javaPaths[self.javaVersion()]]
		args += cfg.javaArgs
		args += self._log4ShellFixArg()
		args += ["-jar", self.jarFile(), "nogui"]
		subp.run(args,cwd=self.path)
		while not self.online():
			if not self.runing():
				raise ServerFailedToStart(f"{self.name}")
			time.sleep(1)

	def stop(self) -> None:
		self.sendCommand("stop")
		while self.runing():
			time.sleep(1)
	
	def online(self) -> bool:
		"""
		use /proc/net/tcp to get active network connections
		and search for the port of the server in the file
		more information on the file format see here
		https://metacpan.org/pod/Linux::Proc::Net::TCP
		"""
		with open("/proc/net/tcp") as file:
			text = file.read()
			return "00000000:"+hex(int(self.properties()["server-port"]))[2:].upper() in text

	def runing(self) -> bool:
		for x in os.listdir("/run/screen/S-"+os.environ["USER"]):
			if self.name in x:
				return True
		return False

	def version(self) -> str:
		try:
			return self.mVersion
		except AttributeError:
			self._loadConfig()
			return self.mVersion

	def javaVersion(self) -> str:
		try:
			return self.mJavaVersion
		except AttributeError:
			self._loadConfig()
			return self.mJavaVersion

	def jarFile(self) -> str:
		try:
			return self.mJarFile
		except AttributeError:
			self._loadConfig()
			return self.mJarFile

	def properties(self) -> Dict[str,str]:
		try:
			return self.mProperties
		except AttributeError:
			with open(self.path/"server.properties") as file:
				text = file.read()
				ret = {}
				for x in text.split("\n"):
					if "=" not in x:
						continue
					varName, value = x.split("=")
					ret[varName] = value
				self.mProperties = ret
			return self.mProperties
		except FileNotFoundError as e:
			raise NoServerPropertiesFile(f"server.properties file is not avalible for {self.name}") from e

	def sendCommand(self,cmd:str) -> str:
		subp.run(
			["screen","-S",
			"minecraft_"+self.name, 
			"-X", "stuff", cmd+"\n"])


	def _loadConfig(self) -> None:
		data = cfg.load(self.path/"config.json",[
			("javaVersion", lambda : str(prompt.javaVetsion())),
			("jarName"    , lambda : prompt.serverJarFile(self.path)),
			("gameVersion", prompt.minecrftVesrsion),
		])
		self.mJavaVersion = data[0]
		self.mJarFile     = data[1]
		self.mVersion  = data[2]

	def _log4ShellFixArg(self) -> List[str]:
		minor = int(self.version().split(".")[1])
		ret = []
		if minor == 17:
			ret.append("-Dlog4j2.formatMsgNoLookups=true")
		elif 12 <= minor <= 16:
			ret.append("-Dlog4j.configurationFile="+str(cfg.assets/"log4j2_112-116.xml"))
		elif 7 <= minor <= 11:
			ret.append("-Dlog4j.configurationFile="+str(cfg.assets/"log4j2_17-111.xml"))
		return ret

	def getProp(self,name:str)->str:
		if name == "version":
			return self.version()
		elif name == "jar-file":
			return self.jarFile()
		elif name == "java-version":
			return self.javaVersion()
		elif name == "online":
			return str(self.online())
		elif name == "name":
			return self.name
		elif name == "path":
			return self.path
		else:
			return self.properties()[name]
	
	def backup(self) -> None:
		if self.online():
			self.sendCommand("save-off")
			self.sendCommand("save-all flush")
		#TODO: wait for the server to flush (not as a static wait time)
		timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
		subp.run(["borg", "create", f"{cfg.borgRepoPath}::{self.name}-{timestr}", self.path])
		if self.online():
			self.sendCommand("save-on")