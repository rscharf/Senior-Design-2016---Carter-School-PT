#!/bin/sh

file="/mnt/excelusb/SensoryWalk.xlsx"

sleep 3

#first mount the usb drive to the designated mount point
sudo mount -U "5BCF-16E1" /mnt/excelusb -o uid=pi,gid=pi

#remove any existing excel spreadsheet
if [ -f $file ] ; then
    rm $file
fi

#then copy over the excel spreadsheet to the mount point
cp SensoryWalk.xlsx /mnt/excelusb

#then unmount the usb drive
sudo umount /mnt/excelusb