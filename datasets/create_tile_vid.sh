#input $1 is video name, $2, $3 is tile size, $4, $5 is pos_h and pos_w 
#example ./create_tile_dat.sh ./segment_vids/paris_8_1.mp4 192 192 1680 938

inputvid=$(realpath $1)
vidname=$(basename $inputvid)
vidID=${vidname//.mp4/}
echo "CUTTING VID $inputvid into tiles of different resoluion and bitrate"

cd ./tile_vids
mkdir $vidID
dirname=${vidID}/$4_$5 #folder with position of the tile


w0=$2
h0=$3

mkdir $dirname || true

#create 192x192 tile video
echo "yes | ffmpeg -loglevel panic  -i \"$inputvid\" -filter:v \"crop=$2:$3:$4:$5\"  ./$dirname/${w0}x${h0}.mp4 || true"
yes | ffmpeg -loglevel panic -i "$inputvid" -filter:v "crop=$2:$3:$4:$5"  ./$dirname/${w0}x${h0}.mp4 || true
tilevid_path=$(realpath ./$dirname/${w0}x${h0}.mp4)
cd ..
