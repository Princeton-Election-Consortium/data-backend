from plotting import generate_line_plot, generate_histogram
import numpy as np
import os

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

path = os.path.join(out_dir, 'meta_lead_senate')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
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
path = os.path.join(out_dir, 'thumb_meta_lead_senate')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
        x_column='date',
        y_column='meta_margin',
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt = 'Meta-margin for Senate control',
        hline_ypos = 0,
        hline_labels = ['R control', 'D+I control'],
        hline_label_units = '%',
        hline_lab_xpos = 0.75,
        hline_lab_pad = 0.1,
        title_pad = 0,
        shading = True,
        thumbnail = True,
        out_path=path)

path = os.path.join(out_dir, 'meta_lead_president')
generate_line_plot(
        data_file='EV_estimate_history.csv',
        x_column='date',
        y_column='meta_margin',
        ylab_txt='Meta-margin',
        ylab_pad=0.05,
        ylab_rotation=90,
        yticklab_format = True,
        title_txt = 'Popular meta-lead for President',
        hline_ypos = 0,
        hline_labels = ['Trump leads','Biden leads'],
        hline_label_units = '%',
        presidential_2020 = True,
        shading = True,
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_meta_lead_president')
generate_line_plot(
        data_file='EV_estimate_history.csv',
        x_column='date',
        y_column='meta_margin',
        ylab_pad=0.00,
        ylab_rotation=90,
        yticklab_format = True,
        title_txt = 'Presidential Meta-margin',
        hline_ypos = 0,
        hline_labels = ['Trump leads','Biden leads'],
        hline_label_units = '%',
        presidential_2020 = True,
        hline_lab_xpos = 0.75,
        hline_lab_pad = 0.1,
        title_pad = 0,
        shading = True,
        thumbnail = True,
        out_path=path)

path = os.path.join(out_dir, 'dem_senate_seats')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
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

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_dem_senate_seats')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
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
        hline_lab_pad = 0.1,
        title_pad = 0,
        thumbnail = True,
        out_path=path)

path = os.path.join(out_dir, 'president_estimator')
generate_line_plot(
        data_file = 'EV_estimate_history.csv',
        strike_zone_data_file = 'EV_prediction.csv',
        x_column='date',
        y_column='median_EV0', # 0=biden, 1=trump
        x_minus_yvalues= None, # to make in terms of trump
        yerr_columns=['95ci_lower', '95ci_upper'],
        ylim=None,
        yticks_interval=40,
        ylab_txt='Biden electoral votes',
        ylab_rotation=90,
        ylab_pad=0.048,
        title_txt='{last_value:.0f} Biden electoral votes expected',
        strike_colors = ['#c62535', (.97, .965, .494)],
        hline_ypos = 270,
        hline_labels = ['Trump leads', 'Biden leads'],
        hline_lab_xpos = 0.35,
        hline_lab_pad = 0.05,
        color_reverse = False,
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_president_estimator')
generate_line_plot(
        data_file = 'EV_estimate_history.csv',
        strike_zone_data_file = 'EV_prediction.csv',
        x_column='date',
        y_column='median_EV0', # 0=biden, 1=trump
        x_minus_yvalues= None, # to make in terms of trump
        yerr_columns=['95ci_lower', '95ci_upper'],
        ylim=None,
        yticks_interval=40,
        ylab_rotation=90,
        ylab_pad=0.00,
        title_txt='Today: Biden {last_value:.0f} Trump {inv_pres_last_value:.0f} EV',
        strike_colors = ['#c62535', (.97, .965, .494)],
        hline_ypos = 270,
        hline_labels = ['Trump leads', 'Biden leads'],
        hline_label_units = "given",
        hline_lab_xpos = 0.35,
        hline_lab_pad = 0.08,
        color_reverse = False,
        title_pad = 0,
        thumbnail = True,
        out_path=path)

path = os.path.join(out_dir, 'senate_histogram')
generate_histogram(
        data_file = 'Senate_histogram.csv',
        xvals=np.arange(44, 61),
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
path = os.path.join(out_dir, 'thumb_senate_histogram')
generate_histogram(
        data_file = 'Senate_histogram.csv',
        xvals=np.arange(44, 61),
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

path = os.path.join(out_dir, 'ev_histogram')
generate_histogram(
        data_file = 'EV_histogram.csv',
        xvals=None,
        bar_width=1.0,
        ylim=(0, 1.15),
        xlim=(230, 431),
        xticks_interval=40,
        yticks_interval=0.4,
        ylab_txt='Prob. of exact # of EV (%)',
        ylab_rotation=90,
        ylab_pad=0.045,
        xlab_txt = 'Electoral votes for Biden',
        title_txt='Today\'s median: {median_value:.0f} EV for Biden',
        hard_median = True,
        vline_xpos=270,
        vline_labels = ['Trump\nwins', 'Biden\nwins'],
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_ev_histogram')
generate_histogram(
        data_file = 'EV_histogram.csv',
        xvals=None,
        bar_width=1.0,
        ylim=(0, 1.15),
        xlim=(230, 431),
        xticks_interval=40,
        yticks_interval=0.4,
        ylab_rotation=90,
        ylab_pad=0.00,
        xlab_txt = 'Electoral votes for Biden',
        # title_txt='Today\'s median: {median_value:.0f} votes for Biden',
        hard_median = True,
        vline_xpos=270,
        vline_labels = ['Trump', 'Biden'],
        vline_lab_pad = 0.105,
        vline_lab_ypos = 0.85,
        thumbnail = True,
        out_path=path)


path = os.path.join(out_dir, 'house_meta_margin')
generate_line_plot(
        data_dir='../matlab',
        data_file='2020.generic.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-1, 15),
        yticks_interval=4,
        ylab_txt='House control meta-margin',
        ylab_pad=0.068,
        ylab_rotation=90,
        title_txt='House control meta-margin: {party}{last_value:.01f}%',
        title_pad=5,
        shading = False,
        hline_ypos = 3,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = None,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        out_path=path)

## new strike zone and standard formatting version
path = os.path.join(out_dir, 'house_meta_margin_new')
generate_line_plot(
        data_dir='../matlab',
        data_file='2020.generic.polls.median.txt',
        strike_zone_data_file = './outputs/House_predictions.csv',
        strike_colors = ['#c62535', (.97, .965, .494)],
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-1, 15),
        yticks_interval=4,
        ylab_txt='House control meta-margin',
        ylab_pad=0.068,
        ylab_rotation=90,
        title_txt='House control meta-margin: {party}{last_value:.01f}%',
        title_pad=5,
        shading = True,
        hline_ypos = 3,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = None,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        plot_customization_2 = True,
        out_path=path)

## generate thumbnail version
path = os.path.join(out_dir, 'thumb_house_meta_margin')
generate_line_plot(
        data_dir='../matlab',
        data_file='2020.generic.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.55,
        width=9,
        axes_box = [0.19, 0.1, 0.60, 0.75],
        x_column='date',
        y_column='median_margin',
        yerr_columns=['esd'],
        xtick_pad=0.018,
        ylim=(-1, 15),
        yticks_interval=4,
        ylab_pad=0.00,
        ylab_rotation=90,
        title_txt='Meta-margin for House Control',
        title_pad=0,
        shading = False,
        hline_ypos = 3,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = ["", '{party}{last_value:.01f}%'],
        hline_label_units = "given",
        hline_lab_xpos = 0.85,
        hline_lab_pad = 0.25,
        se_xpos= 0.732,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        thumbnail = True,
        out_path=path)
