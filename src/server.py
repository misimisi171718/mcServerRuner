from datetime import datetime
from functools import cache
from typing import Dict,List
import subprocess as subp
import config as cfg
from builtins import Exception
from itertools import chain
import time, prompt, os

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

	@property
	def version(self) -> str:
		self._loadConfig()
		return self.mVersion

	@property
	def javaVersion(self) -> str:
		self._loadConfig()
		return self.mJavaVersion

	@property
	def jarFile(self) -> str:
		self._loadConfig()
		return self.mJarFile

	@property
	@cache
	def properties(self) -> Dict[str,str]:
		try:
			with open(self.path/"server.properties") as file:
				text = file.read()
				ret = {}
				for x in text.split("\n"):
					if "=" not in x:
						continue
					varName, value = x.split("=")
					ret[varName] = value
			return ret 
		except FileNotFoundError as e:
			raise NoServerPropertiesFile(f"server.properties file is not avalible for {self.name}") from e

	def sendCommand(self,cmd:str) -> str:
		subp.run(
			["screen","-S",
			"minecraft_"+self.name, 
			"-X", "stuff", cmd+"\n"])

	@cache
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
			ret.append("-Dlog4j.configurationFile="+str(cfg.ASSETS/"log4j2_112-116.xml"))
		elif 7 <= minor <= 11:
			ret.append("-Dlog4j.configurationFile="+str(cfg.ASSETS/"log4j2_17-111.xml"))
		return ret

	def getProp(self,name:str)->str:
		if name == "version":
			return self.version
		elif name == "jar-file":
			return self.jarFile
		elif name == "java-version":
			return self.javaVersion
		elif name == "online":
			return str(self.online())
		elif name == "name":
			return self.name
		elif name == "path":
			return self.path
		else:
			return self.properties[name]
	
	def backup(self) -> None:
		if self.online():
			self.sendCommand("save-off")
			self.sendCommand("save-all flush")
		#TODO: wait for the server to flush (not as a static wait time)
		timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
		subp.run(["borg", "create", f"{cfg.borgRepoPath}::{self.name}-{timestr}", self.path])
		if self.online():
			self.sendCommand("save-on")
	
	@classmethod
	@cache
	def getServerNames() -> List[str]:
		ret = []
		for temp in  chain(*[list(folder.glob("*")) for folder in cfg.serverFolders]):
			if not temp.is_dir():
				continue
			ret.append(temp.parts[-1])
		return ret