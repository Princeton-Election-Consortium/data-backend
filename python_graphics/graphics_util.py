
import os

import numpy as np
import pandas as pd
import datetime as dt

from plotting_util import generate_line_plot, generate_superimposed_line_plot, generate_histogram

# ======================================================================
# GLOBAL VARIABLES

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

YEAR = 2024 # Takes care of having to change file names every election cycle

# == HOUSE =============================================================

def generate_house_meta_lead_graphics():
        house_meta_lead_kw = dict(
                # Data
                data_dir = '../scraping/outputs/', 
                data_file = f'{YEAR}.house.polls.median.txt',
                read_csv_kw = dict(delimiter=r"\s+"), 
                x_column=1,             # julian_date
                y_column=3,             # median_margin
                yerr_columns=[4],       # median_std_dev
                
                # Lines
                ylim=(-14, 14),
                yticks_interval=2,
                hline_ypos = 0, 

                # Customs
                meta_lead_graphic=True,
                strike_zone_data_file = f'../matlab/outputs/House_predictions_{YEAR}.csv', 
                strike_zone_house = True,
                custom_twin_axis = True,
                custom_twin_axis_offset=0,      # Remember to also set this in banner_util.py
                custom_twin_axis_label=f'{YEAR} generic ballot D-R',
                custom_hline=True,
                custom_hline_label='Prior from special elections',
                custom_hline_ypos=4.5,          # Remember to also set this in federal_constants.m
        )

        house_meta_lead = os.path.join(out_dir, f'house_meta_lead_{YEAR}')
        generate_line_plot(
               **house_meta_lead_kw,

                # Text
                title_txt='House control meta-lead: {party}{last_value:.01f}%',
                ylab_txt='House control meta-lead',

                # Output
                out_path=house_meta_lead,
        )

        thumb_house_meta_lead = os.path.join(out_dir, f'thumb_house_meta_lead_{YEAR}')
        generate_line_plot(
                **house_meta_lead_kw, 

                # Text
                title_txt="House control meta-lead",
                corner_label = '{party}{last_value:.01f}%', 

                # Output
                thumbnail=True,
                out_path=thumb_house_meta_lead,
        )

# == SENATE ============================================================

def generate_senate_meta_lead_graphics():
        senate_meta_lead_kw = dict(
                # Data
                data_dir = '../matlab/outputs', 
                data_file=f'Senate_estimate_history_{YEAR}.csv',
                x_column=0,             # date
                y_column=11,            # meta-lead

                # Lines
                ylim=(-9, 3),
                hline_ypos = 0,

                # Customs
                meta_lead_graphic=True,
        )

        senate_meta_lead = os.path.join(out_dir, f'senate_meta_lead_{YEAR}')
        generate_line_plot(
               **senate_meta_lead_kw,

                # Text
                title_txt = 'Popular meta-lead for Senate control: {party}{last_value:.01f}%',
                ylab_txt='Meta-lead',
                hline_labels = ['R control', 'D+I control'],

                # Output
                out_path=senate_meta_lead,                
        )

        thumb_senate_meta_lead = os.path.join(out_dir, f'thumb_senate_meta_lead_{YEAR}')
        generate_line_plot(
                **senate_meta_lead_kw,

                # Text
                title_txt = 'Senate control meta-lead',
                corner_label = '{party}{last_value:.01f}%', 

                # Output
                thumbnail = True,
                out_path=thumb_senate_meta_lead,
        )

def generate_senate_dem_seats():
        senate_dem_seats_kw = dict(
                # Data
                data_dir = '../matlab/outputs', 
                data_file=f'Senate_estimate_history_{YEAR}.csv',
                x_column=0,             # date
                y_column=2,             # mean_seats
                yerr_columns= [8,9],    # ['1sigma_lower', '1sigma_upper'],

                # Lines
                hline_ypos = 49.5,
        )

        senate_dem_seats = os.path.join(out_dir, f'senate_dem_seats_{YEAR}')
        generate_line_plot(
               **senate_dem_seats_kw, 

                # Text
                title_txt='{last_value:.0f} Democratic Senate seats expected',
                ylab_txt='Democratic + Independent seats',
                hline_labels = ['R control', 'D+I control'],

                # Output
                out_path=senate_dem_seats,
        )

        thumb_senate_dem_seats = os.path.join(out_dir, f'thumb_senate_dem_seats_{YEAR}')
        generate_line_plot(
               **senate_dem_seats_kw, 

                # Text
                title_txt='Senate seats expected',
                corner_label = ["{inv_last_value:.0f} R seats", '{last_value:.0f} D+I seats'],

                # Output
                thumbnail = True,
                out_path=thumb_senate_dem_seats,
        )

