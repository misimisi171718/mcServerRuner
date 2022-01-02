#!/bin/sh
#old script that this program replaces its
#still usefull for single server deployments


# send a comand to the server
comand(){
	var="$1\n"
	screen -S minecraft_$name -X stuff "$var"
	unset var
}

startServer(){
	echo "starting server..."

	#check if the server is moded or not
	if [ -f arguments ];then
		args=$(cat arguments | grep -o '^[^#]*' | tr '\r\n' ' ')
	else
		echo "aguments file not found using default arguments"
		args="-Xms1024M -Xmx4G"
	fi
	java=$([ -d mods ] && echo "/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64/bin/java -server" || echo "java")

	if [  $debug -eq 0 ]
	then
		screen -S minecraft_$name -dm $java $args -jar $jarName nogui
	else
		echo "starting in debug mode"
		$java $args -jar $jarName nogui
	fi

	unset java
	unset args
}

stopServer(){
	echo "stoping server"
	comand stop

	#wiat untyl the serve is stoped
	while [ "$(screen -ls | grep minecraft_$name)" ]
	do
		sleep 1
	done
	echo "server stoped"
}

# get the name of the server
name=$(realpath $0 | awk -F "/" '{print $(NF-1)}')

#check if the server is online
online=$(screen -ls | grep minecraft_$name)

#go to the right directory
cd /home/minecraft/$name/

#get the name of the jar file
if [ $(ls | grep .jar | wc -l) -eq 1 ]
then
	jarName=$(ls | grep .jar)
else
	if [ -f jarName ]
	then
		jarName=$(cat jarName)
	else
		jarName=$(ls | grep .jar | awk 'NR==1')
		echo "### WARNING ### multiple jar files found the scrip might not be runing the right file"
		echo "the file can be specifyed by adding a file named jarName and typing the name if the jar file in it"
	fi
fi

#chek if debug mode is enabled
[ "$2" = "debug" ] && debug=1 || debug=0

case $1 in
	stop|p)stopServer;;
	comand|c)comand "$2";;
	start|t)[ -z "$online" ] && startServer || echo server is alredy runing;;
	restart|r)
		stopServer
		startServer
		;;
	*)
		echo unkown option
		echo avalible options
		echo start, stop, restart, comand
	;;
esac

