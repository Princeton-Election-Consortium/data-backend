#!/bin/bash

if [ $1 = "local" ]; then
    python3 scraping/pec2020.py
    cp scraping/outputs/*.txt matlab
    matlab -r matlab/federal_runner
    matlab -r matlab/senate_estimator
    python3 python_graphics/main.py
else
    python3 /web/data-backend/scraping/pec2020.py
    cp /web/data-backend/scraping/outputs/*.txt /web/data-backend/matlab
    /web/data-backend/matlab/Xrun.sh
    reset
    python3 /web/data-backend/python_graphics/main.py
fi