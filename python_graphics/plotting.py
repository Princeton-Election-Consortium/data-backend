# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.transforms import blended_transform_factory as blend
import datetime as dt
import calendar
import os
from skimage.transform import rescale
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# constants
mo_names = {
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
election_day = dt.datetime(2020, 11, 3)
year = 2020
doy2dt = lambda d: dt.datetime(year, 1, 1) + dt.timedelta(int(d)-1)

# matplotlib settings
pl.rcParams["font.sans-serif"] = 'Arial'

# common parameters
data_dir = '../matlab/outputs'
data_file = ''
size_scale = 4
font_size = size_scale * 5
width = 8 # inches
height_to_width = 0.8 # ratio
width_pixels_save = 2000
axes_box = [0.18, 0.16, 0.79, 0.75]
col_D = '#1660CE'
col_R = '#C62535'
zone_colors = [col_R, col_D]
watermark = 'election.princeton.edu'
watermark_pos = (0.79, 0.96)
out_path = '.'
out_format = 'png'

# main plotting functions
def generate_line_plot(
                  # data parameters
                  data_dir = data_dir,
                  data_file = data_file,
                  read_csv_kw = {},
                  strike_zone_data_file = None,
                  x_column = 0,
                  y_column = -1,
                  x_minus_yvalues = None,
                  yerr_columns = None,
                  year = year,
                  first_day = None,
                  last_day = 334,
                  hline_ypos = None,

                  # figure parameters
                  width = width,
                  height_to_width = height_to_width,
                  width_pixels_save = width_pixels_save,
                  axes_box = axes_box,

                  # text parameters
                  title_txt = '',
                  ylab_txt = '',
                  ylab_rotation = 0,
                  hline_labels = None,
                  hline_label_units = '',
                  presidential_2020 = False,

                  hline_lab_xpos = 0.85,
                  watermark = watermark,
                  watermark_pos = watermark_pos,

                  # size parameters
                  size_scale = size_scale,
                  font_size = font_size,
                  circle_size = 3,

                  # thickness parameters
                  data_lw = 1,
                  grid_lw = 0.25,
                  spine_lw = 0.25,
                  hline_lw = 1,
                  tick_lw = 0.25,

                  # color parameters
                  col_D = col_D,
                  col_R = col_R,
                  zone_colors = zone_colors,
                  shading = True,
                  color_reverse = False,
                  shading_kw = dict(zorder=0, alpha=0.15, lw=0),
                  yerr_kw = dict(color='grey', alpha=0.3, lw=0),
                  hline_color = 'dimgrey',
                  hline_lab_colors = None,
                  data_line_color = 'k',
                  yticklab_format = False,
                  grid_alpha = 0.5,
                  strike_colors = ['dimgrey', 'lightgrey'],

                  # axes parameters
                  ylim = None,

                  # tick parameters
                  tick_length = 3,
                  tick_pad = 1,
                  yticks_interval = 1,

                  # distance/pad parameters
                  title_pad = 3,
                  ylab_pad = 0.1,
                  xtick_pad = 0.015,
                  hline_lab_pad = 0.06,

                  # output parameters
                  out_path = out_path,
                  out_format = out_format,

                  # other customs
                  plot_customization = False,
                  thumbnail = False,
                ):

    # load data
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path, **read_csv_kw)

    # read in column labels
    fname, ext = os.path.splitext(data_file)
    column_file = fname + '_columns' + ext
    column_path = os.path.join(data_dir, column_file)
    columns = pd.read_csv(column_path).columns
    data.columns = columns
    data.sort_values(by=x_column, inplace=True)

    # convert dates to datetimes
    days = data[x_column].values
    day_of_year = days
    days = np.array([doy2dt(int(d)) for d in days])

    # specify data to plot
    vals = data[y_column].values
    if x_minus_yvalues is not None:
        vals = x_minus_yvalues - vals
    
    # use data to fill title text
    title_fillers = dict(last_value = vals[-1],
                         party = '',
                        )
    
    # change hline_labels for thumbnail versions, set fontsizes 
    # for hline labels
    hlabel_font_size = font_size
    if thumbnail and hline_label_units == "given":
        font_size = font_size * 1.25
        hlabel_font_size = font_size * 1.5
    elif thumbnail and not plot_customization and hline_labels is not None:
        font_size = font_size * 1.25
        hlabel_font_size = font_size * 1.5
        rounded_last_value = round(float(title_fillers['last_value']), 1)
        if presidential_2020:
            if rounded_last_value > 0:
                hline_labels[1] = "Biden +" + str(rounded_last_value) + hline_label_units 
            else: hline_labels[1] = "Trump +" + str(rounded_last_value) + hline_label_units 

        elif rounded_last_value > 0:
            if hline_label_units == "seats":
                hline_labels[1] = "D+" + str(round(rounded_last_value/10,1)) + " " + hline_label_units
            else:
                hline_labels[1] = "D+" + str(rounded_last_value) + hline_label_units 
        elif rounded_last_value < 0:
            if hline_label_units == "seats":
                hline_labels[1] = "R+" + str(round(rounded_last_value/10,1)) + " " + hline_label_units
            else:
                hline_labels[1] = "Current R+" + str(rounded_last_value) + hline_label_units 
        else: hline_labels[1] = "Currently Tie"
        hline_labels[0] = ""

    # prepare figurex
    fig = pl.figure(figsize=(width, width * height_to_width))
    ax = fig.add_axes(axes_box)

    # plot main data line
    ax.plot(days, vals,
            color=data_line_color,
            lw=data_lw * size_scale,
            zorder=1000)

    # plot circle on most recent data point
    col = zone_colors[1] if vals[-1]>0 else zone_colors[0]
    ax.plot(days[-1], vals[-1],
            marker='o',
            markersize=circle_size * size_scale,
            markerfacecolor=col,
            markeredgewidth=0,
            zorder=1001)

    # plot error bars
    err = None
    if yerr_columns is not None:
        err = data[yerr_columns].values
        if len(yerr_columns) == 1:
            # then column with symmetrical value to be added
            # otherwise abs values were assumed
            err = err.squeeze()
            err = np.array([vals - err, vals + err]).T
        if x_minus_yvalues is not None:
            err = x_minus_yvalues - err
            err = err[:,::-1] # keep [lower, upper]
        ax.fill_between(days,
                        err[:,0],
                        err[:,1],
                        **yerr_kw,
                        )

    # x axis limits
    first_day = first_day or np.min(day_of_year)
    last_day = last_day or np.max(day_of_year)
    first_date = doy2dt(first_day)
    last_date = doy2dt(last_day)
    ax.set_xlim(first_date, last_date)

    # y axis limits
    if ylim is None:
        mindat = err[:,0] if err is not None else vals
        maxdat = err[:,1] if err is not None else vals
        minn = np.floor(np.min(mindat))
        maxx = np.ceil(np.max(maxdat))
        pad = np.round((maxx-minn) / 5)
        y0, y1 = minn-pad, maxx+pad
        if pad > 10:
            def r210(val, fx=np.ceil):
                return int(fx(val / 10.0)) * 10
            y0 = r210(y0, np.ceil)
            y1 = r210(y1, np.floor)
        ylim = (y0, y1)
    ax.set_ylim(ylim)
    ylim = ax.get_ylim()

    # x ticks at month boundaries
    date_range = pd.date_range(first_date, last_date)
    tick_dates = date_range[date_range.day == 1]
    tick_dates_dt = np.array([td.to_datetime64() for td in tick_dates])
    ax.set_xticks(tick_dates_dt)
    ax.set_xticklabels([])

    # x tick labels at centers of months
    def get_mid(mo):
        rang = calendar.monthrange(year, mo)
        return int(np.round(rang[-1]/2))
    if not thumbnail:
        mid_months = np.array([get_mid(d.month) for d in date_range])
        tick_label_dates = date_range[date_range.day == mid_months]
        for td in tick_label_dates:
            loc = td.to_datetime64()
            ax.text(loc, -xtick_pad * size_scale,
                    mo_names[td.month],
                    color='k',
                    ha='center',
                    va='center',
                    fontsize=font_size,
                    transform=blend(ax.transData, ax.transAxes))

    # y ticks at integer values
    ax.set_yticks(np.arange(ylim[0], ylim[1]+yticks_interval, yticks_interval))

    if yticklab_format:
        # ytick labels with formatting specifications
        ytls = []
        for t in ax.get_yticks():
            plus = '+' if t != 0 else ''
            ytls.append(f'{plus}{abs(t):0.0f}%')
        ytls[0] = f'R {ytls[0]}'
        ytls[-1] = f'D {ytls[-1]}'
        ax.set_yticklabels(ytls)

        # color ytick labels
        for lab, pos in zip(ax.get_yticklabels(), ax.get_yticks()):
            if pos > 0:
                col = zone_colors[1]
            elif pos < 0:
                col = zone_colors[0]
            else:
                col = 'k'
            lab.set_color(col)

    # tick parameters
    ax.tick_params(labelsize=font_size,
                   length=tick_length * size_scale,
                   pad=tick_pad * size_scale,
                   width=tick_lw * size_scale)
    ax.tick_params(which='minor', length=0)

    # grid and spines
    ax.grid('on', linewidth=grid_lw * size_scale, alpha=grid_alpha)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    pl.setp(ax.spines.values(), linewidth=spine_lw * size_scale)

    # colors for hline labels and shading
    col0, col1 = zone_colors
    if color_reverse:
        col0, col1 = col1, col0

    # horizontal line
    if hline_ypos is not None:
        ax.axhline(hline_ypos,
                   color=hline_color,
                   lw=hline_lw * size_scale)
        
        #***************
        if hline_labels is not None:
            pad_data_units = hline_lab_pad * np.diff(ax.get_ylim())
            txt_kw = dict(fontsize=hlabel_font_size,
                          ha='center',
                          va='center',
                          transform=blend(ax.transAxes, ax.transData))
            if hline_lab_colors is None:
                hline_lab_colors = [col0, col1]
            ax.text(hline_lab_xpos,
                    hline_ypos - pad_data_units,
                    hline_labels[0].format(**title_fillers),
                    color=hline_lab_colors[0],
                    **txt_kw,)
            ax.text(hline_lab_xpos,
                    hline_ypos + pad_data_units,
                    hline_labels[1].format(**title_fillers),
                    color=hline_lab_colors[1],
                    **txt_kw,)

    # background shading of plot regions
    if shading:
        ax.axhspan(ax.get_ylim()[0], hline_ypos, color=col0, **shading_kw)
        ax.axhspan(hline_ypos, ax.get_ylim()[1], color=col1, **shading_kw)

    # target bar
    if strike_zone_data_file is not None:
        strike_path = os.path.join(data_dir, strike_zone_data_file)
        strike_data = pd.read_csv(strike_path)
        values = np.array(strike_data.columns).astype(float)
        if x_minus_yvalues is not None:
            values = x_minus_yvalues - values
        s1_lo, s1_hi, s2_lo, s2_hi = values
        pairs = [s1_lo, s1_hi], [s2_lo, s2_hi]
        zorders = [150, 149]

        for (lo, hi), col, zo in zip(pairs, strike_colors, zorders):
            ax.plot([election_day] * 2,
                    [lo, hi],
                    lw=2*size_scale,
                    color=col,
                    zorder=zo,
                    alpha=0.7,
                    transform=blend(ax.transData, ax.transData))

    # text labels
    if thumbnail:
        ax.set_title(title_txt.format(**title_fillers),
            y = 0.9,
            fontsize=font_size,
            weight='bold')
    else:
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

    # watermark
    if not thumbnail:
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

    # CUSTOM type special plot
    if plot_customization:
        new_ax_offset = 3

        ax2 = ax.twinx()

        ax.spines['right'].set_visible(True)
        ax.yaxis.tick_right()
        ax2.yaxis.tick_left()
        
        spec_ypos = 6
        spec_span = 3
        spec_col = '#f58025'
        ax.axhline(spec_ypos,
                   color=spec_col,
                   lw=0.5 * size_scale)
        ax.axhspan(spec_ypos - spec_span,
                   spec_ypos + spec_span,
                   color=spec_col,
                   alpha=0.15,
                   zorder=0,
                   lw=0,
                   )

        pad_data_units = 0.05 * np.diff(ax.get_ylim())
        ax.text(0.79,
                spec_ypos - pad_data_units,
                'Special elections',
                color=spec_col,
                fontsize=font_size-4,
                alpha=0.8,
                ha='center',
                va='center',
                transform=blend(ax.transAxes, ax.transData))

        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks(ax.get_yticks())
        ax2.tick_params(labelsize=font_size,
                       length=tick_length * size_scale,
                       pad=tick_pad * size_scale,
                       width=tick_lw * size_scale)
        ax2.tick_params(which='minor', length=0)

        # ytick labels with formatting specifications
        ytls, ytls2 = [], []
        def make_str(t):
            plus = '+' if t != 0 else ''
            let = 'D' if t>0 else 'R'
            if t==0: let=''
            return f'{let}{plus}{abs(t):0.0f}%'
        for t in ax.get_yticks():
            ytls.append(make_str(t))
            ytls2.append(make_str(t-new_ax_offset))
        if not thumbnail:
            ax.set_yticklabels(ytls)
            ax2.set_yticklabels(ytls2)

            ax.text(1 + ylab_pad * size_scale,
                    0.5,
                    '2020 generic ballot D-R',
                    fontsize=font_size,
                    rotation=-ylab_rotation,
                    ha='center',
                    va='center',
                    transform=ax.transAxes)
        
        lv = title_fillers['last_value']
        lv = lv - new_ax_offset
        if lv > 0:
            title_fillers['party'] = 'D+'
        elif lv < 0:
            title_fillers['party'] = 'R+'
        title_fillers['last_value'] = lv
        if not thumbnail:
            ax.set_title(title_txt.format(**title_fillers),
                    pad=title_pad * size_scale,
                    fontsize=font_size,
                    weight='bold')
        else:
            ax.set_title(title_txt.format(**title_fillers),
                    y = 0.9,
                    fontsize=font_size,
                    weight='bold')
        
        if thumbnail:
            ax2.get_xaxis().set_visible(False)
            ax2.get_yaxis().set_visible(False)

    if thumbnail:
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    # save out figure
    dpi = width_pixels_save / width
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'
    if thumbnail:
        pl.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        pl.savefig(out_path, dpi=dpi)
    pl.close(fig)

