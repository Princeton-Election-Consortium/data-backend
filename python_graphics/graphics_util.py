
import os

import numpy as np
import pandas as pd

from plotting_util import generate_line_plot, generate_histogram

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

YEAR = 2024

# == HOUSE =============================================================

def generate_house_meta_lead_graphics():
        house_meta_lead_kw = dict(
                # Data parameters
                data_dir = '../scraping/outputs/', # '../matlab'
                data_file = '2024.house.polls.median.txt',
                read_csv_kw = dict(delimiter=r"\s+"),
                strike_zone_data_file = '../matlab/outputs/House_predictions_2024.csv', 
                strike_zone_house = True,
                
                # Column / line parameters
                x_column=1, # julian_date
                y_column=3, # median_margin
                yerr_columns=[4], # esd
                hline_ypos = 0, # SET PARAMETER

                # Axes / tick parameters
                ylim=(-14, 14),
                yticks_interval=2,
                ax_offset=0, # Chosen by Sam in 2024

                # Custom parameters
                meta_lead_graphic=True,
                custom_twin_axis = True,
                custom_h_line=True,
        )

        house_meta_margin = os.path.join(out_dir, f'house_meta_margin_{YEAR}')
        generate_line_plot(
               **house_meta_lead_kw,

                # Text parameters
                title_txt='House control meta-margin: {party}{last_value:.01f}%',
                ylab_txt='House control meta-margin',

                # Output parameters
                out_path=house_meta_margin,
        )

        thumb_house_meta_margin = os.path.join(out_dir, f'thumb_house_meta_margin_{YEAR}')
        generate_line_plot(
                **house_meta_lead_kw, 

                # Text parameters
                title_txt="House control meta-margin",
                hline_label = '{party}{last_value:.01f}%', 

                # Output parameters
                thumbnail=True,
                out_path=thumb_house_meta_margin,
        )

# == SENATE ============================================================

def generate_senate_meta_lead_graphics():
        senate_meta_lead_kw = dict(
                # Data parameters
                data_dir = '../matlab/outputs', 
                data_file='Senate_estimate_history_2024.csv',

                # Column / line parameters
                x_column=0, # Date
                y_column=11, # meta-margin
                hline_ypos = 0,

                # Axes / tick parameters
                ylim=(-9, 3),

                # Custom parameters
                meta_lead_graphic=True,
        )

        senate_meta_lead = os.path.join(out_dir, f'senate_meta_lead_{YEAR}')
        generate_line_plot(
               **senate_meta_lead_kw,

                # Text parameters
                title_txt = 'Popular meta-lead for Senate control: {party}{last_value:.01f}%',
                ylab_txt='Meta-margin',
                hline_labels = ['R control', 'D+I control'],

                # Output parameters
                out_path=senate_meta_lead,                
        )

        thumb_senate_meta_lead = os.path.join(out_dir, f'thumb_senate_meta_lead_{YEAR}')
        generate_line_plot(
                **senate_meta_lead_kw,

                # Text parameters
                title_txt = 'Senate control meta-margin',
                hline_label = '{party}{last_value:.01f}%', 

                # Output parameters
                thumbnail = True,
                out_path=thumb_senate_meta_lead,
        )

def generate_senate_dem_seats():
        senate_dem_seats_kw = dict(
                # Data parameters
                data_dir = '../matlab/outputs', 
                data_file='Senate_estimate_history_2024.csv',

                # Column / line parameters
                x_column=0, # Date
                y_column=2, # mean_seats
                yerr_columns= [8,9], #['1sigma_lower', '1sigma_upper'],
                hline_ypos = 49.5,
        )

        senate_dem_seats = os.path.join(out_dir, f'senate_dem_seats_{YEAR}')
        generate_line_plot(
               **senate_dem_seats_kw, 

                # Text parameters
                title_txt='{last_value:.0f} Democratic Senate seats expected',
                ylab_txt='Dem/Ind seats',
                hline_labels = ['R control', 'D+I control'],

                # Output parameters
                out_path=senate_dem_seats,
        )

        # generate thumbnail version
        # NOT GENERATING THE H_LABELS...
        thumb_senate_dem_seats = os.path.join(out_dir, f'thumb_senate_dem_seats_{YEAR}')
        generate_line_plot(
               **senate_dem_seats_kw, 

                # Text parameters
                title_txt='Senate seats expected',
                hline_labels = ["{inv_last_value:.0f} R seats", '{last_value:.0f} D+I seats'],

                # Output parameters
                thumbnail = True,
                out_path=thumb_senate_dem_seats,
        )

