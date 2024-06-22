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

# ======================================================================
# GLOBAL VARIABLES

YEAR = dt.datetime.now().year
ELECTION_DATE = dt.datetime(2024, 11, 5)
MONTH_NAMES = {
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

DEM_COLOR = '#1660CE'
REP_COLOR = '#C62535'
ZONE_COLORS = [DEM_COLOR, REP_COLOR] # 0th index represents incumbent Presidential party

# Figure
WIDTH = 10 # inches
HEIGHT_TO_WIDTH = 0.9 # ratio
WIDTH_PIXELS_SAVE = 2000
AXES_BOX = [0.16, 0.12, 0.79, 0.76] # Leave space for text
GRID_ALPHA = 0.5

# Visual feel
FONT_SIZE = 24 # SET 
FONT_SIZE_MED = FONT_SIZE * 0.925
TITLE_PAD = 7
GRID_LW = 0.5 # or 0.25
SPINE_LW = 0.5 # or 0.25
LINE_LW = 1 # horizontal or vertical
TICK_LW = 0.5
TICK_LENGTH = 5
TICK_PAD = 1

TXT_KW = dict(ha='center', va='center')
SHADING_KW = dict(zorder=0, alpha=0.15, lw=0)

# Output
OUT_FORMAT = 'png'
WATERMARK = 'election.princeton.edu'
WATERMARK_POS = (0.77, 0.95)

# = LINE PLOTS =========================================================

def doy2dt(d):
    """
    Convert a given day of the year (doy) to a corresponding datetime object (dt).

    Args:
    - d (int): The day of the year to convert.

    Returns:
    - datetime: A datetime object representing the specified day of the year.
    """
    return dt.datetime(YEAR, 1, 1) + dt.timedelta(int(d) - 1)

def get_mid_day(month):
    """
    Gets the middle day of the specified month in the current year.

    Args:
    - month (int): The month for which to find the middle day (1-12).

    Returns:
    - int: The middle day of the specified month.
    """
    num_days = calendar.monthrange(YEAR, month)
    return int(np.round(num_days[-1] / 2))

def load_data(data_dir, data_file, read_csv_kw):
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path, header=None, **read_csv_kw)
    return data 

def prepare_data(data, x_column, y_column):
    """
    Prepares data for plotting.

    Args:
    - data (DataFrame): The input DataFrame containing x and y data.
    - x_column (int): The column index for x-values.
    - y_column (int): The column index for y-values.

    Returns:
    - julian_days (ndarray): Array of Julian days extracted from the DataFrame.
    - dates (ndarray): Array of datetime objects corresponding to the Julian days.
    - vals (ndarray): Array of y-values extracted from the DataFrame.
    """
    # Sort data based on x-values 
    data.sort_values(by=x_column, inplace=True)

    # Extract x-values (Julian days) and convert to datetime objects
    days = data[x_column].values
    julian_days = days
    dates = np.array([doy2dt(d) for d in days])
    
    # Extract y-values (data to plot)
    vals = data[y_column].values
    
    return julian_days, dates, vals

