#!/bin/bash

source /mysql0/python/anaconda3/bin/activate

cd /opt/cron/scripts/data-backend

git pull origin master

python scraping/pec2022.py

cp /opt/cron/data-backend/scraping/outputs/*.txt /opt/cron/data-backend/matlab
cd matlab
matlab -r "federal_runner; quit"
cd ..

cd python_graphics
python main_2022.py

cd /opt/cron/data-backend/banner
python banner_2022.py
cd ..

cd /opt/cron/data-backend/sidebar
# python banner/banner_orig.py
# python sidebar/Presidential_Race_Table.py
python Senate_JV_Widget_2022.py
# python sidebar/Senate_JV_Widget_old.py

cp /opt/cron/data-backend/matlab/*.txt /opt/cron/outputs
cp /opt/cron/data-backend/scraping/outputs/*.csv /opt/cron/outputs
cp /opt/cron/data-backend/matlab/outputs/*.csv /opt/cron/outputs
cp /opt/cron/data-backend/matlab/outputs/270towin_URL.txt /opt/cron/outputs

cp /opt/cron/data-backend/python_graphics/outputs/*.png /opt/cron/outputs
cp /opt/cron/data-backend/banner/*.html /opt/cron/outputs
cp /opt/cron/data-backend/sidebar/*.html /opt/cron/outputs

# cp /opt/cron/data-backend/moneyball/* /opt/cron/www/data/moneyball/

# backups
archive_dir=$(date +%Y-%m-%d_%H-%M-%S)
mkdir /opt/cron/outputs/archive/$archive_dir
cp /opt/cron/outputs/* /opt/cron/outputs/archive/$archive_dir

cd ..
git add .
git commit -m "today's output"
git push


