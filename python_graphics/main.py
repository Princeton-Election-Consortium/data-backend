from plotting import generate_line_plot, generate_histogram, generate_dual_line_plot
import numpy as np
import os

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

# plot 0
path = os.path.join(out_dir, 'meta_lead_senate')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
        x_column='date',
        y_column='meta_margin',
        ylab_txt='Meta-\nmargin',
        ylab_pad=0.06,
        yticklab_format = True,
        title_txt = 'Popular meta-lead for Senate control',
        hline_ypos = 0,
        hline_labels = ['R control', 'D+I control'],
        shading = True,
        out_path=path)

# plot 1
path = os.path.join(out_dir, 'dem_senate_seats')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
        x_column='date',
        y_column='mean_seats',
        yerr_columns=['1sigma_lower', '1sigma_upper'],
        ylab_txt='Dem/Ind\nseats (%)',
        ylab_pad=0.055,
        ylab_rotation = 0,
        title_txt='{last_value:.0f} Democratic Senate seats expected',
        hline_ypos = 49.5,
        hline_labels = ['R control', 'D+I control'],
        out_path=path)

# plot 2
path = os.path.join(out_dir, 'president_estimator')
generate_line_plot(
        data_file = 'EV_estimate_history.csv',
        strike_zone_data_file = 'EV_prediction.csv',
        x_column='date',
        y_column='median_EV0', # 0=biden, 1=trump
        x_minus_yvalues=533, # to make in terms of trump
        yerr_columns=['95ci_lower', '95ci_upper'],
        ylim=None,
        yticks_interval=40,
        ylab_txt = 'Trump\nelectoral\nvotes',
        ylab_rotation = 0,
        ylab_pad=0.058,
        title_txt='{last_value:.0f} Trump electoral votes expected',
        strike_colors = ['#909090', '#c8c8c8'],
        hline_ypos = 270,
        hline_labels = ['Biden leads', 'Trump leads'],
        hline_lab_xpos = 0.35,
        hline_lab_pad = 0.05,
        color_reverse = True,
        out_path=path)
'''
* Electoral vote time series: can it please have the red/yellow strike zone of 1-sigma and 2-sigma November outcomes? The zones can be a more neutral color too, like dark gray/light gray.
* Electoral vote time series: can there please be a shaded zone, as done for the Senate time series?
'''

# plot 3
path = os.path.join(out_dir, 'senate_histogram')
generate_histogram(
        data_file = 'Senate_histogram.csv',
        xvals=np.arange(44, 61),
        ylim=(0, 1.15),
        xlim=(46, 56.5),
        xticks_interval=1,
        yticks_interval=5,
        ylab_txt='Probability\n(%)',
        ylab_pad=0.054,
        xlab_txt = 'Democratic + Independent Senate seats',
        title_txt='Mean: {mean_value:.0f} D+I Senate seats',
        vline_xpos = 49.6,
        vline_labels = ['R\ncontrol', 'D+I\ncontrol'],
        out_path=path)

# plot 4
path = os.path.join(out_dir, 'ev_histogram')
generate_histogram(
        data_file = 'EV_histogram.csv',
        xvals=None,
        bar_width=1.0,
        ylim=(0, 1.15),
        xlim=(230, 431),
        xticks_interval=40,
        yticks_interval=0.4,
        ylab_txt='Prob.\nof exact\n# of EV\n(%)',
        ylab_pad=0.055,
        xlab_txt = 'Electoral votes for Biden',
        title_txt='Mean: {mean_value:.0f} votes for Biden',
        vline_xpos=270,
        vline_labels = ['Trump\nwins', 'Biden\nwins'],
        out_path=path)

# plot 5
path = os.path.join(out_dir, 'house_meta_margin')
generate_line_plot(
        data_dir='../matlab',
        data_file='2020.generic.polls.median.txt',
        read_csv_kw = dict(delimiter=r"\s+"),
        height_to_width=0.5,
        width=10,
        axes_box = [0.24, 0.1, 0.5, 0.75],
        x_column='date',
        y_column='median_margin',
        yerr_columns=['esd'],
        ylim=(-5, 16),
        yticks_interval=4,
        ylab_txt='House\nmeta-\nmargin',
        ylab_pad=0.09,
        ylab_rotation = 0,
        title_txt='House control meta-margin: {party}{last_value:.01f}%',
        shading = False,
        hline_ypos = 3,
        hline_lw = 0.5,
        hline_color = 'black',
        hline_labels = None,
        circle_size = 0,
        watermark_pos=[0.77, 0.95],
        plot_customization = True,
        out_path=path)