def generate_line_plot(
        # Data
        data_dir="",            # required
        data_file="",           # required
        read_csv_kw={},         # optional, for House polls file
        x_column=None,          # required
        y_column=None,          # required
        yerr_columns=None,      # optional

        # ------------------------------------------------------

        # Lines
        ylim=None,              # optional, recommended
        yticks_interval=1,      # optional, recommended
        hline_ypos=None,        # required

        # Text
        title_txt='',           # required
        ylab_txt='',            # required
        hline_labels=None,      # optional, recommended
        corner_label=None,      # optional, str or list, only in thumbnail

        # Customs               # all optional
        meta_lead_graphic=False,
        strike_zone_data_file=None,
        strike_zone_house=False,
        custom_twin_axis=False,         # for House
        custom_twin_axis_offset=None,   # for House
        custom_twin_axis_label=None,    # for House
        custom_hline=False,
        custom_hline_label=None,
        custom_hline_ypos=None,
        
        # ------------------------------------------------------
        
        # Output
        thumbnail=False,        # optional
        out_path='',            # required

    ):
    
    # -- SET PARAMETERS ------------------------------------------------

    # Specific to line plot
    DATA_LW = 3
    HLINE_LAB_PAD = 0.045
    HLINE_LAB_XPOS = 0.78

    # General labels
    if meta_lead_graphic: 
        yticks_font_size = FONT_SIZE * 0.75   # Smaller tick font
        ylab_pad = 0.15                       # More padding
    else:
        yticks_font_size = FONT_SIZE
        ylab_pad = 0.135
    
    # -- PRE-PROCESSING ------------------------------------------------

    # Read data
    data = load_data(data_dir, data_file, read_csv_kw) 
    julian_days, dates, vals = prepare_data(data, x_column, y_column)

    # Prepare figure
    fig = plt.figure(figsize=(WIDTH, WIDTH * HEIGHT_TO_WIDTH))
    if meta_lead_graphic and strike_zone_house and not thumbnail: # Special case (twin axis)
        axes_box = [0.16, 0.12, 0.69, 0.76]     # Reduce width by 0.10
        ylab_pad = 0.18                         # Even more padding
        ax = fig.add_axes(axes_box)
    else:
        ax = fig.add_axes(AXES_BOX)

    # Prepare grid
    ax.grid('on', 
            linewidth=GRID_LW, 
            alpha=GRID_ALPHA)

    # Prepare spines
    plt.setp(ax.spines.values(), 
             linewidth=SPINE_LW)

    # -- PLOT DATA -----------------------------------------------------

    # Plot data line
    ax.plot(dates, vals, 
            color='black',
            lw=DATA_LW,
            zorder=100)
    
    # Plot circle on most recent data point
    last_value_color = DEM_COLOR if vals[-1] > hline_ypos else REP_COLOR
    ax.plot(dates[-1], vals[-1], 
            marker='o', 
            color='black',
            markersize=6, # Set 
            markerfacecolor=last_value_color, 
            markeredgewidth=0, 
            zorder=101)

    # Use data for figure titles/labels
    title_fillers = dict(
        last_value = vals[-1],              # percentage for incumbent
        inv_last_value = 100 - vals[-1],    # percentage for opponent
        inv_pres_last_value = 538 - vals[-1],
        party = '',
    )   
    # print("Last value:", title_fillers['last_value'])

    # -- ERROR BARS ----------------------------------------------------

    # Fill the area between the upper and lower error bars
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

    if err is not None: 
        ax.fill_between(dates, 
                        err[:, 0], err[:, 1], 
                        color='grey',
                        alpha=0.3, 
                        lw=0)
    
    # -- X-AXIS --------------------------------------------------------

    # Set x-axis limits (dates) in datetime format
    first_day = np.min(julian_days)     # first day with data
    last_day = 335                      # hard-set to November 30
    x0, x1 = doy2dt(first_day), doy2dt(last_day)
    ax.set_xlim(x0, x1)

    # Set x-ticks at month boundaries (first day of each month)
    date_range = pd.date_range(x0, x1)
    tick_dates = date_range[date_range.day == 1]
    ax.set_xticks(np.array([pd.to_datetime(td) for td in tick_dates]))

    # Re-set x-tick labels at month centers (excluding thumbnails)
    if not thumbnail:
        ax.set_xticklabels([]) 
        mid_months = np.array([get_mid_day(d.month) for d in date_range])
        tick_label_dates = date_range[date_range.day == mid_months]
        for td in tick_label_dates:
            ax.text(x=pd.to_datetime(td), 
                    y=-0.045, # trial-and-error
                    s=MONTH_NAMES[td.month],
                    fontsize=FONT_SIZE,
                    color='black',
                    transform=blend(ax.transData, ax.transAxes),
                    **TXT_KW)

    # -- Y-AXIS --------------------------------------------------------
    
    # Set y-axis limits
    if ylim is not None: 
        # If provided, use input values
        min_y, max_y = ylim
        y0, y1 = ylim

    else: 
        # If not provided, use data values as guidelines
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
    
    # Set y-axis limits
    ax.set_ylim(y0, y1)
    ylim = ax.get_ylim()

    # Set y-axis label
    ax.text(x=-ylab_pad, 
            y=0.5, # trial-and-error
            s=ylab_txt,
            fontsize=FONT_SIZE,
            rotation=90,
            transform=ax.transAxes,
            **TXT_KW)

    # Set y-ticks
    ax.set_yticks(np.arange(ylim[0], ylim[1] + yticks_interval, yticks_interval))

    # Format y-axis tick labels (if applicable)
    if meta_lead_graphic: 
        yticks_lab = []
        for tick in ax.get_yticks():
            plus = '+' if tick != 0 else ''
            party = 'D' if tick > 0 else 'R'
            if tick == 0:
                party = ''

            formatted_tick = f'{party}{plus}{abs(tick):0.0f}%'
            yticks_lab.append(formatted_tick)
        ax.set_yticklabels(yticks_lab)
    
    # Set tick parameters (both x and y)
    ax.tick_params(labelsize=yticks_font_size, 
                   length=TICK_LENGTH, 
                   pad=TICK_PAD, 
                   width=TICK_LW)
    ax.tick_params(which='minor', length=0) # hide minor ticks
    
    # -- LINE/SHADING --------------------------------------------------

    # Set horizontal line
    if hline_ypos is not None:
        ax.axhline(hline_ypos,
                   color='dimgrey', 
                   lw=LINE_LW)
        
        if hline_labels is not None: 
            pad_data_units = HLINE_LAB_PAD * np.diff(ax.get_ylim())
            
            # Opponent (2024: Trump/Rep)
            ax.text(x=HLINE_LAB_XPOS,
                    y=hline_ypos - pad_data_units,
                    s=hline_labels[0].format(**title_fillers),
                    fontsize=FONT_SIZE_MED,
                    color=ZONE_COLORS[1],
                    transform=blend(ax.transAxes, ax.transData),
                    **TXT_KW)
            
            # Incumbent (2024: Biden/Dem)
            ax.text(x=HLINE_LAB_XPOS,
                    y=hline_ypos + pad_data_units,
                    s=hline_labels[1].format(**title_fillers),
                    fontsize=FONT_SIZE_MED,
                    color=ZONE_COLORS[0],
                    transform=blend(ax.transAxes, ax.transData),
                    **TXT_KW)
    
    # Shade background of plot regions 
    ax.axhspan(ax.get_ylim()[0], hline_ypos, color=REP_COLOR, **SHADING_KW)
    ax.axhspan(hline_ypos, ax.get_ylim()[1], color=DEM_COLOR, **SHADING_KW)
    
    # -- CUSTOMS ------------------------------------------------------

    # Plot strike zone data (target bar)
    if strike_zone_data_file is not None:
        strike_colors=['#c62535', '#FFFF00']
        zorders = [150, 149]

        # Define strike zone pairs and z-orders 
        if strike_zone_house == True: 
            # House strike zone data file is in different directory
            # as input data file
            strike_path = strike_zone_data_file
            strike_data = pd.read_csv(strike_path)
            values = np.array(strike_data.columns).astype(float)
            
            na1, s1_lo, s1_hi, s2_lo, s2_hi, na2, na3 = values
            pairs = [s1_lo, s1_hi], [s2_lo, s2_hi]

        else:
            # EV strike zone data file is in same directory
            # as input data file
            strike_path = os.path.join(data_dir, strike_zone_data_file)
            strike_data = pd.read_csv(strike_path)
            values = np.array(strike_data.columns).astype(float)

            s1_lo, s1_hi, s2_lo, s2_hi = values
            pairs = [s1_lo, s1_hi], [s2_lo, s2_hi]

        # Plot strike zone bars a bit after Election Day
        for (lo, hi), col, zo in zip(pairs, strike_colors, zorders):
            # print("Strike zone pair:", (lo, hi))
            ax.plot([ELECTION_DATE + dt.timedelta(days=6)] * 2, [lo, hi],
                    lw=2,
                    color=col,
                    zorder=zo,
                    alpha=0.7,
                    transform=blend(ax.transData, ax.transData))

    # Set twin y-axis at offset (same x-axis, limits, ticks)
    if custom_twin_axis:
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks(ax.get_yticks())
        ax2.tick_params(labelsize=yticks_font_size,
                       length=TICK_LENGTH,
                       pad=TICK_PAD,
                       width=TICK_LW)
        ax2.tick_params(which='minor', length=0)

        # Set twin y-axis label (excluding thumbnails)
        if not thumbnail:
            ax2.text(x=1+ylab_pad, 
                    y=0.5, # trial-and-error
                    s=custom_twin_axis_label, 
                    fontsize=FONT_SIZE,
                    rotation=-90,
                    transform=ax.transAxes,
                    **TXT_KW)
        
        # Format twin y-axis tick labels
        yticks_lab2 = []
        for tick in ax.get_yticks():
            if custom_twin_axis_offset == 0 and tick == 0:
                # No party advantage
                plus = ''
                party = ''
            else:
                # Positive values indicate Republican advantage (shifted up)
                plus = '+'
                party = 'D' if float(tick)-custom_twin_axis_offset >= 0 else 'R'

            formatted_tick = f'{party}{plus}{abs(float(tick)-custom_twin_axis_offset):0.0f}%'
            yticks_lab2.append(formatted_tick)
        ax2.set_yticklabels(yticks_lab2)
    
    # Set custom horizontal line
    if custom_hline:
        ax.axhline(custom_hline_ypos,
                   color='orange',
                   lw=LINE_LW)
        ax.text(x=0.39,                   # trial-and-error
                y=custom_hline_ypos + 1,  # trial-and-error
                s=custom_hline_label,
                fontsize=FONT_SIZE_MED,
                color='orange',
                weight='semibold',
                alpha=0.9,
                transform=blend(ax.transAxes, ax.transData),
                **TXT_KW)

    # -- FORMATTING ----------------------------------------------------
    
    # Set title
    last_value = title_fillers['last_value']
    if last_value >= 0:    
        # Incumbent (2024: Biden/Dem) 
        title_fillers['party'] = 'D+'
    else:                  
        # Opponent (2024: Trump/Rep) 
        title_fillers['party'] = 'R+'
        title_fillers['last_value'] = abs(last_value)

    ax.set_title(title_txt.format(**title_fillers),
                 pad=TITLE_PAD,
                 fontsize=FONT_SIZE,
                 weight='bold')    

    # Regular size image with watermark
    if not thumbnail:
        ax.text(x=WATERMARK_POS[0],
                y=WATERMARK_POS[1],
                s=WATERMARK,
                fontsize=FONT_SIZE_MED,
                color='black',
                alpha=0.3,
                style='italic',
                zorder=200,
                transform=ax.transAxes,
                **TXT_KW)
    
    # Thumbnail size image with hidden axes and spines
    else:
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        if custom_twin_axis:
            ax2.get_yaxis().set_visible(False)
            ax2.spines['left'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['top'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)

        # Set corner label in bottom-right (if applicable)
        if corner_label is not None:
            pad_data_units = HLINE_LAB_PAD * np.diff(ax.get_ylim())

            if type(corner_label) == str:       # length one
                ax.text(x=HLINE_LAB_XPOS,
                        y=ylim[0] + 1.5*pad_data_units,
                        s=corner_label.format(**title_fillers), # index 0?
                        color=last_value_color,
                        fontsize=FONT_SIZE_MED,
                        transform=blend(ax.transAxes, ax.transData),
                        **TXT_KW)
                
            elif type(corner_label) == list:    # length two
                # Opponent (2024: Trump/Rep)
                ax.text(x=HLINE_LAB_XPOS,
                        y=ylim[0] + 1.5*pad_data_units,
                        s=corner_label[0].format(**title_fillers),
                        fontsize=FONT_SIZE_MED,
                        color=ZONE_COLORS[1],
                        transform=blend(ax.transAxes, ax.transData),
                        **TXT_KW)
                
                # Incumbent (2024: Biden/Dem)
                ax.text(x=HLINE_LAB_XPOS,
                        y=ylim[0] + 3*pad_data_units,
                        s=corner_label[1].format(**title_fillers),
                        fontsize=FONT_SIZE_MED,
                        color=ZONE_COLORS[0],
                        transform=blend(ax.transAxes, ax.transData),
                        **TXT_KW)
    
    # -- SAVE FIGURE ---------------------------------------------------

    # Calculate dots per inch (dpi)
    dpi = WIDTH_PIXELS_SAVE / WIDTH

    # If the output path does not already have the specified output format, append it 
    if not out_path.endswith(OUT_FORMAT):
        out_path = f'{out_path}.{OUT_FORMAT}'

    if thumbnail:
        # Tight bounding box to remove excess whitespace
        plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(out_path, dpi=dpi)

    # plt.subplots_adjust(left=0.10, bottom=0.15, right=0.85, top=0.85)

    plt.close(fig)

def get_plotting_data(data_dir, data_file, read_csv_kw, x_column, y_column):
    # Read data
    data = load_data(data_dir, data_file, read_csv_kw) 
    julian_days, dates, vals = prepare_data(data, x_column, y_column)

    # Use data for figure titles/labels
    title_fillers = dict(
        last_value = vals[-1],              # percentage for incumbent
        party = '',
    )   
    # print("Last value:", title_fillers['last_value'])

    # # Set title
    last_value = title_fillers['last_value']
    if last_value >= 0:    
        # Incumbent (2024: Biden/Dem) 
        title_fillers['party'] = 'D+'
    else:                  
        # Opponent (2024: Trump/Rep) 
        title_fillers['party'] = 'R+'
        title_fillers['last_value'] = abs(last_value)

    last_val_color = DEM_COLOR if vals[-1] > 0 else REP_COLOR

    return julian_days, dates, vals, title_fillers, last_val_color

def generate_superimposed_line_plot(
        # House
        house_data_dir="",            # required
        house_data_file="",           # required
        house_read_csv_kw={},         # optional, for House polls file
        house_x_column=None,          # required
        house_y_column=None,          # required
        house_color='orange',
        house_label=None,             # required

        # Senate
        senate_data_dir="",            # required
        senate_data_file="",           # required
        senate_x_column=None,          # required
        senate_y_column=None,          # required
        read_csv_kw={},
        senate_color='green',
        senate_label=None,             # required

        # EV 
        ev_data_dir = '../matlab/outputs', 
        ev_data_file=f'EV_estimate_history_{YEAR}.csv',
        ev_x_column=0,             # date
        ev_y_column=13,            # meta-margin
        ev_color='purple',
        ev_label=None,                  # required

        # ------------------------------------------------------

        # Lines
        ylim=None,              # optional, recommended
        yticks_interval=1,      # optional, recommended

        # Text
        title_txt='',           # required
        ylab_txt='',            # required

        # Customs               # all optional
        meta_lead_graphic=False,
        
        # ------------------------------------------------------
        
        # Output
        thumbnail=False,        # optional
        out_path='',            # required

    ):
    
    # -- SET PARAMETERS ------------------------------------------------

    # Specific to line plot
    DATA_LW = 3
    HLINE_LAB_YPOS = 0

    # General labels
    if meta_lead_graphic: 
        yticks_font_size = FONT_SIZE * 0.75   # Smaller tick font
        ylab_pad = 0.15                       # More padding
    else:
        yticks_font_size = FONT_SIZE
        ylab_pad = 0.135
    
    # -- PRE-PROCESSING ------------------------------------------------

    # Prepare figure
    fig = plt.figure(figsize=(WIDTH, WIDTH * HEIGHT_TO_WIDTH))
    ax = fig.add_axes(AXES_BOX)

    # Prepare grid
    ax.grid('on', 
            linewidth=GRID_LW, 
            alpha=GRID_ALPHA)

    # Prepare spines
    plt.setp(ax.spines.values(), 
             linewidth=SPINE_LW)

    # -- PLOT HOUSE DATA -----------------------------------------------
    
    house_plotting_data = get_plotting_data(house_data_dir, house_data_file, house_read_csv_kw, house_x_column, house_y_column)
    house_julian_days = house_plotting_data[0]
    house_dates = house_plotting_data[1]
    house_vals = house_plotting_data[2]
    house_title_fillers = house_plotting_data[3]
    house_last_val_color = house_plotting_data[4]

    # Plot data line
    house_line, = ax.plot(house_dates, house_vals, 
                            color=house_color,
                            lw=DATA_LW,
                            zorder=100,
                            label=house_label.format(**house_title_fillers))
    
    # Plot circle on most recent data point
    ax.plot(house_dates[-1], house_vals[-1], 
            marker='o', 
            markersize=4.5, # Set 
            markerfacecolor=house_last_val_color, 
            markeredgewidth=0, 
            zorder=101)
    
    # -- PLOT SENATE DATA ----------------------------------------------

    senate_plotting_data = get_plotting_data(senate_data_dir, senate_data_file, read_csv_kw, senate_x_column, senate_y_column)
    senate_julian_days = senate_plotting_data[0]
    senate_dates = senate_plotting_data[1]
    senate_vals = senate_plotting_data[2]
    senate_title_fillers = senate_plotting_data[3]
    senate_last_val_color = senate_plotting_data[4]

    # Plot data line
    senate_line, = ax.plot(senate_dates, senate_vals, 
                            color=senate_color,
                            lw=DATA_LW,
                            zorder=100,
                            label=senate_label.format(**senate_title_fillers))
    
    # Plot circle on most recent data point
    ax.plot(senate_dates[-1], senate_vals[-1], 
            marker='o', 
            markersize=4.5, # Set 
            markerfacecolor=senate_last_val_color, 
            markeredgewidth=0, 
            zorder=101)

    # -- PLOT EV DATA ----------------------------------------------

    ev_plotting_data = get_plotting_data(ev_data_dir, ev_data_file, read_csv_kw, ev_x_column, ev_y_column)
    ev_julian_days = ev_plotting_data[0]
    ev_dates = ev_plotting_data[1]
    ev_vals = ev_plotting_data[2]
    ev_title_fillers = ev_plotting_data[3]
    ev_last_val_color = ev_plotting_data[4]

    # Plot data line
    ev_line, = ax.plot(ev_dates, ev_vals, 
                        color=ev_color,
                        lw=DATA_LW,
                        zorder=100,
                        label=ev_label.format(**ev_title_fillers))
    
    # Plot circle on most recent data point
    ax.plot(senate_dates[-1], ev_vals[-1], 
            marker='o', 
            markersize=4.5, # Set 
            markerfacecolor=ev_last_val_color, 
            markeredgewidth=0, 
            zorder=101)

    # Add legend
    ax.legend(handles=[house_line, senate_line, ev_line], 
              loc='lower right',
              fontsize=FONT_SIZE_MED)
    
    # -- X-AXIS --------------------------------------------------------

    # Set x-axis limits (dates) in datetime format
    min_house = np.min(house_julian_days)
    min_senate = np.min(senate_julian_days)
    min_ev = np.min(ev_julian_days)
    first_day = min(min_house, min_senate, min_ev) # first day with any data -OR- all data
    last_day = 335                                 # hard-set to November 30
    x0, x1 = doy2dt(first_day), doy2dt(last_day)
    ax.set_xlim(x0, x1)

    # Set x-ticks at month boundaries (first day of each month)
    date_range = pd.date_range(x0, x1)
    tick_dates = date_range[date_range.day == 1]
    ax.set_xticks(np.array([pd.to_datetime(td) for td in tick_dates]))

    # Re-set x-tick labels at month centers (excluding thumbnails)
    if not thumbnail:
        ax.set_xticklabels([]) 
        mid_months = np.array([get_mid_day(d.month) for d in date_range])
        tick_label_dates = date_range[date_range.day == mid_months]
        for td in tick_label_dates:
            ax.text(x=pd.to_datetime(td), 
                    y=-0.045, # trial-and-error
                    s=MONTH_NAMES[td.month],
                    fontsize=FONT_SIZE,
                    color='black',
                    transform=blend(ax.transData, ax.transAxes),
                    **TXT_KW)

    # -- Y-AXIS --------------------------------------------------------
    
    # Set y-axis limits
    if ylim is not None: 
        y0, y1 = ylim
    
    # Set y-axis limits
    ax.set_ylim(y0, y1)
    ylim = ax.get_ylim()

    # Set y-axis label
    ax.text(x=-ylab_pad, 
            y=0.5, # trial-and-error
            s=ylab_txt,
            fontsize=FONT_SIZE,
            rotation=90,
            transform=ax.transAxes,
            **TXT_KW)

    # Set y-ticks
    ax.set_yticks(np.arange(ylim[0], ylim[1] + yticks_interval, yticks_interval))

    # Format y-axis tick labels (if applicable)
    if meta_lead_graphic: 
        yticks_lab = []
        for tick in ax.get_yticks():
            plus = '+' if tick != 0 else ''
            party = 'D' if tick > 0 else 'R'
            if tick == 0:
                party = ''

            formatted_tick = f'{party}{plus}{abs(tick):0.0f}%'
            yticks_lab.append(formatted_tick)
        ax.set_yticklabels(yticks_lab)
    
    # Set tick parameters (both x and y)
    ax.tick_params(labelsize=yticks_font_size, 
                   length=TICK_LENGTH, 
                   pad=TICK_PAD, 
                   width=TICK_LW)
    ax.tick_params(which='minor', length=0) # hide minor ticks
    
    # -- LINE/SHADING --------------------------------------------------

    # Set horizontal line
    if HLINE_LAB_YPOS is not None:
        ax.axhline(HLINE_LAB_YPOS,
                   color='dimgrey', 
                   lw=LINE_LW)
    
    # Shade background of plot regions 
    ax.axhspan(ax.get_ylim()[0], HLINE_LAB_YPOS, color=REP_COLOR, **SHADING_KW)
    ax.axhspan(HLINE_LAB_YPOS, ax.get_ylim()[1], color=DEM_COLOR, **SHADING_KW)
    
    # -- FORMATTING ----------------------------------------------------

    ax.set_title(title_txt,
                 pad=TITLE_PAD,
                 fontsize=FONT_SIZE,
                 weight='bold')    

    # Regular size image with watermark
    if not thumbnail:
        ax.text(x=WATERMARK_POS[0],
                y=WATERMARK_POS[1],
                s=WATERMARK,
                fontsize=FONT_SIZE_MED,
                color='black',
                alpha=0.3,
                style='italic',
                zorder=200,
                transform=ax.transAxes,
                **TXT_KW)
    
    # Thumbnail size image with hidden axes and spines
    else:
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
    
    # -- SAVE FIGURE ---------------------------------------------------

    # Calculate dots per inch (dpi)
    dpi = WIDTH_PIXELS_SAVE / WIDTH

    # If the output path does not already have the specified output format, append it 
    if not out_path.endswith(OUT_FORMAT):
        out_path = f'{out_path}.{OUT_FORMAT}'

    if thumbnail:
        # Tight bounding box to remove excess whitespace
        plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(out_path, dpi=dpi)

    plt.close(fig)

# == HISTOGRAM =========================================================

def compute_rv_median(p, xs):
        """
        Compute the median value of a probability distribution.

        Args:
        - p (array-like): Probability distribution values.
        - xs (array-like): Corresponding values.

        Returns:
        - float: The median value of the distribution.
        """
        p = p / np.sum(p)  # Normalize the probability distribution
        cum = np.cumsum(p)  # Compute the cumulative sum of probabilities

        # Find the value corresponding to the cumulative probability >= 0.5
        median_value = xs[np.argwhere(cum >= 0.5).squeeze()[0]]

        return median_value

def get_estimates(path):
    """
    Read estimates from a CSV file and return them.

    Args:
    - path (str): The path to the CSV file containing estimates.

    Returns:
    - list or None: A list of estimates read from the CSV file, or None if the file is empty.
    """
    estimates = None
    with open(path, 'r') as est_file:
        reader = csv.reader(est_file)
        # Read only the first row (assuming there's only one line)
        for row in reader:
            estimates = row
            break
    return estimates

def generate_histogram(
        # Data 
        data_dir="",            # required
        data_file="",           # required
        xvals=None,             # optional

        # ------------------------------------------------------

        # Lines
        xlim=(0, 100),          # optional, recommended
        xticks_interval=1,      # optional, recommended
        ylim=(0, 1.15),         # optional, recommended
        yticks_interval=0.5,    # optional, recommended
        vline_xpos=None,        # required
        vline_lab_pad=0.1,      # optional, recommended

        # Text
        title_txt='',           # required
        xlab_txt='',            # required
        ylab_txt='',            # required
        vline_labels=None,      # optional, recommended

        # Customs               # all optional, for EV only?
        hard_median = False, 
        hard_median_data_file=None,

        # ------------------------------------------------------

        # Output
        thumbnail=False,        # optional
        out_path='',            # required

    ):

    # -- SET PARAMETERS ------------------------------------------------

    # Specific to histogram
    BAR_WIDTH = 0.8
    VLINE_LAB_YPOS = 0.87
    
    # General labels
    XLAB_PAD = 5
    YLAB_PAD = 0.135

    # -- PRE-PROCESSING ------------------------------------------------

    # Read data
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path, header=None)
    data = data.values.squeeze() * 100.0 # Scale by set data factor
    if xvals is not None and len(xvals) != len(data):
        raise ValueError("xvals and data arrays must have same length")
    elif xvals is None:
        # xvals = np.arange(len(data))
        xvals = np.arange(43, 43 + len(data)) # TESTING HERE - For some reason, need to add 1 to 42 here

    # Prepare figure
    fig = plt.figure(figsize=(WIDTH, WIDTH * HEIGHT_TO_WIDTH))
    ax = fig.add_axes(AXES_BOX)

    # Prepare grid
    ax.grid('on', 
            linewidth=GRID_LW, 
            alpha=GRID_ALPHA)
    
    # Prepare spines
    plt.setp(ax.spines.values(), 
             linewidth=SPINE_LW)

    # -- PLOT DATA -----------------------------------------------------

    # Plot data bars
    ax.bar(xvals, data,
           color='black',
           width=BAR_WIDTH,
           zorder=100)
    
    # Use data for figure titles/labels
    title_fillers = dict(
        mean_value = np.sum(data * xvals) / np.sum(data),
        # median_value = 100 - compute_rv_median(data, xvals),
        median_value = compute_rv_median(data, xvals),
    )
    # print(title_fillers['median_value'])

    # Get external median
    if hard_median: 
        # EV estimates data file is in same directory
        # as input data file
        hard_median_path = os.path.join(data_dir, hard_median_data_file)   
        estimates = get_estimates(hard_median_path) 
        ev_rep = int(estimates[1])
        ev_dem = int(estimates[0])
        title_fillers['median_value'] = ev_dem

    # -- X-AXIS --------------------------------------------------------

    # Set x-axis limits
    ax.set_xlim(xlim)
    xlim = ax.get_xlim()

    # Set x-axis label
    ax.set_xlabel(xlab_txt,
                  fontsize=FONT_SIZE,
                  labelpad=XLAB_PAD)
    
    # Set x-ticks
    ax.set_xticks(np.arange(xlim[0], xlim[1], xticks_interval))

    # -- Y-AXIS --------------------------------------------------------
    
    # Set y-axis limits
    ylim = [ylim[0], np.max(data) * ylim[1]]
    ax.set_ylim(ylim)
    ylim = ax.get_ylim()

    # Set y-axis label
    ax.text(x=-YLAB_PAD,
            y=0.5, # trial-and-error
            s=ylab_txt,
            fontsize=FONT_SIZE,
            rotation=90,
            transform=ax.transAxes,
            **TXT_KW)

    # Set y-ticks
    ax.set_yticks(np.arange(ylim[0], ylim[1] + yticks_interval, yticks_interval))

    # Set tick parameters (both x and y)
    ax.tick_params(labelsize=FONT_SIZE,
                   length=TICK_LENGTH,
                   pad=TICK_PAD,
                   width=TICK_LW)
    ax.tick_params(which='minor', length=0) # hide minor ticks

    # -- LINE/SHADING --------------------------------------------------

    # Set vertical line
    if vline_xpos is not None:
        ax.axvline(vline_xpos ,
                   color='dimgrey',
                   lw=LINE_LW)

        if vline_labels is not None:
            pad_data_units = vline_lab_pad * np.diff(ax.get_xlim())

            # Opponent (2024: Trump/Rep)
            ax.text(x=vline_xpos - pad_data_units,
                    y=VLINE_LAB_YPOS,
                    s=vline_labels[0],
                    fontsize=FONT_SIZE_MED,
                    color=ZONE_COLORS[1],
                    transform=blend(ax.transData, ax.transAxes),
                    **TXT_KW)
            
            # Incumbent (2024: Biden/Dem)
            ax.text(x=vline_xpos + pad_data_units,
                    y=VLINE_LAB_YPOS,
                    s=vline_labels[1],
                    fontsize=FONT_SIZE_MED,
                    color=ZONE_COLORS[0],
                    transform=blend(ax.transData, ax.transAxes),
                    **TXT_KW)
    
    # Shade background of plot regions
    ax.axvspan(ax.get_xlim()[0], vline_xpos, color=REP_COLOR, **SHADING_KW)
    ax.axvspan(vline_xpos, ax.get_xlim()[1], color=DEM_COLOR, **SHADING_KW)
    
    # -- FORMATTING ---------------------------------------------------

    # Set title
    ax.set_title(title_txt.format(**title_fillers),
                 pad=TITLE_PAD,
                 fontsize=FONT_SIZE,
                 weight='bold')

    # Regular size image with watermark
    if not thumbnail:
        ax.text(x=WATERMARK_POS[0],
                y=WATERMARK_POS[1],
                s=WATERMARK,
                fontsize=FONT_SIZE_MED,
                color='black',
                alpha=0.3,
                style='italic',
                zorder=200,
                transform=ax.transAxes,
                **TXT_KW)
    
    # Thumbnail size image with hidden axes and spines
    else:
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
    # -- SAVE FIGURE ---------------------------------------------------

    # Calculate dots per inch (dpi)
    dpi = WIDTH_PIXELS_SAVE / WIDTH

    # If the output path does not already have the specified output format, append it 
    if not out_path.endswith(OUT_FORMAT):
        out_path = f'{out_path}.{OUT_FORMAT}'

    if thumbnail:
        # Tight bounding box to remove excess whitespace
        plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(out_path, dpi=dpi)

    plt.close(fig)
