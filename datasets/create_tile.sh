#input $1 is video name, $2, $3 is tile size, $4, $5 is pos_h and pos_w 
#example ./create_tile.sh ../../paris_d1.mp4 192 192 240 452
dirname=$4:$5 #folder with position of the tile
dirname4=${dirname}:fps4
dirname2=${dirname}:fps2
dirname1=${dirname}:fps1
w0=$2
h0=$3
w1=$((w0/2))   #name of the file using the silze of the tile
h1=$((h0/2))
w2=$((w0/4))
h2=$((h0/4))
w3=$((w0/8))
h3=$((h0/8))


mkdir $dirname || true
#create 192x192 vid
yes | ffmpeg -i $1 -filter:v "crop=$2:$3:$4:$5"  ./$dirname/${w0}x${h0}.mp4 || true
yes | ffmpeg -i ./$dirname/${w0}x${h0}.mp4 -filter:v scale=${w1}:-1 -c:a copy ./$dirname/${w1}x${h1}.mp4 || true
yes | ffmpeg -i ./$dirname/${w0}x${h0}.mp4 -filter:v scale=${w2}:-1 -c:a copy ./$dirname/${w2}x${h2}.mp4 || true
yes | ffmpeg -i ./$dirname/${w0}x${h0}.mp4 -filter:v scale=${w3}:-1 -c:a copy ./$dirname/${w3}x${h3}.mp4 || true

stat -c %s ./$dirname/*.mp4 > tmp.txt
sort -n -r tmp.txt >  sizestats_vid.txt

echo PROCESSING FPS=4
mkdir $dirname4 || true
yes | ffmpeg -i $1 -filter:v "crop=$2:$3:$4:$5, fps=4"  ./$dirname4/${w0}x${h0}.mp4 || true
yes | ffmpeg -i ./$dirname4/${w0}x${h0}.mp4  -filter:v scale=${w1}:-1  -c:a copy ./$dirname4/${w1}x${h1}.mp4 || true
yes | ffmpeg -i ./$dirname4/${w0}x${h0}.mp4  -filter:v scale=${w2}:-1  -c:a copy ./$dirname4/${w2}x${h2}.mp4 || true
yes | ffmpeg -i ./$dirname4/${w0}x${h0}.mp4  -filter:v scale=${w3}:-1  -c:a copy ./$dirname4/${w3}x${h3}.mp4 || true

stat -c %s ./$dirname4/*.mp4 > tmp.txt
sort -n -r tmp.txt >  sizestats_vidfps4.txt

echo PROCESSING FPS=2
mkdir $dirname2 || true
yes | ffmpeg -i $1 -filter:v "crop=$2:$3:$4:$5, fps=2"  ./$dirname2/${w0}x${h0}.mp4 || true
yes | ffmpeg -i ./$dirname2/${w0}x${h0}.mp4  -filter:v scale=${w1}:-1  -c:a copy ./$dirname2/${w1}x${h1}.mp4 || true
yes | ffmpeg -i ./$dirname2/${w0}x${h0}.mp4  -filter:v scale=${w2}:-1  -c:a copy ./$dirname2/${w2}x${h2}.mp4 || true
yes | ffmpeg -i ./$dirname2/${w0}x${h0}.mp4  -filter:v scale=${w3}:-1  -c:a copy ./$dirname2/${w3}x${h3}.mp4 || true

stat -c %s ./$dirname2/*.mp4 > tmp.txt
sort -n -r tmp.txt >  sizestats_vidfps2.txt


echo PROCESSING FPS=1
mkdir $dirname1 || true
yes | ffmpeg -i $1 -filter:v "crop=$2:$3:$4:$5, fps=1"  ./$dirname1/${w0}x${h0}.mp4 || true
yes | ffmpeg -i ./$dirname1/${w0}x${h0}.mp4  -filter:v scale=${w1}:-1  -c:a copy ./$dirname1/${w1}x${h1}.mp4 || true
yes | ffmpeg -i ./$dirname1/${w0}x${h0}.mp4  -filter:v scale=${w2}:-1  -c:a copy ./$dirname1/${w2}x${h2}.mp4 || true
yes | ffmpeg -i ./$dirname1/${w0}x${h0}.mp4  -filter:v scale=${w3}:-1  -c:a copy ./$dirname1/${w3}x${h3}.mp4 || true

stat -c %s ./$dirname1/*.mp4 > tmp.txt
sort -n -r tmp.txt >  sizestats_vidfps1.txt

#create screenshots
yes | ffmpeg -ss 00:00:00 -i ./$dirname/${w0}x${h0}.mp4 -vframes 1 -q:v 2 ./$dirname/${w0}x${h0}.jpg || true
yes | ffmpeg -ss 00:00:00 -i ./$dirname/${w1}x${h1}.mp4 -vframes 1 -q:v 2 ./$dirname/${w1}x${h1}.jpg || true
yes | ffmpeg -ss 00:00:00 -i ./$dirname/${w2}x${h2}.mp4 -vframes 1 -q:v 2 ./$dirname/${w2}x${h2}.jpg || true
yes | ffmpeg -ss 00:00:00 -i ./$dirname/${w3}x${h3}.mp4 -vframes 1 -q:v 2 ./$dirname/${w3}x${h3}.jpg || true


stat -c %s ./$dirname/*.jpg > tmp.txt
sort -n -r tmp.txt  >  sizestats_frame.txt

cat sizestats_vid.txt
cat sizestats_vidfps4.txt
cat sizestats_vidfps2.txt
cat sizestats_vidfps1.txt
cat sizestats_frame.txt
