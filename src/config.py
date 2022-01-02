from enum import Enum
from typing import Dict,List
import logging as log
import json
import pathlib as pl
import argparse
import signal
import sys
import prompt

class Action(Enum):
	START = 0
	STOP = 1
	RESTART = 2
	LIST = 3

class ListType(Enum):
	ALL = 0
	ONLINE = 1
	OFFLINE = 2

javaPaths: Dict[str,str] = {}
javaArgs: List[str] = []
serverFolders: List[pl.Path] = []

debugMode:bool = False
action:Action = Action.START
serverName:str = ""
serverFolder:pl.Path = ""
jarFile:str = ""
javaVersion:str = "default"
gameVesion:str = ""

getPort:bool = False
listType:ListType = ListType.ALL
assets:pl.Path = pl.Path.home()/".local/share/minecraft/assets"


def _addLog4ShellFixArg():
	global gameVesion
	global javaArgs
	global assets
	minor = int(gameVesion.split(".")[1])
	if minor == 17:
		javaArgs.append("-Dlog4j2.formatMsgNoLookups=true")
	elif 12 <= minor <= 16:
		javaArgs.append("-Dlog4j.configurationFile="+str(assets/"log4j2_112-116.xml"))
	elif 7 <= minor <= 11:
		javaArgs.append("-Dlog4j.configurationFile="+str(assets/"log4j2_17-111.xml"))

def _loadGlobalConfig():
	global javaPaths
	global javaArgs
	global serverFolders
	with open(pl.Path.home()/".config/minecraftRuner.json") as file:
		config = json.loads(file.read())
		if "javaPaths" in config:
			for vesion in config["javaPaths"]:
				javaPaths.update({int(vesion): config["javaPaths"][vesion]})
		if "javaArgs" in config:
			for arg in config["javaArgs"]:
				javaArgs.append(arg)
		
		if "serverPaths" in config:
			for arg in config["serverPaths"]:
				serverFolders.append(pl.Path(arg))

def _loadLocalCongig():
	global serverFolder
	global javaVersion
	global javaPaths
	global jarFile
	global gameVesion
	saveConfig = False
	confFile = serverFolder/"config.json"

	if not confFile.is_file():
		with open(confFile,"w") as file:
			file.write("{}")

	with open(confFile) as file:
		try:
			config = json.loads(file.read())
		except json.decoder.JSONDecodeError as e:
			log.error("failed to load server config file")
			log.error(e)
			sys.exit()
		if "javaVersion" in config:
			javaVersion = config["javaVersion"]
		else:
			saveConfig = True
			javaVersion = prompt.javaVetsion()

		if "jarName" in config:
			jarFile = config["jarName"]
		else:
			jarFile = prompt.serverJarFile()
			saveConfig = True
		if "gameVersion" in config:
			gameVesion = config["gameVersion"]
		else:
			gameVesion = prompt.minecrftVesrsion()
			saveConfig = True
		
	if saveConfig:
		with open(confFile,"w") as file:
			x = {
				"javaVersion": javaVersion,
				"jarName": jarFile,
				"gameVersion": gameVesion
			}
			file.write(json.dumps(x,indent=4))

def _parseArgs():
	argp = argparse.ArgumentParser(description="start and stop minecraft servers")
	argp.add_argument("-d","--debug",action="store_true", help="show server output")
	subp = argp.add_subparsers(dest="action")
	start = subp.add_parser("start",help="start a server")
	start.add_argument("server",nargs="?" ,type=str , help="server that you want to operate on")
	stop = subp.add_parser("stop",help="stop a server")
	stop.add_argument("server",nargs="?" ,type=str , help="server that you want to operate on")
	restart = subp.add_parser("restart",help="restart a server")
	restart.add_argument("server",nargs="?" ,type=str , help="server that you want to operate on")
	list = subp.add_parser("list",help="list information about servers")
	list.add_argument("type",help="type of server that you want to list",choices=["all","online","offline"])
	list.add_argument("-p","--port",help="print the port of the server", action="store_true")
	if len(sys.argv)==1:
		argp.print_help()
		sys.exit()
	return argp.parse_args()

def _setupListParams(args):
	global getPort
	global listType

	listType = ListType[str(args.type).upper()]
	getPort = args.port
	
def _setupStartRestartParams(args):
	global serverName
	global serverFolder
	global serverFolders
	if args.server:
		serverName = args.server
	else:
		serverName = pl.Path.cwd().parts[-1]

	isValid = False
	for folder in serverFolders:
		if (folder/serverName).is_dir():
			serverFolder = folder/serverName
			isValid = True
			break
	if not isValid:
		if args.server:
			log.error("no server named", serverName)
		else:
			log.error("current directory is not in the list of server paths")
		sys.exit()

	_loadLocalCongig()
	_addLog4ShellFixArg()

def init(): 

	global action
	global debugMode

	log.basicConfig(level=log.INFO,format='%(levelname)s: %(message)s')
	signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
	_loadGlobalConfig()

	args = _parseArgs()

	debugMode = args.debug
	action = Action[str(args.action).upper()]
	
	if action == Action.LIST:
		_setupListParams(args)
	else:
		_setupStartRestartParams(args)