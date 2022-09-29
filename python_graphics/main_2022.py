from plotting import generate_line_plot, generate_histogram
import numpy as np
import os
import pandas as pd

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

path = os.path.join(out_dir, 'meta_lead_senate_2022')
generate_line_plot(
        data_file='Senate_estimate_history_2022.csv',
        x_column='date',
        y_column='meta_margin',
        ylab_txt='Meta-margin',
        ylab_pad=0.05,
        ylab_rotation=90,
        yticklab_format = True,
        title_txt = 'Popular meta-lead for Senate control',
        hline_ypos = 0,
        hline_labels = ['R control', 'D+I control'],
        shading = True,
        out_path=path)

## generate thumbnail version
#  suitable for reproduction at 200 pixel width. No axis labels. No tick marks
path = os.path.join(out_dir, 'thumb_meta_lead_senate_2022')
generate_line_plot(
        data_file='Senate_estimate_history_2022.csv',
        x_column='date',
        y_column='meta_margin',
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt = 'Meta-margin Senate control',
        hline_ypos = 0,
        hline_labels = ['R control', 'D+I control'],
        hline_label_units = '%',
        hline_lab_xpos = 0.75,
        hline_lab_pad = 0.1,
        title_pad = 0,
        shading = True,
        thumbnail = True,
        out_path=path)

path = os.path.join(out_dir, 'dem_senate_seats_2022')
generate_line_plot(
        data_file='Senate_estimate_history_2022.csv',
        x_column='date',
        y_column='mean_seats',
        yerr_columns=['1sigma_lower', '1sigma_upper'],
        ylab_txt='Dem/Ind seats',
        ylab_pad=0.04,
        ylab_rotation=90,
        title_txt='{last_value:.0f} Democratic Senate seats expected',
        hline_ypos = 49.5,
        hline_labels = ['R control', 'D+I control'],
        out_path=path)

# generate thumbnail version
path = os.path.join(out_dir, 'thumb_dem_senate_seats_2022')
generate_line_plot(
        data_file='Senate_estimate_history_2022.csv',
        x_column='date',
        y_column='mean_seats',
        yerr_columns=['1sigma_lower', '1sigma_upper'],
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt='Senate seats expected',
        hline_ypos = 49.5,
        hline_labels = ["R {inv_last_value:.0f}", '{last_value:.0f} D+I seats'],
        hline_label_units = "given",
        hline_lab_xpos = 0.75,
        hline_lab_pad = 0.42,
        title_pad = 0,
        thumbnail = True,
        out_path=path)

