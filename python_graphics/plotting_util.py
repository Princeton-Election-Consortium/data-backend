import os
import csv
import calendar
import datetime as dt

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory as blend
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
# TODO: Move to another call

month_names = {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec',
           }
D_color = '#1660CE'
R_color = '#C62535'
zone_colors = [D_color, R_color]

year = 2024
doy2dt = lambda d: dt.datetime(year, 1, 1) + dt.timedelta(int(d)-1)
# TODO: Change doy2dt
# pd.to_datetime('2024-01-01') + pd.to_timedelta(julian_days - 1, unit='D')

def load_data(data_dir, data_file, read_csv_kw):
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path, header=None, **read_csv_kw)
    return data 

def prepare_data(data, x_column, y_column):
    """
    data: DataFrame

    Assuming days is an array of Julian days for the current calendar year
    """
    # Sort data based on x-values 
    # print(data)
    data.sort_values(by=x_column, inplace=True)

    # Extract x-values and convert to datetime objects
    days = data[x_column].values
    julian_days = days
    # Creates a pandas datetime object for the start of the year (January 1st, 2024)
    # Adds a timedelta corresponding to the Julian days to get the desired dates
    # dates = pd.to_datetime('2024-01-01') + pd.to_timedelta(julian_days - 1, unit='D')
    dates = np.array([doy2dt(d) for d in days])
    
    # Extract y-values (data to plot)
    vals = data[y_column].values
    
    return julian_days, dates, vals