# histogram graphics in Matlab?
def generate_senate_histogram_graphics():
        # senate_histogram_kw = dict(
        #         # Data parameters
        #         # data_dir = '../scraping/outputs', # '../matlab'
        #         data_file='Senate_estimate_history_2024.csv',

        #         # Column parameters
        #         x_column=0, # Date
        #         y_column=11, # meta-margin

        #         hline_ypos = 0,
        #         hline_labels = ['R control', 'D+I control'],
        # )

        path = os.path.join(out_dir, 'senate_histogram_2024')
        generate_histogram(
                # Data parameters
                data_dir = '../matlab/outputs', 
                data_file='Senate_histogram_2024.csv',
                # data_file = 'Senate_histogram_2024_dummy.csv',
                # xvals=np.arange(46, 58), # 2020- (43,61)
                xvals=None,
                ylim=(0, 1.15),
                # xlim=(47, 58),
                xlim=(1,10),
                xticks_interval=1,
                yticks_interval=5,
                ylab_txt='Probability (%)',
                ylab_rotation=90,
                ylab_pad=0.044,
                xlab_txt = 'Democratic + Independent Senate seats',
                title_txt='Median: {median_value:.0f} D+I Senate seats',
                vline_xpos = 49.6,
                vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
                out_path=path
        )

        # ## generate thumbnail version
        # path = os.path.join(out_dir, 'thumb_senate_histogram_2022')
        # generate_histogram(
        #         data_file = 'Senate_histogram_2022.csv',
        #         xvals=np.arange(46, 58),
        #         ylim=(0, 1.15),
        #         xlim=(46, 56.5),
        #         xticks_interval=1,
        #         yticks_interval=5,
        #         ylab_rotation=90,
        #         ylab_pad=0.00,
        #         title_txt='Median: {median_value:.0f} D+I Senate seats',
        #         vline_xpos = 49.6,
        #         vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
        #         vline_lab_pad = 0.125,
        #         vline_lab_ypos = 0.85,
        #         thumbnail = True,
        #         out_path=path)

# == PRESIDENTIAL ======================================================

def generate_ev_meta_lead_graphics():
        ev_meta_lead_kw = dict(
                # Data parameters
                data_dir = '../matlab/outputs', 
                data_file='EV_estimate_history_2024.csv',

                # Column / line parameters
                x_column=0, # date
                y_column=13, # meta-margin
                hline_ypos = 0,
                hline_labels = ['Trump leads','Biden leads'],

                # Axes / tick parameters
                ylim=(-6, 2), ## AUTOMATE?

                # Custom parameters
                meta_lead_graphic=True,
        )

        ev_meta_lead = os.path.join(out_dir, f'ev_meta_lead_{YEAR}')
        generate_line_plot(
               **ev_meta_lead_kw,
                
                # Text parameters
                title_txt = 'Popular meta-lead for President: {party}{last_value:.01f}%',
                ylab_txt='Meta-margin',
        
                # Output parameters
                out_path=ev_meta_lead,
        )

        ## generate thumbnail version
        thumb_ev_meta_lead = os.path.join(out_dir, f'thumb_ev_meta_lead_{YEAR}')
        generate_line_plot(
                **ev_meta_lead_kw,

                # Text parameters
                title_txt = 'Presidential Meta-margin',
                # hline_lab_xpos = 0.75,
                # hline_lab_pad = 0.1,

                # Output parameters
                thumbnail = True,
                out_path=thumb_ev_meta_lead,
        )
       
