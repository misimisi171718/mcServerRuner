import subprocess
import logging as log
from itertools import chain
import time
import config as cfg
from config import Action,ListType

def sendCommand(command:str):
	subprocess.run(
		["screen","-S",
		"minecraft_"+cfg.serverName, 
		"-X", "stuff", command+"\n"])

def isOnline(name):
	try:
		out = subprocess.check_output(["screen", "-ls"])
	except subprocess.CalledProcessError as e:
		out = e.output
	return "minecraft_"+name in str(out)

def startServer() -> None:
	if isOnline(cfg.serverName):
		log.info("server is already runing")
		return
	log.info("starting server ...")
	args = []
	if not cfg.debugMode:
		args.append("screen")
		args.append("-S")
		args.append("minecraft_"+cfg.serverName)
		args.append("-dm")
	args.append(cfg.javaPaths[cfg.javaVersion])
	args.extend(cfg.javaArgs)
	args.append("-jar")
	args.append(cfg.jarFile)
	args.append("nogui")
	subprocess.run(args,cwd=cfg.serverFolder)

def stopServer() -> None:
	log.info("stoping server")
	sendCommand("stop")
	while isOnline(cfg.serverName):
		time.sleep(1)
	log.info("server has stoped")

def listServers() -> None:
	servers = [list(folder.glob("*")) for folder in cfg.serverFolders]
	servers = list(chain(*servers))
	for server in servers:
		if not server.is_dir():
			continue
		name = server.parts[-1]
		if cfg.listType != ListType.ALL:
			online = isOnline(name)
			if cfg.listType == ListType.ONLINE and not online:
				continue
			elif cfg.listType == ListType.OFFLINE and online:
				continue
		
		port = ""
		if cfg.getPort:
			try:
				with open(server/"server.properties") as file:
					text = file.read()
					for x in text.split("\n"):
						if "=" not in x:
							continue
						varName, value = x.split("=")
						if varName == "server-port":
							port = value
			except FileNotFoundError:
				port = "unkown"

		print(name,port)
		

def main():
	cfg.init()
	if cfg.action == Action.START:
		startServer()
	elif cfg.action == Action.STOP:
		stopServer()
	elif cfg.action == Action.RESTART:
		stopServer()
		startServer()
	elif cfg.action == Action.LIST:
		listServers()

if __name__ == "__main__":
	main()