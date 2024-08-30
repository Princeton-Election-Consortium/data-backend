%%%  federal_runner.m - a MATLAB script
%%%  Author: Stephanie Yen <sy7@alumni.princeton.edu> 
%%%  Script written for election.princeton.edu run by Samuel S.-H. Wang under
%%%  non-commercial-use-only license:
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact sswang@princeton.edu.

% This script simply calls the other MATLAB scripts in appropriate order
% so they can be run in the same MATLAB environment.
% It references a constants file for the appropriate election year.

clear
close
% federal_constants_2024
% 
% forhistory=1; 
% EV_estimator
% EV_jerseyvotes
% EV_prediction

clear
federal_constants_2024

forhistory=1;
Senate_estimator
Senate_jerseyvotes
Senate_prediction

clear
federal_constants_2024

House_prediction

% quit                    % closes MATLAB when done
