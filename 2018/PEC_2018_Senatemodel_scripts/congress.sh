#!/bin/bash

# Collect and process polls for the Senate and House
# Expects to be run from /web/XXXX/ as `sh bin/congress.sh`

DIR=`pwd -P`
export PYTHONDIR=$DIR/python
export MATLABDIR=$DIR
export BINDIR=$DIR
export OUTDIR=$DIR
export DATADIR=$DIR
# export PYTHONPATH=$PYTHONDIR:$PYTHONPATH

### House stuff
export HOUSE_FILE=house_race_polls.csv
export HOUSE_MATLAB_FILE=house_race_matlab.csv # specified in House_timeseries.m
export POLLSTERS_FILE=pollsters.p
export HOUSE_HISTORY_FILE=House_median_history.csv
export HOUSE_HISTORY_GRAPH=House_generic_history.jpg
export HOUSE_URL=http://elections.huffingtonpost.com/pollster/2016-national-house-race.csv

# cd $DATADIR

# wget $HOUSE_URL -O $HOUSE_FILE
# python $PYTHONDIR/convert_huffpost_csv.py $HOUSE_FILE $HOUSE_MATLAB_FILE $POLLSTERS_FILE
# cd $MATLABDIR
# sh $BINDIR/Xrun.sh "matlab -r House_runner"

# mv -f $HOUSE_HISTORY_FILE $DATADIR
# mv -f $HOUSE_HISTORY_GRAPH $OUTDIR

### Senate stuff
# TODO most of these should probably just be in a list of filenames
# unless Sam's MATLAB scripts start taking filenames as parameters
export SEN_POLLS_FILE=2018.Senate.polls.median.txt # from senate_update_polls.py
export SEN_HISTORY_FILE=Senate_estimate_history.csv
export SEN_HISTOGRAM_FILE=Senate_histogram.csv
export SEN_HISTOGRAM=Senate_histogram_today.jpg
export SEN_STATEPROBS=Senate_stateprobs.csv
export SEN_ESTIMATES=Senate_estimates.csv
export SEN_JERSEYVOTES_FILE=Senate_jerseyvotes.csv
export SEN_NOV_PROB_FILE=Senate_D_November_control_probability.csv
export SEN_MM_HIST=Senate_metamargin_history.jpg
export SEN_SEAT_HIST=Senate_seat_history.jpg

#cd $DATADIR

# Lucas, this is the section that updates polls. I think replace 
# with your code for scraping RCP and electoral-vote.com
# python $PYTHONDIR/senate_update_polls.py
python3 ../datascrape.py --senate
# mv ../$SEN_POLLS_FILE .


# If this has already run today, trim off the last line
# if cat $SEN_HISTORY_FILE | grep -e ^`date +%j`
# then
# mv $SEN_HISTORY_FILE EH.tmp
# head -n -1 EH.tmp > $SEN_HISTORY_FILE
# rm -f EH.tmp
# fi
# end old section that Lucas should replace

# Lucas, I think everything from here on down can stay the same
#mv -f $SEN_HISTORY_FILE $SEN_POLLS_FILE $MATLABDIR
cd $DIR

sh Xrun.sh "matlab -r Senate_runner"
cp *.csv ..  

# move output back to $DATADIR and $OUTDIR
# mv -f $SEN_HISTOGRAM_FILE $SEN_STATEPROBS $SEN_ESTIMATES $SEN_JERSEYVOTES_FILE $SEN_NOV_PROB_FILE $DATADIR
# mv -f $SEN_HISTOGRAM $SEN_MM_HIST $SEN_SEAT_HIST $OUTDIR

# postprocess
# cd $DATADIR
# python $PYTHONDIR/senate_jerseyvotes.py
# python $PYTHONDIR/senate_stateprobs.py
# mv -f *.html $OUTDIR # TODO get filenames
reset
