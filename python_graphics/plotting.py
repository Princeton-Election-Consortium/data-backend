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
col_D = '#1660CE'
col_R = '#C62535'
watermark = 'election.princeton.edu'
watermark_pos = (0.79, 0.96)
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
                  shading = True,
                  color_reverse = False,
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
                  hline_lab_pad = 0.06,

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
    
    # use data to fill title text
    title_fillers = dict(last_value = vals[-1]
                        )

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
    err = None
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
    if ylim is None:
        mindat = err[:,0] if err is not None else vals
        maxdat = err[:,1] if err is not None else vals
        minn = np.floor(np.min(mindat))
        maxx = np.ceil(np.max(maxdat))
        pad = np.round((maxx-minn) / 5)
        ylim = (minn - pad,
                maxx + pad)
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

    # colors for hline labels and shading
    col0, col1 = col_R, col_D
    if color_reverse:
        col0, col1 = col1, col0

    # horizontal line
    if hline_ypos is not None:
        ax.axhline(hline_ypos,
                   color=hline_color,
                   lw=hline_lw * size_scale)
        
        if hline_labels is not None:
            pad_data_units = hline_lab_pad * np.diff(ax.get_ylim())
            txt_kw = dict(fontsize=font_size,
                          ha='center',
                          va='center',
                          transform=blend(ax.transAxes, ax.transData))
            ax.text(hline_lab_xpos,
                    hline_ypos - pad_data_units,
                    hline_labels[0],
                    color=col0,
                    **txt_kw,)
            ax.text(hline_lab_xpos,
                    hline_ypos + pad_data_units,
                    hline_labels[1],
                    color=col1,
                    **txt_kw,)

    # background shading of plot regions
    if shading:
        ax.axhspan(ax.get_ylim()[0], hline_ypos, color=col0, **shading_kw)
        ax.axhspan(hline_ypos, ax.get_ylim()[1], color=col1, **shading_kw)

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

    # watermark
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

    # use data to fill title text
    title_fillers = dict(mean_value = np.sum(data * xvals) / np.sum(data),
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
    
    # colors for vline labels and shading
    col0, col1 = col_R, col_D
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
            txt_kw = dict(fontsize=font_size,
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

    # watermark
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

    # save out figure
    dpi = width_pixels_save / width
    if not out_path.endswith(out_format):
        out_path = f'{out_path}.{out_format}'
    pl.savefig(out_path, dpi=dpi)
    pl.close(fig)
