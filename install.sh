if [ $1 == "global" ]
then
    base=/usr
else
    base=$home
fi

shareBase=$base/share/minecraft
binBase=$base/bin

cp bin/minecraft $binBase
chmod +x $binBase/minecraft

cp src $shareBase
cp assets $shareBase

