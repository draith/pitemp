#!/bin/sh
FILENAME=$(date +"%H.%M")
LOGDIR='/home/pi/usbdrv/templog'
SOURCE='/sys/bus/w1/devices/28-000007099503/w1_slave'
TEMPSTRING=$(cat $SOURCE)
BACKLOGFILE='/home/pi/pitemp/backlog.txt'
NEWBACKLOG='/var/ram/backlog.txt'
BACKLOGLOGFILE='/home/pi/pitemp/backlog.log'
TEMPVAL=${TEMPSTRING##*=}

# Save reading in local file.
mv $LOGDIR/$FILENAME $LOGDIR/yesterday/$FILENAME
echo $TEMPVAL > $LOGDIR/$FILENAME
chmod a+w $LOGDIR/$FILENAME

# Send reading to web database
# REQUIRED ENVIRONMENT VARIABLES URL1 and URL2 to compile URL for uploading.
# e.g. full URL = "http://www.myurl.com/upload.php?time=$TIMESTAMP\&temp=$TEMPVAL"
TIMESTAMP=$(date -u "+%Y-%m-%d%%20%H:%M:00")
RESPONSE=$(curl http://www.mekeke.co.uk/pitemp/logtemp.php?id=mypicam\&timestamp=$TIMESTAMP\&reading=$TEMPVAL)

if [ "$RESPONSE" != "OK" ]
then
  # FAILED: Append date and reading to backlog file
  mail -s "temp log failed" draith2001@gmail.com
  echo "$TIMESTAMP $TEMPVAL" >> $BACKLOGFILE
else
  # Success. Now upload any backlog.
  while read line; do
    words=($line)
    TIMESTAMP=${words[0]}
    TEMPVAL=${words[1]}
    if [ "$RESPONSE" != "OK" ]
    then
      echo "$TIMESTAMP $TEMPVAL" >> $NEWBACKLOG
    else
      echo "Uploading backlog" $TIMESTAMP $TEMPVAL >> $BACKLOGLOGFILE
      RESPONSE=$(curl http://www.mekeke.co.uk/pitemp/logtemp.php?id=mypicam\&timestamp=$TIMESTAMP\&reading=$TEMPVAL)
      if [ "$RESPONSE" != "OK" ]
      then
        echo "RESPONSE =" $RESPONSE >> $BACKLOGLOGFILE
        echo "$TIMESTAMP $TEMPVAL" >> $NEWBACKLOG
      else
        echo "OK: " $TIMESTAMP $TEMPVAL >> $BACKLOGLOGFILE
      fi
    fi
  done < $BACKLOGFILE
  
  if [ "$RESPONSE" != "OK" ]
  then
    mv $NEWBACKLOG $BACKLOGFILE
  else
    echo -n "" > $BACKLOGFILE
  fi
fi
