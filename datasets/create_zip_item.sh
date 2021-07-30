#TODO: extract a target video into frames, and zip into one file, put into target folder
#example ./create_zip_item.sh  ./tile_vids/1680_938/192x192.mp4 ./tiles/JPEGImages/paris.zip

curdir=$(pwd)
inputpath=$(realpath $1)
outputpath=$(realpath $2)
outputdir=$(dirname $outputpath)
echo "CUTTING VID $inputvid into tiles of different resoluion and bitrate"

mkdir ./tmp
ffmpeg -i $inputpath  ./tmp/%05d.jpg

cd ./tmp
echo "zip -q -r $outputpath *.jpg"
zip -q -r $outputpath *.jpg

cd $curdir

