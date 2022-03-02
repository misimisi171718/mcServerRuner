from typing import Callable, Dict, List, Tuple
import logging as log
import pathlib as pl
import json, signal, sys, prompt

javaPaths: Dict[str,str] = {}
javaArgs: List[str] = []
serverFolders: List[pl.Path] = []
borgRepoPath: pl.Path = ""

assets:pl.Path = pl.Path.home()/".local/share/minecraft/assets"

#TODO: add borg prune and compat some where may be at the start of the program?

def load(fileName:pl.Path,variabels:List[Tuple[str,Callable]])->List:
	if not fileName.is_file():
		with open(fileName,"w") as file:
			file.write("{}")

	save = False
	with open(fileName) as file:
		try:
			data = json.loads(file.read())
		except json.decoder.JSONDecodeError as e:
			log.error(f"failed to load config file {fileName}")
			log.error(e)
			sys.exit()
		ret = []
		for name, function in variabels:
			if name in data:
				ret.append(data[name])
			else:
				save = True
				ret.append(function())
	
	if save:
		with open(fileName, "w") as file:
			for i, namefun in enumerate(variabels):
				name , fun = namefun
				data[name] = ret[i]
			file.write(json.dumps(data,indent=4))

	return ret

def _loadGlobalConfig():
	global javaPaths
	global javaArgs
	global serverFolders
	global borgRepoPath
	data = load(pl.Path.home()/".config/minecraftRuner.json",[
		("javaPaths"  ,lambda:{ x.parts[-1]: str(x) for x in list(pl.Path("/usr/lib/jvm").glob("*"))}),
		("javaArgs"   ,lambda:["-Xms:2G","-XmX:4G"]),
		("serverPaths",prompt.serverPaths),
		("borgPath"   ,prompt.borgPath),
	])
	javaPaths     = data[0]
	javaArgs      = data[1]
	serverFolders = [pl.Path(x) for x in data[2]]
	borgRepoPath  = pl.Path(data[3])


def init(): 
	log.basicConfig(level=log.INFO,format='%(levelname)s: %(message)s')
	signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
	_loadGlobalConfig()