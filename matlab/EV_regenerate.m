%regenerate data from March 2 to now
for analysisdate=62:floor(today-datenum('31-dec-2019'))
    forhistory=1;
    EV_estimator
    EVhistfilename=['oldhistograms\EV_histogram_' num2str(analysisdate,'%i') '.jpg']
    copyfile('EV_histogram_today.jpg',EVhistfilename);
end