def generate_line_plot(
                # Figure parameters (SET)
                width=9,
                height_to_width=0.80,
                width_pixels_save=2000,
                # axes_box=[0.1, 0.1, 0.8, 0.8],
                axes_box=[0.2, 0.1, 0.65, 0.75],
                watermark='',
                watermark_pos=(0.5, 0.5),

                # ------------------------------------------------------

                # Data parameters
                data_dir="",
                data_file="",
                read_csv_kw={},
                strike_zone_data_file=None,
                strike_zone_house=False,

                # Column / line parameters
                x_column=0,
                y_column=-1,
                yerr_columns=None,
                hline_ypos=None,

                # Axes / tick parameters
                ylim=None, # TODO: Move/rename
                yticks_interval = 1, # 4-5
                ax_offset=0, 

                # ------------------------------------------------------

                # Text parameters
                title_txt='',
                title_pad = 5,
                ylab_txt='',
                ylab_pad = 0.135,

                hline_label=None, # one, use for House
                hline_labels=None,
                hline_label_units='',
                hline_lab_xpos=0.85, # Set - try changing? 0.35 
                hline_lab_ypos=None,

                # Size parameters
                size_scale=1, 
                font_size=10, 
                circle_size=3, # Check

                # Color parameters
                zone_colors=zone_colors,

                shading=True, # Default True!
                # shading_kw=dict(zorder=0, alpha=0.15, lw=0), # move
                # yerr_kw=dict(color='grey', alpha=0.3, lw=0), # move
                
                hline_lab_colors=None,
                strike_colors=['#c62535', '#FFFF00'],

                # Distance/pad parameters
                hline_lw=1, # If thumbnail, 0.5? Add back as arg?
                xtick_pad = 0.035, 
                hline_lab_pad = 0.06,  # Set
                
                # Output parameters
                thumbnail=False,
                out_path="output", # CHANGE
                out_format="png",

                # Customs
                meta_lead_graphic=False,
                custom_twin_axis=False,
                custom_h_line=False,

                presidential=False,
            ):
    
    
    # Fixed parameters
    data_lw=1.5
    grid_lw=0.25
    spine_lw=0.25
    
    tick_lw=0.25
    tick_length = 3
    tick_pad = 1

    grid_alpha=0.5
    
    # -- PRE-PROCESSING ------------------------------------------------

    # Load data
    data = load_data(data_dir, data_file, read_csv_kw) 
    julian_days, dates, vals = prepare_data(data, x_column, y_column)

    # Prepare figure
    fig = plt.figure(figsize=(width, width * height_to_width))
    ax = fig.add_axes(axes_box)

    # -- PLOT DATA -----------------------------------------------------

    # Plot data line
    ax.plot(dates, vals, 
            color='k',
            lw=data_lw * size_scale,
            zorder=1000)
    
    # Plot circle on most recent data point (if unnecessary, set circle_size to 0)
    col = zone_colors[0] if vals[-1] > hline_ypos else zone_colors[1]
    ax.plot(dates[-1], vals[-1], 
            marker='o', 
            color='k',
            markersize=circle_size * size_scale, 
            markerfacecolor=col, 
            markeredgewidth=0, 
            zorder=1001)

    # Use data for figure titles/labels
    # TODO: Remove unnecessary parameters
    title_fillers = dict(
        # Last observed value (percentage)
        last_value = vals[-1],
        # Inverse of last observed value (percentage for opponent)
        inv_last_value = 100 - vals[-1],
        # Difference between number of electoral votes and last observed value
        inv_pres_last_value = 538 - vals[-1],
        # Placeholder for political party
        party = '',
    )   
    print("Last value:", title_fillers['last_value'])

    # -- ERROR BARS ----------------------------------------------------

    # Fill the area between the upper and lower error bars
    # TODO: Options: 'esd', '1sigma_lower', '1sigma_upper'?
    err = None
    if yerr_columns is not None:
        # Extract error values from the DataFrame into an array
        err = data[yerr_columns].values

        # If only one error column, assume symmetrical errors
        if len(yerr_columns) == 1:
            # Convert the error array to a 1D array
            err = err.squeeze()
            # Calculate upper and lower bounds for error bars
            err = np.array([vals - err, vals + err]).T

            # Maximize the error bounds such that the range is 1 or err, 
            # whichever is bigger
            range_err = np.ptp(err, axis=1)
            maximized_err = np.maximum(range_err, 1)
            err = np.column_stack((vals - maximized_err / 2, vals + maximized_err / 2))

    yerr_kw = dict(color='grey', alpha=0.3, lw=0)
    if err is not None: 
        ax.fill_between(dates, 
                        err[:, 0], 
                        err[:, 1], 
                        **yerr_kw  
                        )
    
    # -- AXIS LIMITS ---------------------------------------------------

    # Set x-axis limits (dates) in datetime format
    first_day = np.min(julian_days)
    last_day = min(334, np.max(julian_days) * 2)
    x0, x1 = doy2dt(first_day), doy2dt(last_day)
    ax.set_xlim(x0, x1)

    # Set y-axis limits (values)
    if ylim is not None: 
        min_y, max_y = ylim
        y0, y1 = ylim

    else: 
        if err is not None:
            min_y = np.floor(np.min(err[:, 0]))
            max_y = np.ceil(np.max(err[:, 1]))
        else:
            min_y = np.floor(np.min(vals))
            max_y = np.ceil(np.max(vals))
    
        padding = np.round((max_y - min_y) / 5)
        y0 = min_y - padding
        y1 = max_y + padding

        # If the padding is greater than 10,
        # round the limits to nearest multiples of 10 
        if padding > 10:
            y0 = int(np.ceil(y0 / 10.0)) * 10
            y1 = int(np.floor(y1 / 10.0)) * 10
        
    ax.set_ylim(y0, y1)
    ylim = ax.get_ylim()
    print("Y-axis limits:", ylim)
    
    # -- TICK LABELS & PARAMS ------------------------------------------

    # Set x-ticks at month boundaries (first day of each month)
    date_range = pd.date_range(x0, x1)
    tick_dates = date_range[date_range.day == 1]
    tick_dates_dt = np.array([pd.to_datetime(td) for td in tick_dates])
    ax.set_xticks(tick_dates_dt)

    # Set x-tick labels at month centers
    ax.set_xticklabels([]) # Remove x-tick labels
    def get_mid_day(month):
        num_days = calendar.monthrange(year, month)
        return int(np.round(num_days[-1] / 2))
    
    if not thumbnail:
        mid_months = np.array([get_mid_day(d.month) for d in date_range])
        tick_label_dates = date_range[date_range.day == mid_months]
        for td in tick_label_dates:
            loc = pd.to_datetime(td)
            ax.text(x=loc, 
                    y=-1 * xtick_pad * size_scale, # Label below x-axis
                    s=month_names[td.month],
                    color='k',
                    ha='center',
                    va='center',
                    fontsize=font_size,
                    transform=blend(ax.transData, ax.transAxes))

    # Set y-ticks at integer values
    yticks = np.arange(ylim[0], ylim[1] + yticks_interval, yticks_interval)
    # Works for House but is buggy!!
    # if 0 not in yticks:
    #     yticks = np.concatenate(([0], yticks))
    ax.set_yticks(yticks)
    
    # Set tick parameters
    ax.tick_params(labelsize=font_size, 
                   length=tick_length * size_scale, 
                   pad=tick_pad * size_scale, 
                   width=tick_lw * size_scale)
    ax.tick_params(which='minor', length=0) # Hide the minor ticks

    # -- GRID & SPINES -------------------------------------------------

    ax.grid('on', 
            linewidth=grid_lw * size_scale, 
            alpha=grid_alpha)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.setp(ax.spines.values(), 
             linewidth=spine_lw * size_scale)
    
    # -- HORIZONTAL LINE -----------------------------------------------

    if hline_ypos is not None:
        ax.axhline(hline_ypos,
                   color='k',
                   lw=hline_lw * size_scale)
    
    # Shade background of plot regions (if applicable) 
    if shading:
        shading_kw = dict(zorder=0, alpha=0.15, lw=0)
        ax.axhspan(ax.get_ylim()[0], hline_ypos, color=R_color, **shading_kw)
        ax.axhspan(hline_ypos, ax.get_ylim()[1], color=D_color, **shading_kw)

    # -- STRIKE ZONE ---------------------------------------------------

    # Plot target bar (strike zone data)
    if strike_zone_data_file is not None and not thumbnail:
        zorders = [150, 149]

        # Define strike zone pairs and z-orders 
        if strike_zone_house == True: 
            strike_path = strike_zone_data_file
            strike_data = pd.read_csv(strike_path)
            values = np.array(strike_data.columns).astype(float)
            
            na1, s1_lo, s1_hi, s2_lo, s2_hi, na2, na3 = values
            pairs = [s1_lo, s1_hi], [s2_lo, s2_hi]

        else:
            strike_path = os.path.join(data_dir, strike_zone_data_file)
            strike_data = pd.read_csv(strike_path)
            values = np.array(strike_data.columns).astype(float)

            s1_lo, s1_hi, s2_lo, s2_hi = values
            pairs = [s1_lo, s1_hi], [s2_lo, s2_hi]

        # Plot strike zone bars
        # TODO: Change the date to be a constant
        for (lo, hi), col, zo in zip(pairs, strike_colors, zorders):
            print("Strike zone pair:", (lo, hi))
            ax.plot([dt.datetime(2024, 9, 12)] * 2, [lo, hi],
                    lw=2*size_scale,
                    color=col,
                    zorder=zo,
                    alpha=0.7,
                    transform=blend(ax.transData, ax.transData))

    # -- Y-AXES --------------------------------------------------------

    # Y-axis label appearance
    ax.text(x=-ylab_pad * size_scale, 
            y=0.5,
            s=ylab_txt,
            fontsize=font_size,
            rotation=90,
            ha='center',
            va='center',
            transform=ax.transAxes)
    
    # Set y-axis ticks
    # Format tick labels
    if meta_lead_graphic: 
        yticks_lab = []
        for tick in ax.get_yticks():
            plus = '+' if tick != 0 else ''
            party = 'D' if tick > 0 else 'R'
            if tick == 0:
                party = ''

            formatted_tick = f'{party}{plus}{abs(tick):0.0f}%'
            yticks_lab.append(formatted_tick)

        # Set y-axis tick labels for the original and twin axes (excluding thumbnail display)
        if not thumbnail:
            ax.set_yticklabels(yticks_lab)
    
    # Use data to fill text
    # TODO: This is repeat
    last_value = title_fillers['last_value']
    if last_value >= 0:
        title_fillers['party'] = 'D+'
    else:
        title_fillers['party'] = 'R+'
        title_fillers['last_value'] = abs(last_value)
    
    # Add twin y-axis
    if custom_twin_axis:

        # TODO: Check
        # Offset between right and left axis (positive values indicate Republican advantage)
        new_ax_offset = ax_offset

        # Create a twin y-axis (shares same x-axis, limits, ticks)
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks(ax.get_yticks())

        ax.spines['right'].set_visible(True)
        ax.yaxis.tick_right()
        ax2.yaxis.tick_left() # Make ticks more visible

        # Set tick parameters for the twin axis
        ax2.tick_params(labelsize=font_size,
                       length=tick_length * size_scale,
                       pad=tick_pad * size_scale,
                       width=tick_lw * size_scale)
        
        # Format tick labels
        yticks_lab, yticks_lab2 = [], []
        for tick in ax.get_yticks():
            plus = '+' if tick != 0 else ''
            party = 'D' if tick > 0 else 'R'
            if tick == 0:
                party = ''

            formatted_tick = f'{party}{plus}{abs(tick):0.0f}%'
            yticks_lab.append(formatted_tick)

            numerical_tick = float(tick)
            formatted_tick = f'{party}{plus}{abs(numerical_tick-new_ax_offset):0.0f}%'
            yticks_lab2.append(formatted_tick)

        # Set y-axis tick labels for the original and twin axes (excluding thumbnail display)
        if not thumbnail:
            ax.set_yticklabels(yticks_lab)
            ax2.set_yticklabels(yticks_lab2)

            ax.text(x=1 + ylab_pad * size_scale, 
                    y=0.5,
                    s='2024 generic ballot D-R', 
                    fontsize=font_size,
                    rotation=-90,
                    ha='center',
                    va='center',
                    transform=ax.transAxes)
        
        # Use data to fill text
        last_value = title_fillers['last_value']
        last_value = last_value - new_ax_offset
        if last_value >= 0:
            title_fillers['party'] = 'D+'
        else:
            title_fillers['party'] = 'R+'
            title_fillers['last_value'] = abs(last_value)

    # -- SPECIAL ELECTION LINE -----------------------------------------

    if custom_h_line:
        spec_ypos = 4.5
        ax.axhline(spec_ypos,
                color='orange',
                lw=1 * size_scale)
        ax.text(x=0.2,
                y=spec_ypos + 0.5,
                s='Prior from special elections',
                color='orange',
                weight='semibold',
                fontsize=font_size * 0.8,
                alpha=0.9,
                ha='center',
                va='center',
                transform=blend(ax.transAxes, ax.transData))

    # -- FORMATTING ----------------------------------------------------
    
    hline_lab_colors = [zone_colors[0], zone_colors[1]]

    if thumbnail:
        # Hide axes
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        if custom_twin_axis:
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)

        # Set title
        ax.set_title(title_txt.format(**title_fillers),
                y = 0.885,
                fontsize=font_size,
                weight='bold')

        # Add text labels above and below the horizontal line
        # Add formatted horizontal line labels
        # Check hline parameters
        pad_data_units = hline_lab_pad * np.diff(ax.get_ylim())
        txt_kw = dict(fontsize=font_size,
                        ha='center',
                        va='center',
                        transform=blend(ax.transAxes, ax.transData))
        
        # Need to check
        if hline_label is not None:

            ax.text(hline_lab_xpos,
                    (hline_ypos + hline_lab_ypos if hline_lab_ypos is not None else hline_ypos + pad_data_units),
                    hline_label.format(**title_fillers), # index 0?
                    color='k',
                    **txt_kw,)
        
        # Change hline_labels
        # TODO: Check hline_label_units
        # if not custom_twin_axis and hline_labels is not None:
        #     font_size = font_size * 1.5
        #     hlabel_font_size = font_size  ## ADD
        #     rounded_last_value = round(float(title_fillers['last_value']), 1)
        #     if presidential:
        #         if rounded_last_value > 0:
        #             hline_labels[1] = "Biden +" + str(rounded_last_value) + hline_label_units 
        #         else: 
        #             hline_labels[1] = "Trump +" + str(rounded_last_value) + hline_label_units 

        #     # Senate
        #     elif rounded_last_value > 0:
        #         if hline_label_units == "seats":
        #             hline_labels[1] = "D+" + str(round(rounded_last_value/10,1)) + " " + hline_label_units
        #         else:
        #             hline_labels[1] = "D+" + str(rounded_last_value) + hline_label_units 
        #     elif rounded_last_value < 0:
        #         if hline_label_units == "seats":
        #             hline_labels[1] = "R+" + str(round(rounded_last_value/10,1)) + " " + hline_label_units
        #         else:
        #             hline_labels[1] = "Current R+" + str(rounded_last_value) + hline_label_units 
        #     else: hline_labels[1] = "Currently Tie"
        #    
        #  hline_labels[0] = ""

        if hline_labels is not None: 
            # Trump/Rep
            ax.text(hline_lab_xpos,
                    hline_ypos - pad_data_units,
                    hline_labels[0].format(**title_fillers),
                    color=zone_colors[1],
                    **txt_kw,)
            # Biden/Dem
            ax.text(hline_lab_xpos,
                    hline_ypos + pad_data_units,
                    hline_labels[1].format(**title_fillers),
                    color=zone_colors[0],
                    **txt_kw,)
        
    else:

        # Set title
        ax.set_title(title_txt.format(**title_fillers),
                pad=title_pad * size_scale,
                fontsize=font_size,
                weight='bold')
        
        # Horizontal line labels
        pad_data_units = hline_lab_pad * np.diff(ax.get_ylim())
        txt_kw = dict(fontsize=font_size,
                        ha='center',
                        va='center',
                        transform=blend(ax.transAxes, ax.transData))
        # if hline_lab_colors is None:
        #     hline_lab_colors = [col0, col1]
        # Think I can remove HLINE lab colors
        
        if hline_labels is not None: # new line
            # if out_path == "./outputs/thumb_dem_senate_seats_2022": ## CHECK
            #     ax.text(hline_lab_xpos,
            #         hline_ypos-0.1* np.diff(ax.get_ylim()),
            #         hline_labels[0].format(**title_fillers),
            #         color=hline_lab_colors[0],
            #         **txt_kw,)
            # Trump/Rep
            ax.text(hline_lab_xpos,
                    hline_ypos - pad_data_units,
                    hline_labels[0].format(**title_fillers),
                    color=zone_colors[1],
                    **txt_kw,)
            # Biden/Dem
            ax.text(hline_lab_xpos,
                    hline_ypos + pad_data_units,
                    hline_labels[1].format(**title_fillers),
                    color=zone_colors[0],
                    **txt_kw,)

        # Add watermark
        ax.text(watermark_pos[0],
                watermark_pos[1],
                watermark,
                fontsize=font_size-4,
                color='black',
                alpha=0.3,
                style='italic',
                ha='center',
                va='center',
                zorder=200,
                transform=ax.transAxes)
    
    # -- SAVE FIGURE ---------------------------------------------------

    # Calculate dots per inch (dpi) bared on desired width in pixels and plot width 
    dpi = width_pixels_save / width

    # If the output path does not already have the specified output format, append it 
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'

    if thumbnail:
        # Tight bounding box to remove excess whitespace
        plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(out_path, dpi=dpi)

    plt.close(fig)

