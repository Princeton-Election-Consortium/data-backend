
import os

import numpy as np
import pandas as pd

from plotting_util import generate_line_plot

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

# Year = 2024

width=8 # inches - or 9
height_to_width = 0.8 # ratio
width_pixels_save=2000
watermark = 'election.princeton.edu'
watermark_pos=[0.77, 0.95]

# == HOUSE =============================================================

# Figure parameters
house_width = 9
house_height_to_width = 0.55
house_axes_box = [0.19, 0.1, 0.60, 0.75]

# out_path is unique to each one
# maybe match column names to their index

# Shared between general and thumbnail
house_kw = dict(
    
        # Data parameters
        data_dir = '../scraping/outputs', # '../matlab'
        data_file = '2024.house.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        strike_zone_data_file = './outputs/House_predictions.csv', # Where is this? matlab/outputs
        
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

# == SENATE ============================================================

# path = os.path.join(out_dir, 'meta_lead_senate_2024')
# generate_line_plot(
#         data_dir='../scraping/outputs',
#         data_file='2024.Senate.polls.median.txt',
#         x_column=1,
#         y_column=2,
#         ylab_txt='Meta-margin',
#         ylab_pad=0.05,
#         ylab_rotation=90,
#         yticklab_format = True,
#         title_txt = 'Popular meta-lead for Senate control',
#         hline_ypos = 0,
#         hline_labels = ['R control', 'D+I control'],
#         out_path=path)