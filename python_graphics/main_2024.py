
import os

import numpy as np
import pandas as pd

from plotting_util import generate_line_plot
from plotting_util import generate_line_plot_debug

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

# Year = 2024

width=8 # inches - or 9
height_to_width = 0.8 # ratio
width_pixels_save=2000 # SET PARAMETER
watermark = 'election.princeton.edu'
watermark_pos=[0.77, 0.95]

# # == HOUSE =============================================================

# Figure parameters
house_width = 9
house_height_to_width = 0.55
house_axes_box = [0.19, 0.1, 0.60, 0.75]

# out_path is unique to each one
# maybe match column names to their index

house_kw = dict(
        # Data parameters
        data_dir = '../scraping/outputs', # '../matlab'
        data_file = '2024.house.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        # strike_zone_data_file = './outputs/House_predictions.csv', # Where is this? matlab/outputs
        
        # Column parameters
        x_column=1, # julian_date
        y_column=3, # median_margin
        yerr_columns=[4], # esd

        hline_ypos = 0, # SET PARAMETER

        # Color parameters
        shading = True,
        strike_colors = ['#c62535', (.97, .965, .494)],

        # Tick parameters
        ylim=(-14, 10),
        yticks_interval=2,

        # Custom parameters
        plot_customization = True,
        plot_customization_3=True,

        # Output parameters
        width_pixels_save=width_pixels_save
)

def generate_house_graphics():
        house_meta_margin_2024 = os.path.join(out_dir, 'house_meta_margin_2024')
        generate_line_plot(
                # Figure parameters
                width=house_width,
                height_to_width=house_height_to_width,
                axes_box=house_axes_box,

                title_txt='House control meta-margin: {party}{last_value:.01f}%',
                title_pad=5,
                ylab_txt='House control meta-margin',

                out_path=house_meta_margin_2024,

                **house_kw
        )

        # generate thumbnail version
        thumb_house_meta_margin_2024 = os.path.join(out_dir, 'thumb_house_meta_margin_2024')
        generate_line_plot(
                width=house_width,
                height_to_width=house_height_to_width,
                axes_box=house_axes_box,

                title_txt="House control meta-margin",
                title_pad=0,


                ylab_pad=0,

                # hline_label stuff
                hline_label = '{party}{last_value:.01f}%', # plus label_units,
                # hline_label_units="given",    

                thumbnail=True,
                out_path=thumb_house_meta_margin_2024,

                **house_kw
        )
generate_house_graphics()

# # == SENATE ============================================================


def generate_senate_meta_lead_graphics():

        senate_meta_lead_kw = dict(
                # Data parameters
                # data_dir = '../scraping/outputs', # '../matlab'
                data_file='Senate_estimate_history_2024.csv',

                # Column parameters
                x_column=0, # Date
                y_column=11, # meta-margin

                hline_ypos = 0,
                hline_labels = ['R control', 'D+I control'],
        )

        senate_meta_lead = os.path.join(out_dir, 'meta_lead_senate_2024')
        generate_line_plot(

                ylab_txt='Meta-margin',
                title_txt = 'Popular meta-lead for Senate control',

                out_path=senate_meta_lead,

                **senate_meta_lead_kw
        )

        ## generate thumbnail version
        #  suitable for reproduction at 200 pixel width. No axis labels. No tick marks
        path = os.path.join(out_dir, 'thumb_meta_lead_senate_2024')
        generate_line_plot(
                title_txt = 'Meta-margin Senate control',

                hline_label_units = '%',
                hline_lab_xpos = 0.75,
                hline_lab_pad = 0.1,

                # Distance/pad parameters
                title_pad = 0,
                ylab_pad=0.00,

                # Output parammeters
                thumbnail = True,
                out_path=path,

                **senate_meta_lead_kw
        )

def generate_senate_dem_seats():

        senate_dem_seats_kw = dict(
                # Data parameters
                # data_dir = '../scraping/outputs', # '../matlab'
                data_file='Senate_estimate_history_2024.csv',

                # Column parameters
                x_column=0, # Date
                y_column=2, # mean_seats
                yerr_columns= [8,9], #['1sigma_lower', '1sigma_upper'],

                hline_ypos = 49.5,
        )

        path = os.path.join(out_dir, 'dem_senate_seats_2024')
        generate_line_plot(
                ylab_txt='Dem/Ind seats',
                # ylab_pad=0.04,
                title_txt='{last_value:.0f} Democratic Senate seats expected',
                hline_labels = ['R control', 'D+I control'],
                out_path=path,

                **senate_dem_seats_kw
        )

        # generate thumbnail version
        # NOT GENERATING THE H_LABELS...
        path = os.path.join(out_dir, 'thumb_dem_senate_seats_2024')
        generate_line_plot(
                ylab_pad=0.00,
                title_txt='Senate seats expected',
                hline_labels = ["R {inv_last_value:.0f}", '{last_value:.0f} D+I seats'],
                hline_label_units = "given",
                hline_lab_xpos = 0.75,
                hline_lab_pad = 0.42,
                title_pad = 0,
                thumbnail = True,
                out_path=path,
        
                **senate_dem_seats_kw
        )

