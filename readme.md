# Mc Server Runner

this program helps you manage minecraft servers on a server
available options are:
- `start [name]`: start a server with a the given name
- `stop [name]`: stop a server with the given name 
- `restart [name]`: restart a server with the given name
- `list [condition] ?[format]`: list servers in a given format
- `archive ?[name]` : create an archive for the named server if no 
name is given the all online servers will be archived

## list format

in both the condition and the format parameter has a set of
information available to them thees are
 - `version` : version 
 - `jar-file` : name of the jar file that will be ran
 - `java-version` : java version required by the server
 - `online` : the current status of the server
 - `name` : name of the server
 - `path` : absolute path to the folder of the server
 and any that that is in the `server.properties` is
 available under the same name 

### condition

the condition is a list of key value pairs separated in this
format
```
key=value,key=value
```
the key is can be any parameter mentioned above and the value
is a regex the will have to match the value for the server to
be printed

### format

the format is interpreted literally except for the "`%`" charter
witch must be followed by "`{}`" in witch you must name a valid
parameter

example
```
name = %{name}, version = %{version}
```
this will be formatted to
```
name = creative server name, version = 1.18.1
```

## dependencies

this project depends on to programs

[gnu screen](https://www.gnu.org/software/screen/) for the serves
to be contained in
and [borg backup](https://borgbackup.readthedocs.io/en/stable/index.html)
for the backups
