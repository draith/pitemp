#!/bin/sh
SOURCE='/sys/bus/w1/devices/28-000007099503/w1_slave'
TEMPSTRING=$(cat $SOURCE)
TEMPVAL=${TEMPSTRING##*=}
TIMESTAMP=$(date -u "+%Y-%m-%d%%20%H:%M:00")

LOGDIR='/home/pi/usbdrv/templog'
BACKLOGFILE='/home/pi/pitemp/backlog.txt'
NEWBACKLOG='/var/ram/backlog.txt'

# Save reading in local file.
FILENAME=$(date +"%H.%M")
mv $LOGDIR/$FILENAME $LOGDIR/yesterday/$FILENAME
echo $TEMPVAL > $LOGDIR/$FILENAME
chmod a+w $LOGDIR/$FILENAME

# Send reading to web database
# REQUIRED ENVIRONMENT VARIABLES URL1 and URL2 to compile URL for uploading.
# e.g. full URL = "http://www.myurl.com/upload.php?time=$TIMESTAMP\&temp=$TEMPVAL"

RESPONSE=$(curl $URL1$TIMESTAMP$URL2$TEMPVAL)
# echo "Sent:" $URL1$TIMESTAMP$URL2$TEMPVAL
# echo "Response:" $RESPONSE

if [ "$RESPONSE" != "OK" ]
then
  # FAILED: Append date and reading to backlog file
  mail -s "temp log failed" draith2001@gmail.com
  echo "$TIMESTAMP $TEMPVAL" >> $BACKLOGFILE
  echo "Upload failed:" $RESPONSE
else
  # Success. Now upload any backlog.
  while read line; do
    TIMESTAMP=${line%% *}
    TEMPVAL=${line##* }
    if [ "$RESPONSE" != "OK" ]
    then
      echo "$TIMESTAMP $TEMPVAL" >> $NEWBACKLOG
    else
      echo "Uploading backlog" $TIMESTAMP $TEMPVAL
       RESPONSE=$(curl $URL1$TIMESTAMP$URL2$TEMPVAL)
      if [ "$RESPONSE" != "OK" ]
      then
        echo "RESPONSE =" $RESPONSE
        echo "$TIMESTAMP $TEMPVAL" >> $NEWBACKLOG
      else
        echo "OK: " $TIMESTAMP $TEMPVAL
      fi
    fi
  done < $BACKLOGFILE
  
  if [ "$RESPONSE" != "OK" ]
  then
    echo "Updating" $BACKLOGFILE
    mv $NEWBACKLOG $BACKLOGFILE
  else
    echo -n > $BACKLOGFILE
  fi
fi