def generate_ev_estimator_graphics():
        ev_estimator_kw = dict(
                # Data parameters
                data_dir = '../matlab/outputs', 
                data_file = 'EV_estimate_history_2024.csv',
                strike_zone_data_file = 'EV_prediction_2024.csv',

                # Column / line parameters
                x_column=0, # date
                y_column= 1, #'median_EV0', # 0=biden, 1=trump
                # x_minus_yvalues= None, # to make in terms of trump
                yerr_columns= [10,11], # ['95ci_lower', '95ci_upper'],
                hline_ypos = 270,
                hline_labels = ['Trump leads', 'Biden leads'],

                # Axes / tick parameters
                ylim=(150,300),
                yticks_interval=40,
        )

        ev_estimator = os.path.join(out_dir, f'ev_estimator_{YEAR}')
        generate_line_plot(
                **ev_estimator_kw, 

                # Text parameters
                title_txt='{last_value:.0f} Biden electoral votes expected',
                ylab_txt='Biden electoral votes',

                # Output parameters
                out_path=ev_estimator,
        )

        thumb_ev_estimator = os.path.join(out_dir, f'thumb_ev_estimator_{YEAR}')
        generate_line_plot(
                **ev_estimator_kw, 

                # Text parameters
                title_txt='Today: Biden {last_value:.0f}, Trump {inv_pres_last_value:.0f} EV',

                # Output parameters
                thumbnail = True,
                out_path=thumb_ev_estimator
        )

# def generate_ev_histogram_graphics():
        # path = os.path.join(out_dir, 'ev_histogram_2024')
        # generate_histogram(
        #         data_file = 'EV_histogram.csv',
        #         xvals=None,
        #         bar_width=1.0,
        #         ylim=(0, 1.15),
        #         xlim=(230, 431),
        #         xticks_interval=40,
        #         yticks_interval=0.4,
        #         ylab_txt='Prob. of exact # of EV (%)',
        #         ylab_rotation=90,
        #         ylab_pad=0.045,
        #         xlab_txt = 'Electoral votes for Biden',
        #         title_txt='Today\'s median: {median_value:.0f} EV for Biden',
        #         hard_median = True,
        #         vline_xpos=270,
        #         vline_labels = ['Trump\nwins', 'Biden\nwins'],
        #         out_path=path)

        # ## generate thumbnail version
        # path = os.path.join(out_dir, 'thumb_ev_histogram_2024')
        # generate_histogram(
        #         data_file = 'EV_histogram.csv',
        #         xvals=None,
        #         bar_width=1.0,
        #         ylim=(0, 1.15),
        #         xlim=(230, 431),
        #         xticks_interval=40,
        #         yticks_interval=0.4,
        #         ylab_rotation=90,
        #         ylab_pad=0.00,
        #         xlab_txt = 'Electoral votes for Biden',
        #         # title_txt='Today\'s median: {median_value:.0f} votes for Biden',
        #         hard_median = True,
        #         vline_xpos=270,
        #         vline_labels = ['Trump', 'Biden'],
        #         vline_lab_pad = 0.105,
        #         vline_lab_ypos = 0.85,
        #         thumbnail = True,
        #         out_path=path)



# ======================================================================

def generate_house_graphics():
        generate_house_meta_lead_graphics()

def generate_senate_graphics():
        generate_senate_meta_lead_graphics()
        generate_senate_dem_seats()
        # generate_senate_histogram_graphics()

def generate_presidential_graphics():
        generate_ev_meta_lead_graphics()
        generate_ev_estimator_graphics()
        # generate_ev_histogram_graphics()

def main():
    generate_house_graphics()
    generate_senate_graphics()
    generate_presidential_graphics()

if __name__ == '__main__':
    main()