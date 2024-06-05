%%%  EV_runner.m - a MATLAB script
%%%  Author: Andrew Ferguson <adferguson@alumni.princeton.edu> 
%%%  Script written for election.princeton.edu run by Samuel S.-H. Wang under
%%%  non-commercial-use-only license:
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact sswang@princeton.edu.

% This script simply calls the other MATLAB scripts in appropriate order
% so they can be run in the same MATLAB environment as loaded via the Unix
% script nightly.sh

close
federal_constants_2024

forhistory=1; 
EV_estimator
EV_jerseyvotes
EV_prediction
% EV_history_plot       % This plot is also produced by ev_history_plot.py
%                       % It is commented out because the jbfill routine
                        % crashes MATLAB when running without a display.
                        % Uncomment it to produce the EV history plot in a
                        % graphical environment.

clear
federal_constants_2024

forhistory=1;
Senate_estimator
% plot_Senate_seats_mm_history % Again, calls jbfill and won't run in a nongraphical environment
Senate_jerseyvotes
Senate_November_prediction

clear
federal_constants_2024

House_prediction

clear
quit                    % closes MATLAB when done
