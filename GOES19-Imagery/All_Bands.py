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

# ─── Configuration ─────────────────────────────────────────────────────────────

INCOMING_DIR  = r"D:\teste"
ORGANIZED_DIR = r"D:\GOES-Organized"
DOMAIN        = [-73.9906, -26.5928, -33.7520, 6.2720]
LOGO_LEFT     = r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png"
LOGO_RIGHT    = r"C:\Users\ire0034\Downloads\BaiaDigital\BaiaDigital-02.png"
SLEEP_SECONDS = 600  # 10 minutes

BAND_CMAPS = {
    1: 'Reds',    2: 'Oranges',  3: 'Greens',   4: 'Purples',
    5: 'Blues',   6: 'Greys',    7: 'YlOrBr',   8: 'PuBu',
    9: 'PuRd',   10: 'BuGn',    11: 'Wistia',  12: 'Greys',
    13:'gray',   14: 'YlGn',    15: 'cool',    16: 'hot'
}
BAND_VMIN = {b: (-80 if b >= 7 else 0) for b in BAND_CMAPS}
BAND_VMAX = {b: ( 40 if b >= 7 else 1) for b in BAND_CMAPS}

logging.basicConfig(
    filename='goes_loop.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def add_logo(fig, logo_path, x=0, y=0, scale=0.12, alpha=1.0):
    """
    Add a logo at an offset (x,y) from figure center.
    x,y in [-1..1], where (0,0) is center, x>0 is right, y>0 is up.
    """
    try:
        logo = Image.open(logo_path)
    except Exception as e:
        logging.warning(f"Could not load logo {logo_path}: {e}")
        return

    dpi        = fig.dpi
    fig_w, fig_h = fig.get_size_inches()
    th_in      = fig_h * scale
    tw_in      = th_in * (logo.width / logo.height)
    th_px      = int(th_in * dpi)
    tw_px      = int(tw_in * dpi)
    logo       = logo.resize((tw_px, th_px), Image.LANCZOS)
    arr        = np.array(logo)

    cx = fig_w * dpi / 2
    cy = fig_h * dpi / 2
    xpos = int(cx + x * (fig_w * dpi / 2) - tw_px / 2)
    ypos = int(cy + y * (fig_h * dpi / 2) - th_px / 2)

    fig.figimage(arr, xo=xpos, yo=ypos, alpha=alpha, zorder=1000)


# ─── Main processing loop ─────────────────────────────────────────────────────

while True:
    try:
        for band_folder in sorted(os.listdir(INCOMING_DIR)):
            band_path = os.path.join(INCOMING_DIR, band_folder)
            if not os.path.isdir(band_path):
                continue

            # Extract band number 1–16 from folder name
            m = re.match(r'Band\s*0*([1-9]\d?)', band_folder, re.IGNORECASE)
            if not m:
                logging.warning(f"Unable to parse band number from folder '{band_folder}'; skipping")
                continue
            band_num = int(m.group(1))
            if band_num not in BAND_CMAPS:
                logging.warning(f"Parsed band {band_num} from '{band_folder}' not in 1–16; skipping")
                continue

            cmap = BAND_CMAPS[band_num]
            vmin = BAND_VMIN[band_num]
            vmax = BAND_VMAX[band_num]

            for nc_path in sorted(glob.glob(os.path.join(band_path, '*.nc'))):
                try:
                    # 1) Open and subset with GOES
                    ds = GOES.open_dataset(nc_path)
                    CMI, Lon, Lat = ds.image('CMI', lonlat='corner', domain=DOMAIN)
                    data = CMI.data.astype(float)

                    # 2) Unit conversion
                    if 7 <= band_num <= 16:
                        data -= 273.15
                        units = '°C'
                    else:
                        units = CMI.standard_name or 'unitless'

                    # 3) Build figure
                    fig = plt.figure(figsize=(12, 5.5), dpi=200, constrained_layout=True)
                    gs  = fig.add_gridspec(20, 20)
                    ax  = fig.add_subplot(gs[3:18, 2:18], projection=ccrs.PlateCarree())
                    ax.set_extent([DOMAIN[0] + 360, DOMAIN[1] + 360, DOMAIN[2], DOMAIN[3]],
                                  crs=ccrs.PlateCarree())

                    mesh = ax.pcolormesh(
                        Lon.data, Lat.data, data,
                        cmap=cmap,
                        norm=mcolors.Normalize(vmin=vmin, vmax=vmax)
                    )

                    # 4) Colorbar
                    cax = fig.add_subplot(gs[19, 2:18])
                    cb  = plt.colorbar(mesh, cax=cax, orientation='horizontal', extend='both')
                    cb.set_label(f'{units}', size=9)
                    cb.ax.tick_params(labelsize=8)

                    # 5) Title with BRT timestamp
                    utc_dt = CMI.time_bounds.data[0]
                    if isinstance(utc_dt, np.datetime64):
                        utc_dt = datetime.strptime(str(utc_dt)[:19], '%Y-%m-%dT%H:%M:%S')
                    if not hasattr(utc_dt, 'tzinfo'):
                        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
                    brt   = ZoneInfo('America/Sao_Paulo')
                    br_dt = utc_dt.astimezone(brt)

                    band_id = ds.variable('band_id').data[0]
                    wl      = ds.variable('band_wavelength').data[0]
                    fig.suptitle(
                        f'{ds.attribute("platform_ID")} - Band {band_id:02d}\n'
                        f'{br_dt.strftime("%Y-%m-%d %H:%M BRT")}\n'
                        f'{wl:.1f} μm',
                        y=0.98, fontsize=8, linespacing=1.5
                    )

                    # 6) Map features
                    ax.add_feature(cfeature.NaturalEarthFeature(
                        'cultural', 'admin_0_countries', '50m', facecolor='none'),
                        edgecolor='red', linewidth=0.8
                    )
                    ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
                    ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
                    ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))

                    # 7) Logos
                    add_logo(fig, LOGO_LEFT,  x=-0.4, y=0, scale=0.12)
                    add_logo(fig, LOGO_RIGHT, x= 0.2, y=0, scale=0.12)

                    # 8) Save JPEG
                    out_dir = os.path.join(
                        ORGANIZED_DIR,
                        f"{br_dt.year:04d}",
                        f"{br_dt.month:02d}",
                        f"{br_dt.day:02d}",
                        f"{br_dt.hour:02d}"
                    )
                    os.makedirs(out_dir, exist_ok=True)

                    base      = os.path.splitext(os.path.basename(nc_path))[0]
                    jpeg_path = os.path.join(out_dir, base + '.jpg')
                    fig.savefig(jpeg_path, format='jpeg')
                    plt.close(fig)

                    # 9) Release file handle & move NetCDF
                    del ds
                    gc.collect()
                    os.rename(nc_path, os.path.join(out_dir, os.path.basename(nc_path)))

                    logging.info(f"Processed {nc_path} → {jpeg_path}")

                except Exception:
                    logging.exception(f"Failed processing {nc_path}")

    except Exception:
        logging.exception("Unexpected error in main loop")

    time.sleep(SLEEP_SECONDS)