path = os.path.join(out_dir, 'senate_histogram_2022')
generate_histogram(
        data_file = 'Senate_histogram_2022.csv',
        xvals=np.arange(46, 58),
        ylim=(0, 1.15),
        xlim=(47, 58),
        xticks_interval=1,
        yticks_interval=5,
        ylab_txt='Probability (%)',
        ylab_rotation=90,
        ylab_pad=0.044,
        xlab_txt = 'Democratic + Independent Senate seats',
        title_txt='Median: {median_value:.0f} D+I Senate seats',
        vline_xpos = 49.6,
        vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_senate_histogram_2022')
generate_histogram(
        data_file = 'Senate_histogram_2022.csv',
        xvals=np.arange(46, 58),
        ylim=(0, 1.15),
        xlim=(46, 56.5),
        xticks_interval=1,
        yticks_interval=5,
        ylab_rotation=90,
        ylab_pad=0.00,
        title_txt='Median: {median_value:.0f} D+I Senate seats',
        vline_xpos = 49.6,
        vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
        vline_lab_pad = 0.125,
        vline_lab_ypos = 0.85,
        thumbnail = True,
        out_path=path)
# generic_pols = pd.read_csv() 
# df = pd.DataFrame(columns = )

## new strike zone and standard formatting version
path = os.path.join(out_dir, 'house_meta_margin_new_2022')
generate_line_plot(
        data_dir='../matlab',
        data_file='2022.generic.polls.median.txt',
        strike_zone_data_file = './outputs/House_predictions.csv',
        strike_colors = ['#c62535', (.97, .965, .494)],
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='julian_date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-8, 9),
        yticks_interval=4,
        ylab_txt='House control meta-margin',
        ylab_pad=0.068,
        ylab_rotation=90,
        title_txt='House control meta-margin: {party}{last_value:.01f}%',
        title_pad=5,
        shading = True,
        hline_ypos = 2,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = None,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        plot_customization_2 = True,
        plot_customization_3 = True,
        out_path=path)

## new strike zone and standard formatting version
path = os.path.join(out_dir, 'house_meta_margin_2022')
generate_line_plot(
        data_dir='../matlab',
        data_file='2022.generic.polls.median.txt',
        strike_zone_data_file = './outputs/House_predictions.csv',
        strike_colors = ['#c62535', (.97, .965, .494)],
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='julian_date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-8, 8),
        yticks_interval=4,
        ylab_txt='House control meta-margin',
        ylab_pad=0.068,
        ylab_rotation=90,
        title_txt='House control meta-margin: {party}{last_value:.01f}%',
        title_pad=5,
        shading = True,
        hline_ypos = 2,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = None,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        plot_customization_2 = True,
        plot_customization_3 = True,
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_house_meta_margin_new_2022')
generate_line_plot(
        data_dir='../matlab',
        data_file='2022.generic.polls.median.txt',
        strike_zone_data_file = './outputs/House_predictions.csv',
        strike_colors = ['#c62535', (.97, .965, .494)],
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='julian_date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-8, 8),
        yticks_interval=4,
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt='Meta-margin House Control',
        title_pad=0,
        shading = True,
        hline_ypos = 2,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = ["", '{party}{last_value:.01f}%'],
        hline_label_units = "given",
        hline_lab_xpos = 0.2,
        hline_lab_ypos = 1.1,
        hline_lab_pad = 0.25,
        se_xpos= 0.732,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        plot_customization_2 = True,
        thumbnail = True,
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_house_meta_margin_2022')
generate_line_plot(
        data_dir='../matlab',
        data_file='2022.generic.polls.median.txt',
        strike_zone_data_file = './outputs/House_predictions.csv',
        strike_colors = ['#c62535', (.97, .965, .494)],
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='julian_date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-8, 8),
        yticks_interval=4,
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt='Meta-margin House Control',
        title_pad=0,
        shading = True,
        hline_ypos = 2,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = ["", '{party}{last_value:.01f}%'],
        hline_label_units = "given",
        hline_lab_xpos = 0.2,
        hline_lab_ypos = 1.1,
        hline_lab_pad = 0.25,
        se_xpos= 0.732,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        plot_customization_2 = True,
        thumbnail = True,
        out_path=path)

## old format with special elections cbox + hline
path = os.path.join(out_dir, 'house_meta_margin_old_2022')
generate_line_plot(
        data_dir='../matlab',
        data_file='2022.generic.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='julian_date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-8, 8),
        yticks_interval=4,
        ylab_txt='House control meta-margin',
        ylab_pad=0.068,
        ylab_rotation=90,
        title_txt='House control meta-margin: {party}{last_value:.01f}%',
        title_pad=5,
        shading = False,
        hline_ypos = 2,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = None,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        out_path=path)

## old format with special elections cbox + hline
## generate thumbnail version
path = os.path.join(out_dir, 'thumb_house_meta_margin_old_2022')
generate_line_plot(
        data_dir='../matlab',
        data_file='2022.generic.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='julian_date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-8, 8),
        yticks_interval=4,
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt='Meta-margin House Control',
        title_pad=0,
        shading = False,
        hline_ypos = 2,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = ["", '{party}{last_value:.01f}%'],
        hline_label_units = "given",
        hline_lab_xpos = 0.2,
        hline_lab_ypos = -9,
        hline_lab_pad = 0.25,
        se_xpos= 0.25,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        thumbnail = True,
        out_path=path)
