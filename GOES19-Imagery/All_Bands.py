# Parte 1: Imports e configurações
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

# Diretórios
INCOMING_DIR  = r"E:\teste1"
ORGANIZED_DIR = r"E:\GOES-Organized"
LOGO_LEFT     = r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png"
LOGO_RIGHT    = r"C:\Users\ire0034\Downloads\BaiaDigital\BaiaDigital-02.png"
DOMAIN        = [-73.9906, -26.5928, -33.7520, 6.2720]
SLEEP_SECONDS = 600

# Logging
logging.basicConfig(filename='goes_loop.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Parte 2: Colormaps exatos para cada banda
def reflectance_cmap(name):
    return mcolors.LinearSegmentedColormap.from_list(name, [
        (0.0, "#000000"), (1.0, "#FFFFFF")
    ])

cmap_band07 = mcolors.LinearSegmentedColormap.from_list(
    "Band07",
    ["#00FFFF", "#000000", "#FFFFFF"],
    N=256,
)

temps_8_10 = [-90, -80, -70, -60, -50, -40, -35, -30, -25, -20, -15, -10, -5, -2.5, 0]
colors_8_10 = [
    "#ffffff", "#00ffff", "#00ff00", "#0000ff", "#dddddd", "#cccccc", "#aaaaaa", "#aa5500",
    "#aa3300", "#550000", "#aa0000", "#ff0000", "#ffcc00", "#ffff00", "#ffff00"
]
norm_8_10 = mcolors.Normalize(vmin=min(temps_8_10), vmax=max(temps_8_10))
cmap_band08 = mcolors.LinearSegmentedColormap.from_list("Band08", list(zip(norm_8_10(temps_8_10), colors_8_10)), N=256)

temps_ir_std = [-90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40]
colors_ir_std = [
    "#ff0000", "#ff8000", "#ffff00", "#00ff00", "#00ffff", "#70a0ff", "#a0c0ff", "#b0d0ff",
    "#d0e0e0", "#c0c0c0", "#a0a0a0", "#808080", "#403030", "#000000"
]
norm_ir_std = mcolors.Normalize(vmin=min(temps_ir_std), vmax=max(temps_ir_std))
cmap_ir_standard = mcolors.LinearSegmentedColormap.from_list("IRStandard", list(zip(norm_ir_std(temps_ir_std), colors_ir_std)), N=256)

temps_15 = temps_ir_std
colors_15 = [
    "#0000ff", "#4b0082", "#00ffff", "#00ff00", "#adff2f", "#ffff00", "#ff8000", "#ff0000",
    "#ff00ff", "#dcdcdc", "#a9a9a9", "#696969", "#404040", "#000000"
]
norm_15 = mcolors.Normalize(vmin=min(temps_15), vmax=max(temps_15))
cmap_band15 = mcolors.LinearSegmentedColormap.from_list("Band15", list(zip(norm_15(temps_15), colors_15)), N=256)

colormaps = {
    1: "Blue Visible", 2: "Red Visible", 3: "Veggie (Near-IR)", 4: "Cirrus (Near-IR)",
    5: "Snow/Ice (Near-IR)", 6: "Cloud Particle Size (Near-IR)", 7: "Shortwave IR",
    8: "Upper-Level Water Vapor", 9: "Mid-Level Water Vapor", 10: "Lower-Level Water Vapor",
    11: "Cloud-Top Phase IR", 12: "Ozone IR", 13: "Clean Longwave IR",
    14: "IR Longwave Window", 15: "Dirty Longwave IR", 16: "CO₂ Longwave IR"
}

vmin_vmax = {
    **{i: (0, 100) for i in range(1, 7)},
    7: (-90, 100),
    **{i: (-90, 0) for i in [8, 9, 10]},
    **{i: (-90, 40) for i in [11, 12, 13, 14, 15, 16]}
}

cmap_lookup = {
    1: reflectance_cmap("Band01"), 2: reflectance_cmap("Band02"), 3: reflectance_cmap("Band03"),
    4: reflectance_cmap("Band04"), 5: reflectance_cmap("Band05"), 6: reflectance_cmap("Band06"),
    7: cmap_band07, 8: cmap_band08, 9: cmap_band08, 10: cmap_band08,
    11: cmap_ir_standard, 12: cmap_ir_standard, 13: cmap_ir_standard,
    14: cmap_ir_standard, 15: cmap_band15, 16: cmap_ir_standard
}

# Parte 3: Função de logo
def add_logo(fig, logo_path, left=True, scale=0.12, alpha=1.0):
    try:
        logo = Image.open(logo_path)
        dpi = fig.dpi
        fig_w, fig_h = fig.get_size_inches()
        th = int(fig_h * scale * dpi)
        tw = int(th * (logo.width / logo.height))
        logo = logo.resize((tw, th), Image.LANCZOS)
        arr = np.array(logo)
        margin = int(fig_w * dpi * 0.02)
        xpos = margin if left else int(fig_w * dpi - tw - margin)
        ypos = int((fig_h * dpi - th) / 2)
        fig.figimage(arr, xo=xpos, yo=ypos, alpha=alpha, zorder=1000)
    except Exception as e:
        logging.warning(f"Logo error: {e}")

# Parte 4: Loop principal
while True:
    try:
        for band_folder in sorted(os.listdir(INCOMING_DIR)):
            band_path = os.path.join(INCOMING_DIR, band_folder)
            if not os.path.isdir(band_path): continue
            m = re.match(r'Band\s*0*([1-9]\d?)', band_folder, re.IGNORECASE)
            if not m: continue
            band_num = int(m.group(1))
            if band_num not in colormaps: continue

            for nc_path in sorted(glob.glob(os.path.join(band_path, '*.nc'))):
                try:
                    ds = GOES.open_dataset(nc_path)
                    CMI, Lon, Lat = ds.image('CMI', lonlat='corner', domain=DOMAIN)
                    data = CMI.data.astype(float)
                    if band_num >= 7:
                        data -= 273.15
                    else:
                        data *= 100

                    cmap = cmap_lookup[band_num]
                    vmin, vmax = vmin_vmax[band_num]

                    fig = plt.figure(figsize=(14, 6), dpi=200, constrained_layout=True)
                    gs = fig.add_gridspec(20, 24)
                    ax = fig.add_subplot(gs[3:18, 4:20], projection=ccrs.PlateCarree())
                    ax.set_extent([DOMAIN[0]+360, DOMAIN[1]+360, DOMAIN[2], DOMAIN[3]])

                    mesh = ax.pcolormesh(Lon.data, Lat.data, data, cmap=cmap,
                                         norm=mcolors.Normalize(vmin=vmin, vmax=vmax))

                    cax = fig.add_subplot(gs[19, 4:20])
                    cb = plt.colorbar(mesh, cax=cax, orientation='horizontal', extend='both')
                    cb.set_label('Brightness Temperature (°C)' if band_num >= 7 else 'Reflectance (%)', size=9)
                    cb.ax.tick_params(labelsize=8)

                    utc_dt = CMI.time_bounds.data[0]
                    if isinstance(utc_dt, np.datetime64):
                        utc_dt = datetime.strptime(str(utc_dt)[:19], '%Y-%m-%dT%H:%M:%S')
                    if not hasattr(utc_dt, 'tzinfo'):
                        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
                    br_dt = utc_dt.astimezone(ZoneInfo('America/Sao_Paulo'))

                    band_id = ds.variable('band_id').data[0]
                    wl = ds.variable('band_wavelength').data[0]
                    product = colormaps.get(band_num, "Unknown")

                    fig.suptitle(
                        f'{ds.attribute("platform_ID")} - Band {band_id:02d}: {product}\n'
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

                    add_logo(fig, LOGO_LEFT, left=True)
                    add_logo(fig, LOGO_RIGHT, left=False)

                    out_dir = os.path.join(ORGANIZED_DIR, band_folder,
                                           f"{br_dt.year:04d}", f"{br_dt.month:02d}", f"{br_dt.day:02d}")
                    os.makedirs(out_dir, exist_ok=True)
                    jpeg_path = os.path.join(out_dir, os.path.splitext(os.path.basename(nc_path))[0] + '.jpg')
                    fig.savefig(jpeg_path, format='jpeg')
                    plt.close(fig)

                    del ds
                    gc.collect()
                    os.rename(nc_path, os.path.join(out_dir, os.path.basename(nc_path)))
                    logging.info(f"Processed {nc_path} → {jpeg_path}")

                except Exception:
                    logging.exception(f"Error processing {nc_path}")
    except Exception:
        logging.exception("Fatal error in main loop")
