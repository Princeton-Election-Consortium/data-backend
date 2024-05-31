% Run the constants file
run('federal_constants_2024.m')

% Regenerate data for this election year
for analysisdate=SENATE_START_DATE:TODAYTE
    forhistory=1;
    Senate_estimator
    Senatehistfilename=['outputs/oldhistograms/Senate_histogram_' num2str(analysisdate,'%i') '.jpg']
    copyfile(SENATE_HISTOGRAM_TODAY_JPG,Senatehistfilename);
end