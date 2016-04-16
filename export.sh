#!/bin/sh

file="/mnt/excelusb/SensoryWalk.xlsx"

#sleep is to enable the drive sufficient time to be recognized by the system before trying to mount (if the drive was just plugged in before button press)
sleep 3

#first mount the usb drive to the designated mount point
sudo mount -U "5BCF-16E1" /mnt/excelusb -o uid=pi,gid=pi

#remove any existing excel spreadsheet
if [ -f $file ] ; then
    rm $file
fi

NOW=$(date +"%m-%d-%Y--%H-%M")
EXT=".xlsx"
NAME="SensoryWalk-"
DIR="/mnt/excelusb/"

FPATH=$DIR$NAME$NOW$EXT

#then copy over the excel spreadsheet to the mount point
cp SensoryWalk.xlsx $FPATH

#then unmount the usb drive
sudo umount /mnt/excelusb