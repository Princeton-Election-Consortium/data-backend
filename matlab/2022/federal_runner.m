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
% forhistory=1; EV_estimator
% EV_jerseyvotes
% EV_prediction
% EV_history_plot       % This plot is also produced by ev_history_plot.py
%                       % Comment out if running without a display, or else jbfill
                        % will crash MATLAB.
                        % Uncomment it to produce the EV history plot in a
                        % graphical environment.

clear
forhistory=1; Senate_estimator_2022
% plot_Senate_seats_mm_history % Again, calls jbfill and won't run in a nongraphical environment
Senate_jerseyvotes_2022
Senate_November_prediction_2022
House_prediction

quit                    % closes MATLAB when done
