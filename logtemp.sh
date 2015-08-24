#/bin/sh
FILENAME=$(date +"%H.%M")
LOGDIR='/home/pi/usbdrv/templog'
SOURCE='/sys/bus/w1/devices/28-000007099503/w1_slave'
TEMPSTRING=$(cat $SOURCE)
mv $LOGDIR/$FILENAME $LOGDIR/yesterday/$FILENAME
echo ${TEMPSTRING##*=} > $LOGDIR/$FILENAME
chmod a+w $LOGDIR/$FILENAME
