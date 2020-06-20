#!/bin/bash

source /mysql0/python/anaconda3/bin/activate

cd /web/data-backend

git pull origin master

python scraping/pec2020.py
python banner/banner.py

cp /web/data-backend/scraping/outputs/*.txt /web/data-backend/matlab
cd matlab
matlab -r "federal_runner; quit"
cd ..

cd python_graphics
python main.py

cp /web/data-backend/matlab/*.txt /web/www/election2020/data
cp /web/data-backend/scraping/outputs/*.csv /web/www/election2020/data
cp /web/data-backend/matlab/outputs/*.csv /web/www/election2020/data
cp /web/data-backend/matlab/outputs/270towin_URL.txt /web/www/election2020/data

cp /web/data-backend/python_graphics/outputs/*.png /web/www/election2020/outputs
cp /web/data-backend/banner/banner.html /web/www/election2020/outputs

# backups
archive_dir=$(date +%Y%m%d_%H%M%S)
mkdir /web/www/election2020/outputs/archive/$archive_dir
cp /web/www/election2020/outputs/* /web/www/election2020/outputs/archive/$archive_dir
