#TODO: cut video into segment, input parameters: vid_path, start_time, segment_length, vid_out_path
#example ./create_segment ./paris.mp4 00:00:10 00:00:01
ffmpeg -i $1 -filter:v scale=3840:-1 -c:a copy -ss $2 -t $3 -async 1 $4