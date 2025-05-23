
import os
import re
import time
import glob
import logging
import gc
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from PIL import Image
import GOES

# NOAA-style custom colormaps
from matplotlib.colors import LinearSegmentedColormap

band7_cmap = LinearSegmentedColormap.from_list("band7_cmap", [
    (0.00, '#2c2c2c'),
    (0.50, '#ffff00'),
    (1.00, '#ff0000')
])

band13_cmap = LinearSegmentedColormap.from_list("band13_cmap", [
    (0.00, '#ffffff'),
    (0.20, '#ff0000'),
    (0.40, '#ffa500'),
    (0.60, '#00ff00'),
    (0.80, '#0000ff'),
    (1.00, '#000000')
])

from matplotlib.colors import LinearSegmentedColormap

fire_cmap = LinearSegmentedColormap.from_list("noaa_fire", [
    (0.00, "#000000"),
    (0.40, "#555555"),
    (0.70, "#FFFF00"),
    (0.85, "#FF7F00"),
    (1.00, "#FF0000"),
])

wv_cmap = LinearSegmentedColormap.from_list("noaa_water_vapor", [
    (0.00, "#7f0000"),
    (0.20, "#ff8000"),
    (0.40, "#ffff00"),
    (0.60, "#ffffff"),
    (0.80, "#80d4ff"),
    (0.90, "#00bfff"),
    (1.00, "#00ff00"),
])

ir_cmap = LinearSegmentedColormap.from_list("noaa_ir", [
    (0.00, "#ffffff"),
    (0.15, "#ff0000"),
    (0.30, "#ffa500"),
    (0.45, "#00ff00"),
    (0.60, "#00bfff"),
    (0.75, "#808080"),
    (1.00, "#000000"),
])

# Configuration
INCOMING_DIR  = r"D:\teste1"
ORGANIZED_DIR = r"D:\GOES-Organized"
DOMAIN        = [-73.9906, -26.5928, -33.7520, 6.2720]
LOGO_LEFT     = r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png"
LOGO_RIGHT    = r"C:\Users\ire0034\Downloads\BaiaDigital\BaiaDigital-02.png"
SLEEP_SECONDS = 600

logging.basicConfig(
    filename='goes_loop.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def add_logo(fig, logo_path, left=True, scale=0.12, alpha=1.0):
    try:
        logo = Image.open(logo_path)
    except Exception as e:
        logging.warning(f"Could not load logo {logo_path}: {e}")
        return

    dpi        = fig.dpi
    fig_w, fig_h = fig.get_size_inches()
    th = int(fig_h * scale * dpi)
    tw = int(th * (logo.width / logo.height))
    logo = logo.resize((tw, th), Image.LANCZOS)
    arr  = np.array(logo)

    margin = int(fig_w * dpi * 0.02)
    xpos = margin if left else int(fig_w * dpi - tw - margin)
    ypos = int((fig_h * dpi - th) / 2)

    fig.figimage(arr, xo=xpos, yo=ypos, alpha=alpha, zorder=1000)

while True:
    try:
        for band_folder in sorted(os.listdir(INCOMING_DIR)):
            band_path = os.path.join(INCOMING_DIR, band_folder)
            if not os.path.isdir(band_path):
                continue

            m = re.match(r'Band\s*0*([1-9]\d?)', band_folder, re.IGNORECASE)
            if not m:
                logging.warning(f"Unable to parse band number from folder '{band_folder}'; skipping")
                continue
            band_num = int(m.group(1))
            if band_num < 1 or band_num > 16:
                continue

            for nc_path in sorted(glob.glob(os.path.join(band_path, '*.nc'))):
                try:
                    ds = GOES.open_dataset(nc_path)
                    CMI, Lon, Lat = ds.image('CMI', lonlat='corner', domain=DOMAIN)
                    data = CMI.data.astype(float)

                    if 7 <= band_num <= 16:
                        data -= 273.15
                        units = '°C'
                    else:
                        units = CMI.standard_name or 'Reflectance'

                    if band_num == 7:
                        cmap = band7_cmap
                        cmap = fire_cmap
                        vmin, vmax = -80, 70
                    elif band_num in [8, 9, 10]:
                        cmap = wv_cmap
                        vmin, vmax = -90, 10
                    elif band_num == 13:
                        cmap = band13_cmap
                        vmin, vmax = -90, 50
                    elif band_num >= 11:
                        cmap = ir_cmap
                        vmin, vmax = -90, 50
                    else:
                        cmap = 'Greys'
                        vmin, vmax = 0, 1

                    fig = plt.figure(figsize=(14, 6), dpi=200, constrained_layout=True)
                    gs = fig.add_gridspec(20, 24)
                    ax = fig.add_subplot(gs[3:18, 4:20], projection=ccrs.PlateCarree())
                    ax.set_extent([DOMAIN[0]+360, DOMAIN[1]+360, DOMAIN[2], DOMAIN[3]])

                    mesh = ax.pcolormesh(Lon.data, Lat.data, data, cmap=cmap,
                                         norm=mcolors.Normalize(vmin=vmin, vmax=vmax))

                    cax = fig.add_subplot(gs[19, 4:20])
                    cb  = plt.colorbar(mesh, cax=cax, orientation='horizontal', extend='both')
                    cb.set_label(f'{units}', size=9)
                    cb.ax.tick_params(labelsize=8)

                    utc_dt = CMI.time_bounds.data[0]
                    if isinstance(utc_dt, np.datetime64):
                        utc_dt = datetime.strptime(str(utc_dt)[:19], '%Y-%m-%dT%H:%M:%S')
                    if not hasattr(utc_dt, 'tzinfo'):
                        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
                    br_dt = utc_dt.astimezone(ZoneInfo('America/Sao_Paulo'))

                    band_id = ds.variable('band_id').data[0]
                    wl      = ds.variable('band_wavelength').data[0]
                    fig.suptitle(
                        f'{ds.attribute("platform_ID")} - Band {band_id:02d}\n'
                        f'{br_dt.strftime("%Y-%m-%d %H:%M BRT")}\n'
                        f'{wl:.1f} µm',
                        y=0.98, fontsize=8, linespacing=1.5
                    )

                    ax.add_feature(cfeature.NaturalEarthFeature(
                        'cultural', 'admin_0_countries', '50m', facecolor='none'),
                        edgecolor='red', linewidth=0.8)
                    ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
                    ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
                    ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))

                    add_logo(fig, LOGO_LEFT,  left=True,  scale=0.12)
                    add_logo(fig, LOGO_RIGHT, left=False, scale=0.12)

                    out_dir = os.path.join(
                        ORGANIZED_DIR,
                        band_folder,
                        f"{br_dt.year:04d}",
                        f"{br_dt.month:02d}",
                        f"{br_dt.day:02d}"
                    )
                    os.makedirs(out_dir, exist_ok=True)

                    base = os.path.splitext(os.path.basename(nc_path))[0]
                    jpeg_path = os.path.join(out_dir, base + '.jpg')
                    fig.savefig(jpeg_path, format='jpeg')
                    plt.close(fig)

                    del ds
                    gc.collect()
                    os.rename(nc_path, os.path.join(out_dir, os.path.basename(nc_path)))
                    logging.info(f"Processed {nc_path} → {jpeg_path}")

                except Exception:
                    logging.exception(f"Failed processing {nc_path}")
    except Exception:
        logging.exception("Unexpected error in main loop")
    time.sleep(SLEEP_SECONDS)
