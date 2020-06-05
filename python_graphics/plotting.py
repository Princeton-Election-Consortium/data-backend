# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.transforms import blended_transform_factory as blend
import datetime as dt
import calendar
import os
from skimage.transform import rescale

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
axes_box = [0.24, 0.16, 0.73, 0.75]
out_path = '.'
out_format = 'png'

# main plotting functions
def generate_line_plot(
                  # data parameters
                  data_dir = data_dir,
                  data_file = data_file,
                  x_column = 0,
                  y_column = -1,
                  yerr_columns = None,
                  year = 2020,
                  first_month = 3,
                  last_month = 11,
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
                  col_D = '#1660CE',
                  col_R = '#C62535',
                  shading = False,
                  shading_reverse = False,
                  shading_kw = dict(zorder=0, alpha=0.15, lw=0),
                  yerr_kw = dict(color='grey', alpha=0.3, lw=0),
                  hline_color = 'dimgrey',
                  data_line_color = 'k',
                  yticklab_format = False,
                  grid_alpha = 0.5,

                  # axes parameters
                  ylim = (-2, 5),

                  # tick parameters
                  tick_length = 3,
                  tick_pad = 1,
                  yticks_interval = 1,

                  # distance/pad parameters
                  title_pad = 3,
                  ylab_pad = 0.1,
                  xtick_pad = 0.015,
                  hline_lab_pad = 12,

                  # output parameters
                  out_path = out_path,
                  out_format = out_format,
                ):

    # load data
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path)

    # convert dates to datetimes
    days = data.iloc[:, x_column].values
    doy2dt = lambda d: dt.datetime(year, 1, 1) + dt.timedelta(int(d))
    days = np.array([doy2dt(int(d)) for d in days])

    # specify data to plot
    vals = data.iloc[:, y_column].values

    # prepare figure
    fig = pl.figure(figsize=(width, width * height_to_width))
    ax = fig.add_axes(axes_box)

    # plot main data line
    ax.plot(days, vals,
            color=data_line_color,
            lw=data_lw * size_scale)

    # plot circle on most recent data point
    col = col_D if vals[-1]>0 else col_R
    ax.plot(days[-1], vals[-1],
            marker='o',
            markersize=circle_size * size_scale,
            markerfacecolor=col,
            markeredgewidth=0)

    # plot error bars
    if yerr_columns is not None:
        err = data.iloc[:, yerr_columns].values
        ax.fill_between(days,
                        err[:,0],
                        err[:,1],
                        **yerr_kw,
                        )

    # x axis limits
    first_month = first_month or np.min([d.month for d in days])
    last_month_end = calendar.monthrange(year, last_month)[-1]
    first_date = dt.datetime(year, first_month, 1)
    last_date = dt.datetime(year, last_month, last_month_end)
    ax.set_xlim(first_date, last_date)

    # y axis limits
    ax.set_ylim(ylim)
    ylim = ax.get_ylim()

    # x ticks at month boundaries
    date_range = pd.date_range(first_date, last_date)
    tick_dates = date_range[date_range.day == 1]
    tick_dates_dt = np.array([td.to_datetime64() for td in tick_dates])
    ax.set_xticks(tick_dates_dt)
    ax.set_xticklabels([])

    # x tick labels at centers of months
    for td in tick_dates:
        loc = td.to_datetime64()
        ax.text(loc + np.timedelta64(15, 'D'), -xtick_pad * size_scale,
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
                col = col_D
            elif pos < 0:
                col = col_R
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

    # line at zero
    if hline_ypos is not None:
        ax.axhline(hline_ypos,
                   color=hline_color,
                   lw=hline_lw * size_scale)
        
        if hline_labels is not None:
            ax.text(0.7,
                    hline_ypos + hline_lab_pad,
                    hline_labels[0],
                    fontsize=font_size,
                    ha='center',
                    va='center',
                    transform=blend(ax.transAxes, ax.transData))
            ax.text(0.7,
                    hline_ypos - hline_lab_pad,
                    hline_labels[1],
                    fontsize=font_size,
                    ha='center',
                    va='center',
                    transform=blend(ax.transAxes, ax.transData))

    # background shading of plot regions
    if shading:
        col0, col1 = col_D, col_R
        if shading_reverse:
            col0, col1 = col1, col0
        ax.axhspan(hline_ypos, ax.get_ylim()[1], color=col0, **shading_kw)
        ax.axhspan(ax.get_ylim()[0], hline_ypos, color=col1, **shading_kw)

    # text labels
    ax.set_title(title_txt,
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

    # save out figure
    dpi = width_pixels_save / width
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'
    pl.savefig(out_path, dpi=dpi)
    pl.close(fig)

def generate_histogram(
                  # data parametersA
                  data_dir = data_dir,
                  data_file = data_file,
                  vline_ypos = None,
                  xvals = None,
                  data_factor=1.0,

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
                  vline_color = 'dimgrey',
                  grid_alpha = 0.5,

                  # axes parameters
                  ylim = (0, 30),
                  xlim = (0, 100),

                  # tick parameters
                  tick_length = 3,
                  tick_pad = 1,
                  xticks_interval = 1,
                  yticks_interval = 1,

                  # distance/pad parameters
                  title_pad = 3,
                  ylab_pad = 6,
                  xlab_pad = 6,
                  xtick_pad = 0.015,
                  vline_lab_pad = 12,

                  # output parameters
                  out_path = out_path,
                  out_format = out_format,
                ):

    # load data
    data_path = os.path.join(data_dir, data_file)
    data = pd.read_csv(data_path)
    data = data.values.squeeze()
    data = data * data_factor
    if xvals is None:
        xvals = np.arange(len(data))

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
        thresh = 1e-1
        cs = np.cumsum(data)
        x0 = np.argwhere(cs<thresh).squeeze()[-1]
        cs_r = np.cumsum(data)
        x1 = len(data) - np.argwhere(cs_r<thresh).squeeze()[-1]
        xlim = (xvals[x0], xvals[x1])
    ax.set_xlim(xlim)
    xlim = ax.get_xlim()

    # y axis limits
    ax.set_ylim(ylim)
    ylim = ax.get_ylim()

    # x ticks
    ax.set_xticks(np.arange(xlim[0], xlim[1]+xticks_interval, xticks_interval))

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

    # line at zero
    if vline_ypos is not None:
        ax.axvline(vline_ypos + (bar_width / 2 + (1-bar_width) / 2),
                   color=vline_color,
                   lw=vline_lw * size_scale,
                   zorder=100)
        if vline_labels is not None:
            ax.text(
                    vline_ypos + vline_lab_pad,
                    0.9,
                    vline_labels[0],
                    fontsize=font_size,
                    ha='center',
                    va='center',
                    transform=blend(ax.transData, ax.transAxes))
            ax.text(
                    vline_ypos - vline_lab_pad,
                    0.9,
                    vline_labels[1],
                    fontsize=font_size,
                    ha='center',
                    va='center',
                    transform=blend(ax.transData, ax.transAxes))
        
    # text labels
    ax.set_title(title_txt,
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

    # save out figure
    dpi = width_pixels_save / width
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'
    pl.savefig(out_path, dpi=dpi)
    pl.close(fig)
