#!/bin/sh

cp /usr/share/zoneinfo/$TZ /etc/localtime

mkdir -p /data/$CAMERA_NAME

while ! nc -z $CAMERA_IP 554; do   
  sleep 0.5
done

exec ffmpeg -xerror -stimeout 2000000 -use_wallclock_as_timestamps 1 -rtsp_transport tcp -i rtsp://$CAMERA_USER:$CAMERA_PW@$CAMERA_IP:554 -an -vcodec copy -map_metadata -1 -f segment -segment_time 600 -segment_format mp4 -strftime 1 -reset_timestamps 1 "/data/$CAMERA_NAME/%Y-%m-%d-%H-%M-%S.mp4"
