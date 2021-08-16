for file in ./*.mp4; do
    dirname=${file//.mp4/}
    zipname=${dirname}.zip
    mkdir $dirname
    ffmpeg -i $file $dirname/%05d.jpg
    cd $dirname
    zip -q -r ../${dirname}.zip *.jpg
    cd ..
    done;