def generate_senate_histogram_graphics():
        senate_histogram_kw = dict(
                # Data
                data_dir = '../matlab/outputs', 
                data_file=f'Senate_histogram_{YEAR}.csv',
                # xvals=np.arange(46, 57), # 2020- (43,61)
                # xvals=np.arange(45, 56), # TODO: I think I need to play around here
                # xvals=np.arange(42, 47),
                xvals=None,

                # Lines
                xlim=(44,54),
                xticks_interval=1,
                ylim=(0, 1.15),
                yticks_interval=5,
                vline_xpos = 50.0,
                vline_lab_pad = 0.125,

                # Text
                title_txt='Median: {median_value:.0f} D+I Senate seats',
                vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
        )

        senate_histogram = os.path.join(out_dir, f'senate_histogram_{YEAR}')
        generate_histogram(
               **senate_histogram_kw, 

                # Text
                xlab_txt = 'Democratic + Independent Senate seats',
                ylab_txt='Probability (%)',
                
                # Output
                out_path=senate_histogram,
        )

        thumb_senate_histogram = os.path.join(out_dir, f'thumb_senate_histogram_{YEAR}')
        generate_histogram(
                **senate_histogram_kw, 

                # Output
                thumbnail = True,
                out_path=thumb_senate_histogram,
        )

# == PRESIDENTIAL ======================================================

def generate_ev_meta_lead_graphics():
        ev_meta_lead_kw = dict(
                # Data 
                data_dir = '../matlab/outputs', 
                data_file=f'EV_estimate_history_{YEAR}.csv',
                x_column=0,             # date
                y_column=13,            # meta-lead

                # Lines
                ylim=(-5, 3), 
                hline_ypos = 0,

                # Text
                hline_labels = ['Trump leads','Harris leads'],
                hline_lab_xpos = 0.22,

                # Customs
                meta_lead_graphic=True,
                custom_arrowhead=True,
        )

        ev_meta_lead = os.path.join(out_dir, f'ev_meta_lead_{YEAR}')
        generate_line_plot(
               **ev_meta_lead_kw,
                
                # Text
                title_txt = 'Popular meta-lead for President: {party}{last_value:.01f}%',
                ylab_txt='Meta-lead',
                
                # Output
                out_path=ev_meta_lead,
        )

        thumb_ev_meta_lead = os.path.join(out_dir, f'thumb_ev_meta_lead_{YEAR}')
        generate_line_plot(
                **ev_meta_lead_kw,

                # Text
                title_txt = 'Presidential Meta-lead',

                # Output
                thumbnail = True,
                out_path=thumb_ev_meta_lead,
        )
       
def generate_ev_estimator_graphics():
        ev_estimator_kw = dict(
                # Data
                data_dir = '../matlab/outputs', 
                data_file=f'EV_estimate_history_{YEAR}.csv',
                x_column=0,             # date
                y_column= 1,            # 'median_EV0', # 0=biden, 1=trump
                yerr_columns= [10,11],  # ['95ci_lower', '95ci_upper']

                # Lines
                ylim=(180,340),
                yticks_interval=40,
                yticks_shift = 10,
                hline_ypos = 270,

                # Text
                hline_labels = ['Trump leads', 'Harris leads'],
                hline_lab_xpos = 0.22, 

                # Customs
                strike_zone_data_file=f'EV_prediction_{YEAR}.csv',
                custom_arrowhead=True,
        )

        ev_estimator = os.path.join(out_dir, f'ev_estimator_{YEAR}')
        generate_line_plot(
                **ev_estimator_kw, 

                # Text
                title_txt='{last_value:.0f} Harris electoral votes expected',
                ylab_txt='Harris electoral votes',

                # Output
                out_path=ev_estimator,
        )

        thumb_ev_estimator = os.path.join(out_dir, f'thumb_ev_estimator_{YEAR}')
        generate_line_plot(
                **ev_estimator_kw, 

                # Text
                title_txt='Today: Harris {last_value:.0f}, Trump {inv_pres_last_value:.0f} EV',

                # Output
                thumbnail = True,
                out_path=thumb_ev_estimator
        )