def generate_histogram(
                  # data parameters
                  data_dir = data_dir,
                  data_file = data_file,
                  vline_xpos = None,
                  xvals = None,
                  data_factor=100.0,

                  # figure parameters
                  width = width,
                  height_to_width = height_to_width,
                  width_pixels_save = width_pixels_save,
                  axes_box = axes_box,

                  # text parameters
                  title_txt = '',
                  ylab_txt = '',
                  ylab_rotation = 0,
                  xlab_txt = '',
                  vline_labels = None,
                  vline_lab_ypos = 0.92,
                  last_date_label_pos = (0.01, 0.01),
                  watermark = watermark,
                  watermark_pos = watermark_pos,

                  # size parameters
                  size_scale = size_scale,
                  font_size = font_size,

                  # thickness parameters
                  bar_width = 0.8,
                  grid_lw = 0.25,
                  spine_lw = 0.25,
                  vline_lw = 1,
                  tick_lw = 0.25,

                  # color parameters
                  bar_color = 'black',
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
                  title_pad = 3,
                  ylab_pad = 6,
                  xlab_pad = 3,
                  xtick_pad = 0.015,
                  vline_lab_pad = 0.09,
                  vline_font_size = font_size,

                  # output parameters
                  out_path = out_path,
                  out_format = out_format,

                  # generate a thumbnail image
                  thumbnail = False,
                ):

    # load data
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path)
    data = data.values.squeeze()
    data = data * data_factor
    if xvals is None:
        xvals = np.arange(len(data))
    
    if thumbnail:
        font_size = font_size * 1.25
        vline_font_size = font_size * 1.25

    # use data to fill title text
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

    # prepare figure
    fig = pl.figure(figsize=(width, width * height_to_width))
    ax = fig.add_axes(axes_box)

    # plot main data line
    ax.bar(xvals, data,
           color=bar_color,
           width=bar_width,
           zorder=100)

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

    # grid and spines
    ax.grid('on', linewidth=grid_lw * size_scale, alpha=grid_alpha)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    pl.setp(ax.spines.values(), linewidth=spine_lw * size_scale)
    
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
        h_filename = data_file.split('_')[0] + '_estimate_history'
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

    # watermark
    if not thumbnail:
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
    
    # adjustments if a thumbnail image
    if thumbnail:
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    # save out figure
    dpi = width_pixels_save / width
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'
    if thumbnail:
        pl.savefig(out_path, dpi=dpi, bbox_inches='tight')
    else:
        pl.savefig(out_path, dpi=dpi)
    pl.close(fig)


def generate_dual_line_plot(*args, **kwargs):
    pass
