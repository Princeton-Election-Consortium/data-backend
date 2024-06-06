#!/bin/bash

# source /mysql0/python/anaconda3/bin/activate
source /opt/anaconda/3.9_4.12.0/bin/activate /opt/anaconda/3.9_4.12.0/

cd /opt/cron/scripts/data-backend

# export PYTHON_PATH = /opt/cron/scripts/data-backend/python_graphics

git pull origin master

# 538 SCRAPING
python scraping/scraping_util.py

# MATLAB SCRIPTS
cd matlab
/opt/MATLAB/R2021b/bin/matlab -r "federal_runner; quit"
cd ..

# PYTHON GRAPHICS
cd python_graphics          # need to run in this directory
python graphics_util.py 
cd ..

# BANNER CODE
python banner/banner_util.py

# SIDEBAR CODE
python sidebar/sidebar_util.py

# OUTPUTS
cp /opt/cron/scripts/data-backend/scraping/outputs/*.txt /opt/cron/output
cp /opt/cron/scripts/data-backend/scraping/outputs/*.csv /opt/cron/output

cp /opt/cron/scripts/data-backend/matlab/outputs/*.csv /opt/cron/output
cp /opt/cron/scripts/data-backend/matlab/outputs/270towin_URL.txt /opt/cron/output

cp /opt/cron/scripts/data-backend/python_graphics/outputs/*.png /opt/cron/output
cp /opt/cron/scripts/data-backend/banner/*.html /opt/cron/output
cp /opt/cron/scripts/data-backend/sidebar/*.html /opt/cron/output

# cp /opt/cron/data-backend/moneyball/* /opt/cron/www/data/moneyball/

# BACKUPS
archive_dir=$(date +%Y-%m-%d_%H-%M-%S)
echo $archive_dir
mkdir /opt/cron/output/archive/$archive_dir
cp /opt/cron/output/* /opt/cron/output/archive/$archive_dir

cd /opt/cron/scripts/data-backend
git add .
git commit -m "today's output"
git push


