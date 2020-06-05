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
        ylim=(-2, 5),
        ylab_txt='Meta-\nmargin',
        ylab_pad=0.06,
        yticklab_format = True,
        title_txt = 'Popular meta-lead for Senate control',
        hline_ypos = 0,
        shading = True,
        out_path=path)

# plot 1
path = os.path.join(out_dir, 'dem_senate_seats')
generate_line_plot(
        data_file='Senate_estimate_history.csv',
        x_column=0,
        y_column=2,
        yerr_columns=[8,9],
        ylim=(46, 56),
        ylab_txt='Dem/Ind\nseats (%)',
        ylab_pad=0.055,
        ylab_rotation = 0,
        title_txt = 'Expected Democratic Senate seats',
        hline_ypos = 49.5,
        #circle_size = 0,
        shading = True,
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
        title_txt = 'President: state-poll-based estimator',
        hline_ypos = 270,
        #circle_size = 0,
        shading = True,
        shading_reverse = True,
        hline_labels = ['Trump leads', 'Biden leads'],
        out_path=path)

# plot 3
path = os.path.join(out_dir, 'senate_histogram')
generate_histogram(
        data_file = 'Senate_histogram.csv',
        xvals=np.arange(44, 61),
        data_factor=100,
        ylim=(0, 30),
        xlim=(45, 61),
        xticks_interval=5,
        yticks_interval=5,
        ylab_txt='Probability\n(%)',
        ylab_rotation=0,
        ylab_pad=0.051,
        xlab_txt = 'Democratic + Independent Senate seats',
        xlab_pad=3,
        title_txt = 'Distribution of possible outcomes',
        vline_ypos = 49,
        out_path=path)

# plot 4
path = os.path.join(out_dir, 'ev_histogram')
generate_histogram(
        data_file = 'EV_histogram.csv',
        xvals=None,
        data_factor=100,
        bar_width=1.0,
        ylim=(0, 2),
        xlim=(220, 420),
        xticks_interval=40,
        yticks_interval=0.4,
        ylab_txt='Prob.\nof exact\n# of EV\n(%)',
        ylab_rotation=0,
        ylab_pad=0.055,
        xlab_txt = 'Electoral votes for Biden',
        xlab_pad=3,
        title_txt='Distribution of possible outcomes',
        vline_ypos=270,
        vline_labels = ['Biden\nwins', 'Trump\nwins'],
        vline_lab_pad=30,
        out_path=path)
