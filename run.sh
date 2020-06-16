#!/bin/bash

source /tmp/update/python/anaconda3/bin/activate

cd /web/data-backend

#python scraping/pec2020.py
#python banner/banner.py

cp /web/data-backend/scraping/outputs/*.txt /web/data-backend/matlab
cd matlab
matlab -r "federal_runner; quit"
matlab -r "Senate_estimator; quit"
cd ..

cd python_graphics
python main.py

cp /web/data-backend/matlab/*.txt /web/www/data/election2020
cp /web/data-backend/python_graphics/outputs/*.png /web/www/data/election2020
cp /web/data-backend/banner/banner.html /web/www/data/election2020