# def generate_senate_histogram_graphics():
#         path = os.path.join(out_dir, 'senate_histogram_2022')
#         generate_histogram(
#                 data_file = 'Senate_histogram_2022.csv',
#                 xvals=np.arange(46, 58), # 2020- (43,61)
#                 ylim=(0, 1.15),
#                 xlim=(47, 58),
#                 xticks_interval=1,
#                 yticks_interval=5,
#                 ylab_txt='Probability (%)',
#                 ylab_rotation=90,
#                 ylab_pad=0.044,
#                 xlab_txt = 'Democratic + Independent Senate seats',
#                 title_txt='Median: {median_value:.0f} D+I Senate seats',
#                 vline_xpos = 49.6,
#                 vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
#                 out_path=path)

#         ## generate thumbnail version
#         path = os.path.join(out_dir, 'thumb_senate_histogram_2022')
#         generate_histogram(
#                 data_file = 'Senate_histogram_2022.csv',
#                 xvals=np.arange(46, 58),
#                 ylim=(0, 1.15),
#                 xlim=(46, 56.5),
#                 xticks_interval=1,
#                 yticks_interval=5,
#                 ylab_rotation=90,
#                 ylab_pad=0.00,
#                 title_txt='Median: {median_value:.0f} D+I Senate seats',
#                 vline_xpos = 49.6,
#                 vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
#                 vline_lab_pad = 0.125,
#                 vline_lab_ypos = 0.85,
#                 thumbnail = True,
#                 out_path=path)

def generate_senate_graphics():
        generate_senate_meta_lead_graphics()
        generate_senate_dem_seats()

generate_senate_graphics()

# == PRESIDENTIAL ======================================================

# path = os.path.join(out_dir, 'meta_lead_president_2024')
# generate_line_plot(
#         data_file='EV_estimate_history_2024.csv',
#         x_column=0, # date
#         y_column=13, # meta-margin
#         ylab_txt='Meta-margin',
#         ylab_pad=0.05,
#         title_txt = 'Popular meta-lead for President',
#         hline_ypos = 0,
#         hline_labels = ['Trump leads','Biden leads'],
#         hline_label_units = '%',
#         # presidential_2020 = True,
#         shading = True,
#         out_path=path,

#         ylim=(-6, 2), ## AUTOMATE?
# )

# ## generate thumbnail version
# path = os.path.join(out_dir, 'thumb_meta_lead_president_2024')
# generate_line_plot(
#         data_file='EV_estimate_history.csv',
#         x_column='date',
#         y_column='meta_margin',
#         ylab_pad=0.00,
#         ylab_rotation=90,
#         yticklab_format = True,
#         title_txt = 'Presidential Meta-margin',
#         hline_ypos = 0,
#         hline_labels = ['Trump leads','Biden leads'],
#         hline_label_units = '%',
#         presidential_2020 = True,
#         hline_lab_xpos = 0.75,
#         hline_lab_pad = 0.1,
#         title_pad = 0,
#         shading = True,
#         thumbnail = True,
#         out_path=path)

# Working!
# path = os.path.join(out_dir, 'president_estimator_2024')
# generate_line_plot(
#         data_file = 'EV_estimate_history_2024.csv',
#         strike_zone_data_file = 'EV_prediction_2024.csv',
#         x_column=0, # date
#         y_column= 1, #'median_EV0', # 0=biden, 1=trump
#         # x_minus_yvalues= None, # to make in terms of trump
#         yerr_columns= [10,11], # ['95ci_lower', '95ci_upper'],
#         # ylim=None,
#         yticks_interval=40,
#         ylab_txt='Biden electoral votes',
#         ylab_pad=0.048,
#         title_txt='{last_value:.0f} Biden electoral votes expected',
#         # strike_colors = ['#c62535', (.97, .965, .494)],
#         strike_colors = ['#c62535', '#c62535'],
#         hline_ypos = 270,
#         hline_labels = ['Trump leads', 'Biden leads'],
#         hline_lab_xpos = 0.35,
#         hline_lab_pad = 0.05,
#         # color_reverse = False,
#         out_path=path,

#         ylim=(150,300),
# )

# ## generate thumbnail version
# path = os.path.join(out_dir, 'thumb_president_estimator_2024')
# generate_line_plot(
#         data_file = 'EV_estimate_history.csv',
#         strike_zone_data_file = 'EV_prediction.csv',
#         x_column='date',
#         y_column='median_EV0', # 0=biden, 1=trump
#         x_minus_yvalues= None, # to make in terms of trump
#         yerr_columns=['95ci_lower', '95ci_upper'],
#         ylim=None,
#         yticks_interval=40,
#         ylab_rotation=90,
#         ylab_pad=0.00,
#         title_txt='Today: Biden {last_value:.0f} Trump {inv_pres_last_value:.0f} EV',
#         strike_colors = ['#c62535', (.97, .965, .494)],
#         hline_ypos = 270,
#         hline_labels = ['Trump leads', 'Biden leads'],
#         hline_label_units = "given",
#         hline_lab_xpos = 0.35,
#         hline_lab_pad = 0.08,
#         color_reverse = False,
#         title_pad = 0,
#         thumbnail = True,
#         out_path=path)

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