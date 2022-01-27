import pathlib as pl

settings = {
    "allow-flight": True,
    "server-port": 25546,
    "enable-status": True,
    "query.port": 25546,
    "enable-query": True,
    "rcon.port": 25646,
    "enable-rcon": True,
    "rcon.password": "U4Vl\!7dlo4\#CS32NVl",
}

p = pl.Path(".")
for dir in p.iterdir():
    if not dir.is_dir():
        continue
    props = dir/"server.properties"
    if not props.is_file():
        continue

    port = int(str(dir)[5:]) + 25500
    settings["server-port"] = port
    settings["query.port"] = port
    settings["rcon.port"] = port = 100

    with open(props) as file:
        text = file.read().split("\n")
        toWrite = ""
        for setting in text:
            if "#" in setting or len(setting) == 0:
                toWrite += setting + "\n"
                continue
            name, value = setting.split("=")
            if name in settings:
                toWrite += name + "=" + settings[name] + "\n"
            else:
                toWrite += name + "=" + value + "\n"
        print(toWrite)