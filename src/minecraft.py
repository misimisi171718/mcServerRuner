import logging as log
from itertools import chain
import time,sys,re
import config as cfg
from server import Server,ServerNotFount
from help import help

def listServers() -> None:
	servers:list[Server] = []
	for temp in  chain(*[list(folder.glob("*")) for folder in cfg.serverFolders]):
		if not temp.is_dir():
			continue
		servers.append(Server(temp.parts[-1]))
	
	filterRe = dict([ x.split("=") for x in sys.argv[2].split(",") ])
	try:
		parts = sys.argv[3]
	except:
		parts = "%{name} %{server-port}"
	parts = parts.split("%")
	first = parts[0]
	properties = []
	separatorText = []

	for x in parts[1:]:
		loc = x.find("}")
		if loc == -1:
			log.error(f"invalid format string {x}")
			sys.exit(1)
		properties.append(x[1:loc])
		separatorText.append(x[loc+1:])

	for server in servers:
		ok = True
		for key,val in filterRe.items():
			try:
				if not re.search(val, server.getProp(key)):
					ok = False
					break
			except:
				ok = False
				break
		if not ok:
			continue

		out = first
		for prop,string in zip(properties,separatorText):
			try:
				out += server.getProp(prop)
			except:
				out += "unkown"
			out += string
		print(out)


def main():
	cfg.init()
	if len(sys.argv) < 3:
		help()
	
	if sys.argv[1].lower() not in ["start","stop","restart","info"]:
		help()

	action = sys.argv[1].lower()

	if action == "info":
		listServers()
	else:
		try:
			s = Server(sys.argv[2])
		except ServerNotFount as ex:
			log.error(ex.message)
			sys.exit(1)

		if action in ["stop","restart"]:
			log.info("stoping server")
			s.stop()
			while s.online():
				time.sleep(1)
			log.info("server has stoped")
		if action in ["start","restart"]:
			if s.online():
				log.info("server is already runing")
				return
			try:
				debug = (sys.argv[3].lower() == "debug")
			except IndexError:
				debug = False
			s.start(debug)
			log.info("starting server...")

if __name__ == "__main__":
	main()