from plotting import generate_line_plot, generate_histogram
import numpy as np
import os

out_dir = './outputs'
os.makedirs(out_dir, exist_ok=True)

# plot 0
path = os.path.join(out_dir, 'meta_lead_senate')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
        x_column=0,
        y_column=-1,
        ylim=None,
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
        x_column=0,
        y_column=2,
        yerr_columns=[8,9],
        ylim=None,
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
        x_column=0,
        y_column=2,
        yerr_columns=None,
        ylim=(100, 360),
        yticks_interval=30,
        ylab_txt = 'Trump\nelectoral\nvotes',
        ylab_rotation = 0,
        ylab_pad=0.055,
        title_txt='{last_value:.0f} Trump electoral votes expected',
        hline_ypos = 270,
        hline_labels = ['Biden leads', 'Trump leads'],
        color_reverse = True,
        out_path=path)

# plot 3
path = os.path.join(out_dir, 'senate_histogram')
generate_histogram(
        data_file = 'Senate_histogram.csv',
        xvals=np.arange(44, 61),
        ylim=(0, 1.15),
        xlim=None,
        xticks_interval=5,
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
        xlim=None,
        xticks_interval=40,
        yticks_interval=0.4,
        ylab_txt='Prob.\nof exact\n# of EV\n(%)',
        ylab_pad=0.055,
        xlab_txt = 'Electoral votes for Biden',
        title_txt='Mean: {mean_value:.0f} votes for Biden',
        vline_xpos=270,
        vline_labels = ['Trump\nwins', 'Biden\nwins'],
        out_path=path)