# == HISTOGRAM =========================================================

def generate_histogram(
                # Data parameters
                data_dir="",
                data_file="",
                vline_xpos = None,
                xvals = None,
                data_factor=100.0,

                # Figure parameters
                width=8, # 9-house
                height_to_width=0.75, # 0.55-house
                width_pixels_save=2000,
                axes_box=[0.1, 0.1, 0.8, 0.8], # [0.19, 0.1, 0.60, 0.75]-house

                # Text parameters
                title_txt = '',
                ylab_txt = '',
                
                ylab_rotation = 0,
                xlab_txt = '',
                vline_labels = None,
                vline_lab_ypos = 0.92,
                last_date_label_pos = (0.01, 0.01),

                watermark='election.princeton.edu',
                watermark_pos=(0.5, 0.5), #[0.77, 0.95]

                # size parameters
                size_scale =1,
                font_size =10,

                # thickness parameters
                bar_width = 0.8,
                grid_lw = 0.25,
                spine_lw = 0.25,
                vline_lw = 1,
                tick_lw = 0.25,

                # color parameters
                col_D = '#1660CE',
                col_R = '#C62535',
                zone_colors = zone_colors,
                vline_color = 'dimgrey',
                grid_alpha = 0.5,
                shading = True,
                color_reverse = False,
                shading_kw = dict(zorder=0, alpha=0.15, lw=0),

                # axes parameters
                ylim = (0, 1.15),
                xlim = (0, 100),

                # tick parameters
                tick_length = 3,
                tick_pad = 1,
                xticks_interval = 1,
                yticks_interval = 1,

                # distance/pad parameters
                title_pad = 5,
                ylab_pad = 0.16,
                xlab_pad = 3,
                xtick_pad = 0.015,
                vline_lab_pad = 0.09,

                # Output parameters
                thumbnail=False,
                out_path="output", # CHANGE
                out_format="png",

                # use external median
                hard_median = False,
            ):

    # -- PRE-PROCESSING ------------------------------------------------

    # Load data
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path, header=None)
    data = data.values.squeeze()
    data = data * data_factor
    if xvals is None:
        xvals = np.arange(len(data))

    # Prepare figure
    fig = plt.figure(figsize=(width, width * height_to_width))
    ax = fig.add_axes(axes_box)

    # -- PLOT DATA -----------------------------------------------------

    print(xvals) 
    print(data) 

    # Plot data bars
    ax.bar(xvals, data,
           color='k',
           width=bar_width,
           zorder=100)
    
    # Use data for figure titles/labels
    def compute_rv_median(p, xs):
        p = p/np.sum(p)
        cum = np.cumsum(p)
        #x1 = xs[np.argwhere(cum <= 0.5).squeeze()[-1]]
        #x2 = xs[np.argwhere(cum >= 0.5).squeeze()[0]]
        #return np.mean([x1, x2])
        return xs[np.argwhere(cum>=0.5).squeeze()[0]]
    
    title_fillers = dict(mean_value = np.sum(data * xvals) / np.sum(data),
                         median_value = compute_rv_median(data, xvals),
                        )
    print(title_fillers)

    ## hard set pres median to matlab median
    def get_estimates(path):
        estimates = None
        with open(path, 'r') as est_file:
            reader = csv.reader(est_file)
            # only one line
            for row in reader:
                estimates = row
                break
        return estimates

    if hard_median:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, '../matlab/outputs/EV_estimates.csv')   
        estimates = get_estimates(path)
        ev_rep = int(estimates[1])
        ev_dem = int(estimates[0])
        title_fillers['median_value'] = ev_dem

    # -- AXIS LIMITS ---------------------------------------------------

    # x axis limits
    if xlim is None:
        thresh = 0.0001 # cuts of tails below this y value
        cs = np.cumsum(data)
        try:
            x0 = np.argwhere(cs<thresh).squeeze()[-1]
        except IndexError:
            x0 = 0
        cs_r = np.cumsum(data[::-1])
        try:
            x1 = len(data) - np.argwhere(cs_r<thresh).squeeze()[-1]
        except IndexError:
            x1 = len(data) - 1
        xlim = (xvals[x0], xvals[x1])
    ax.set_xlim(xlim)
    xlim = ax.get_xlim()

    # y axis limits
    ylim = [ylim[0], np.max(data) * ylim[1]]
    ax.set_ylim(ylim)
    ylim = ax.get_ylim()

    # -- TICK LABELS & PARAMS ------------------------------------------

    # x ticks
    ax.set_xticks(np.arange(xlim[0], xlim[1], xticks_interval))

    # x tick labels

    # y ticks
    ax.set_yticks(np.arange(ylim[0], ylim[1]+yticks_interval, yticks_interval))

    # tick parameters
    ax.tick_params(labelsize=font_size,
                   length=tick_length * size_scale,
                   pad=tick_pad * size_scale,
                   width=tick_lw * size_scale)
    ax.tick_params(which='minor', length=0)

    # -- GRID & SPINES -------------------------------------------------

    ax.grid('on', 
            linewidth=grid_lw * size_scale, 
            alpha=grid_alpha)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.setp(ax.spines.values(), 
             linewidth=spine_lw * size_scale)

    # -- VERTICAL LINE -----------------------------------------------

    # colors for vline labels and shading
    col0, col1 = zone_colors
    if color_reverse:
        col0, col1 = col1, col0

    # vertical line
    if vline_xpos is not None:
        ax.axvline(vline_xpos ,#+ (bar_width / 2 + (1-bar_width) / 2),
                   color=vline_color,
                   lw=vline_lw * size_scale,
                   zorder=100)

        if vline_labels is not None:
            pad_data_units = vline_lab_pad * np.diff(ax.get_xlim())
            # TODO: Prob a better way to do this
            if thumbnail:
                font_size = font_size * 1.5
                vline_font_size = font_size
            else:
                vline_font_size = font_size
            txt_kw = dict(fontsize=vline_font_size,
                          ha='center',
                          va='center',
                          transform=blend(ax.transData, ax.transAxes))
            ax.text(
                    vline_xpos - pad_data_units,
                    vline_lab_ypos,
                    vline_labels[0],
                    color=col0,
                    **txt_kw,)
            ax.text(
                    vline_xpos + pad_data_units,
                    vline_lab_ypos,
                    vline_labels[1],
                    color=col1,
                    **txt_kw,)
    
    # background shading of plot regions
    if shading:
        ax.axvspan(ax.get_xlim()[0], vline_xpos, color=col0, **shading_kw)
        ax.axvspan(vline_xpos, ax.get_xlim()[1], color=col1, **shading_kw)
    
     # -- FORMATTING ----------------------------------------------------

    # text labels
    ax.set_title(title_txt.format(**title_fillers),
                 pad=title_pad * size_scale,
                 fontsize=font_size,
                 weight='bold')

    ax.text(-ylab_pad * size_scale,
            0.5,
            ylab_txt,
            fontsize=font_size,
            rotation=ylab_rotation,
            ha='center',
            va='center',
            transform=ax.transAxes)
    
    ax.set_xlabel(xlab_txt,
                  fontsize=font_size,
                  labelpad=xlab_pad * size_scale,
                 )

    # last date label
    if thumbnail: last_date_label_pos = None
    if last_date_label_pos is not None:
        h_filename = data_file.split('_')[0] + '_estimate_history_2022'
        c_filename = h_filename + '_columns'
        hdata_path = os.path.join(data_dir, h_filename+'.csv')
        cdata_path = os.path.join(data_dir, c_filename+'.csv')
        try:
            hist = pd.read_csv(hdata_path)
            columns = pd.read_csv(cdata_path).columns
            hist.columns = columns
            last_date = doy2dt(np.max(hist.date.values))
            datestr = last_date.strftime('%Y/%m/%d')
            txt = f'Data date: {datestr}'
        except:
            txt = ''
        ax.text(last_date_label_pos[0],
                last_date_label_pos[1],
                txt,
                fontsize=font_size-10,
                color='black',
                alpha=0.3,
                style='italic',
                ha='left',
                va='bottom',
                zorder=200,
                transform=fig.transFigure)

    if thumbnail:
        # Hide axes
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    else:

        # Add watermark
        ax.text(watermark_pos[0],
                watermark_pos[1],
                watermark,
                fontsize=font_size-4,
                color='black',
                alpha=0.3,
                style='italic',
                ha='center',
                va='center',
                zorder=200,
                transform=ax.transAxes)
        
    # -- SAVE FIGURE ---------------------------------------------------

    # Calculate dots per inch (dpi) bared on desired width in pixels and plot width 
    dpi = width_pixels_save / width

    # If the output path does not already have the specified output format, append it 
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'

    if thumbnail:
        # Tight bounding box to remove excess whitespace
        plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(out_path, dpi=dpi)

    plt.close(fig)
