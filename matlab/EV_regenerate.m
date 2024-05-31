% Run the constants file
run('federal_constants_2024.m')

% Regenerate data for this election year
for analysisdate=EV_START_DATE:TODAYTE
    forhistory=1;
    EV_estimator
    EVhistfilename=['outputs/oldhistograms/EV_histogram_' num2str(analysisdate,'%i') '.jpg']
    copyfile(EV_HISTOGRAM_TODAY_JPG,EVhistfilename);
end