#!/bin/bash

clear

menu () { while true
do

tput setaf 51;

echo ""
echo " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
echo ""
echo "0. Create virtual env | 1. Launch venv"
echo "2. Exit venv "
echo "X. Exit script"
echo ""
echo " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
echo ""
read -p "Wpisz numer: " numer
case $numer in
	0) createVenv;;
	1) startVenv;;
	2) wyjdz;;
	x|X) exit;;

esac
done
}
createVenv(){
    echo ""
    echo -n $nazwave "Nazwij środowisko: "
    read nazwave
    virtualenv $nazwave
    $SHELL
}

startVenv(){
    echo ""
    # echo -r $nazwave "Wpisz: "
    # read nazwave
    source my_env/bin/activate
}
menu