def generate_ev_histogram_graphics():
        ev_histogram_kw = dict(
                # Data
                data_dir = '../matlab/outputs', 
                data_file = f'EV_histogram_{YEAR}.csv',

                # Lines
                xlim=(150, 390),
                xticks_interval=40,
                ylim=(0, 1.2),
                yticks_interval=0.5,
                vline_xpos=269,
                vline_lab_pad = 0.105,
                xvals = np.linspace(1, 538, 538),

                # Text
                title_txt='Today\'s median: {median_value:.0f} EV for Harris',
                vline_labels = ['Trump\nwins', 'Harris\nwins'],                

                # Customs
                hard_median = True,
                hard_median_data_file = f'EV_estimates_{YEAR}.csv',
                ev_extra_pad = True,
        )

        ev_histogram = os.path.join(out_dir, f'ev_histogram_{YEAR}')
        generate_histogram(
                **ev_histogram_kw, 

                # Text
                xlab_txt = 'Electoral votes for Harris',
                ylab_txt='Prob. of exact # of EV (%)',

                # Output
                out_path=ev_histogram,
        )

        thumb_ev_histogram = os.path.join(out_dir, f'thumb_ev_histogram_{YEAR}')
        generate_histogram(
                **ev_histogram_kw, 

                # Output
                thumbnail = True,
                out_path=thumb_ev_histogram,
        )

# ======================================================================

def generate_house_graphics():
        generate_house_meta_lead_graphics()

def generate_senate_graphics():
        generate_senate_meta_lead_graphics()
        generate_senate_dem_seats()
        generate_senate_histogram_graphics()

def generate_presidential_graphics():
        generate_ev_meta_lead_graphics()
        generate_ev_estimator_graphics()
        generate_ev_histogram_graphics()

def generate_superimposed_graphic():
        all_meta_lead_kw = dict(
                # House data
                house_data_dir = '../scraping/outputs/', 
                house_data_file = f'{YEAR}.house.polls.median.txt',
                house_read_csv_kw = dict(delimiter=r"\s+"), 
                house_x_column=1,             # julian_date
                house_y_column=3,             # median_margin

                # Senate data
                senate_data_dir = '../matlab/outputs', 
                senate_data_file=f'Senate_estimate_history_{YEAR}.csv',
                senate_x_column=0,             # date
                senate_y_column=11,            # meta-lead

                # EV data
                ev_data_dir = '../matlab/outputs', 
                ev_data_file=f'EV_estimate_history_{YEAR}.csv',
                ev_x_column=0,             # date
                ev_y_column=13,            # meta-lead
                
                # Lines
                ylim=(-14, 8),
                # ylim=(-9, 3),
                # ylim=(-6, 2), 

                yticks_interval=2,

                # Customs
                meta_lead_graphic=True,
        )

        all_meta_lead = os.path.join(out_dir, f'all_meta_lead_{YEAR}')
        generate_superimposed_line_plot(
               **all_meta_lead_kw,

                # Text
                title_txt='House, Senate, and Presidential meta-lead', 
                ylab_txt='Meta-lead', 

                house_label = 'House: {party}{last_value:.01f}%',  
                senate_label = 'Senate: {party}{last_value:.01f}%',  
                ev_label = 'Presidential: {party}{last_value:.01f}%',  

                # hline_labels = ['R control', 'D+I control'], # if needed, move to right by changing HLINE_LAB_XPOS

                # Output
                out_path=all_meta_lead,
        )

# def generate_histogram_test():
#         generate_senate_histogram_graphics()
#         generate_ev_histogram_graphics()

def main():
        print("Generating House graphics...")
        generate_house_graphics()       
        print("Generating Senate graphics...")        
        generate_senate_graphics()       
        print("Generating Presidential graphics...")       
        generate_presidential_graphics()
        generate_superimposed_graphic()

if __name__ == '__main__':
    main()