This folder contains script to cut a video segment into tiles, split the tiles into images, zip the images, then put the zip and the images into 
     the ./tiles/JPEGImages folder 
To generate all possible Tiles for a given 3840x2080 video, execute create_tile_data.ipynb
If necessary, execute the create_all_tile_vid.sh file, generated from the ipynb file above, to generate tile videos. Tile video will be organized into directory tree inside tile_vids directory.

Next, it is necessary to create train.json inside ./tiles folder. To generate this file, go into the tiles folder and follow the instruction

Description of bashscript files in this datasets directory:
create_tile.sh : create tiles at various resolutions and framerates
create_all_tile.sh : a dynamic bash script generated from the create_tile_data.ipynb. Createa all tiles for a given segment
create_all_tile_vid.sh: dynamic bash script generated from create_tile_data.ipynb. Create all tiles for all segments of a videos
