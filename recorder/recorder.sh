#!/bin/sh

mkdir -p /data/$CAMERA_NAME

exec ffmpeg -rtsp_transport tcp -i rtsp://$CAMERA_USER:$CAMERA_PW@$CAMERA_IP:554 -an -vcodec copy -map_metadata -1 -f segment -segment_time 60 -segment_format mp4 -strftime 1 -reset_timestamps 1 "/data/$CAMERA_NAME/%Y-%m-%d_%H-%M-%S.mp4"
