from typing import List,TypeVar

import config as cfg
import logging as log
import sys
import pathlib as pl
import subprocess as subp

T = TypeVar("T")
def _prompt(prompt:str,options: List[T])->T:
	print(prompt,": ")
	for i, x in enumerate(options):
		print(i,")",x)
	id = len(options)
	while id >= len(options):
		try:
			id = int(input("enter the id of the one you want to select:"))
		except ValueError:
			pass
	return options[id]

def minecrftVesrsion()->str:
	minorVersion = 18
	patchVersion = [0,0,5,2,7,2,4,10,9,4,2,2,2,2,4,2,5,1,1]
	version = ["1."+str(x) for x in list(range(minorVersion+1))]
	version = _prompt("select your minor version",version)
	minor = int(version.split(".")[1])
	version = [version+"."+str(x) for x in list(range(patchVersion[minor]+1))]
	return _prompt("select your patch vesion", version)

def serverJarFile( path:pl.Path)->str:
	jarfiles = list(path.glob("*.jar"))
	if len(jarfiles) == 0:
		log.error("no jar file in server folder")
		sys.exit()
	elif len(jarfiles) == 1:
		return str(jarfiles[0].parts[-1])
	else:
		return str(_prompt(
			"jar file not selected for this server avalible options are",
			[x.parts[-1] for x in jarfiles]))

def javaVetsion()->str:
	return _prompt("java version not selected avalible options are", list(cfg.javaPaths.keys()))

def serverPaths():
	path="x"
	ret = []
	print("enter the paths where the servers are located")
	print("thes folders will be searched for servers")
	while path != "":	
		path = input("enter a path: ")
		if pl.Path(path).is_dir():
			ret.append(path)
		else:
			print("path dosent exist")
	return ret

def borgPath() -> str:
	path = "x"
	while not pl.Path(path).is_dir():
		print("enter an exiting path wer the borg repository will be stored for archiveing")
		path = input()
	
	subp.run(["borg", "init", "-e", "none", path])

	return path