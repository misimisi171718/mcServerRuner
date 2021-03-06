import logging as log
import time,sys,re
from typing import List
import config as cfg
from server import Server,ServerNotFount,ServerFailedToStart
from help import help

def listServers() -> None:
	servers:List[Server] = map(Server,Server.getServerNames())
	
	filterRe = dict([ x.split("=") for x in sys.argv[2].split(",") ])
	try:
		parts = sys.argv[3]
	except IndexError:
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
			except KeyError:
				out += "unkown"
			out += string
		print(out)


def main():
	cfg.init()
	if len(sys.argv) < 2:
		help()
	
	if sys.argv[1].lower() not in ["start","stop","restart","info","archive"]:
		help()

	action = sys.argv[1].lower()

	if action == "info":
		listServers()
	elif action == "archive" and len(sys.argv) == 2:
		for i in Server.getServerNames():
			s = Server(i)
			if(s.online()):
				continue
			log.info(f"starting backup for {i}")
			s.backup()
			log.info(f"backup finished for {i}")
	else:
		try:
			s = Server(sys.argv[2])
		except ServerNotFount as ex:
			log.error(ex.message)
			sys.exit(1)

		if action in ["stop","restart"]:
			log.info("stoping server")
			s.stop()
			while s.runing():
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
			log.info("starting server")
			try:
				s.start(debug)
				log.info("server started")
			except ServerFailedToStart:
				log.error("server failed to start")
		if action == "archive":
			log.info("starting backup")
			s.backup()
			log.info("backup finished")

if __name__ == "__main__":
	main()