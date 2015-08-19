#!/bin/sh
FILENAME=$(date +"%H:%M")
cp '/sys/bus/w1/devices/28-000007099503/w1_slave' /var/ram/templog/$FILENAME
chmod a+w /var/ram/templog/$FILENAME
