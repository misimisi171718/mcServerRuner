from typing import Callable, Dict
import pathlib as pl
import config as cfg
from builtins import Exception
from functools import cache

class InfoNotFountError(Exception): ...

@cache
def _readPropertiesFile(name:str)->Dict[str,str]:
	path = absPath(name)
	try:
		with open(path/"server.properties") as file:
			text = file.read()
			ret = {}
			for x in text.split("\n"):
				if "=" not in x:
					continue
				varName, value = x.split("=")
				ret[varName] = value
			return ret
	except FileNotFoundError as e:
		raise InfoNotFountError(f"server.properties file is not avalible for {name}") from e

def port(name:str) -> int:
	try:
		return int(_readPropertiesFile(name)["server-port"])
	except FileNotFoundError as e:
		raise InfoNotFountError("no port is avalible for server") from e

@cache
def absPath(name:str) -> pl.Path:
	for dir in cfg.serverFolders:
		if (dir/name).is_dir():
			return dir/name
	raise InfoNotFountError("no server named "+name) from None
