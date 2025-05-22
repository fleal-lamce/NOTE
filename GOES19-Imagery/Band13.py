import os
import GOES
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PIL import Image

def add_logo(fig, logo_path, x=0, y=0, scale=0.1, alpha=1.0):
    """
    Add a logo at a position relative to the center of the figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to draw the logo on.
    logo_path : str
        Path to the PNG logo file.
    x : float
        Horizontal offset from center (0=center, positive=right, negative=left).
    y : float
        Vertical offset from center (0=center, positive=up, negative=down).
    scale : float
        Fraction of figure height to scale the logo height.
    alpha : float
        Transparency of the logo.
    """
    from PIL import Image
    import numpy as np

    # Load and resize logo
    logo = Image.open(logo_path)
    dpi = fig.dpi
    fig_w, fig_h = fig.get_size_inches()
    target_h_px = int(fig_h * scale * dpi)
    target_w_px = int(target_h_px * (logo.width / logo.height))
    logo = logo.resize((target_w_px, target_h_px), Image.LANCZOS)
    logo_arr = np.array(logo)

    # Convert center-relative x, y (range -1 to 1) to pixel position
    center_x = fig_w * dpi / 2
    center_y = fig_h * dpi / 2

    xpos = int(center_x + x * fig_w * dpi - logo_arr.shape[1] / 2)
    ypos = int(center_y - y * fig_h * dpi - logo_arr.shape[0] / 2)

    fig.figimage(logo_arr, xo=xpos, yo=ypos, alpha=alpha, zorder=1000)


# Data processing
path = r"D:\incoming\GOES-R-CMI-Imagery\Band13"
file = "OR_ABI-L2-CMIPF-M6C13_G19_s20251231900210_e20251231909530_c20251231909590.nc"
ds = GOES.open_dataset(os.path.join(path, file))

domain = [-73.9906, -26.5928, -33.7520, 6.2720]
CMI, LonCor, LatCor = ds.image('CMI', lonlat='corner', domain=domain)
CMI_c = CMI.data - 273.15

# Figure setup
fig = plt.figure(figsize=(12, 5.5), dpi=200, constrained_layout=True)
gs = fig.add_gridspec(nrows=20, ncols=20)

# Main map axis
ax = fig.add_subplot(gs[3:18, 2:18], projection=ccrs.PlateCarree())
ax.set_extent([domain[0] + 360, domain[1] + 360, domain[2], domain[3]])

# Plot data
mesh = ax.pcolormesh(LonCor.data, LatCor.data, CMI_c,
                     cmap='Greys_r', norm=mcolors.Normalize(vmin=-70, vmax=0))

# Colorbar
cax = fig.add_subplot(gs[19, 2:18])
cb = plt.colorbar(mesh, cax=cax, orientation='horizontal', extend='both')
cb.set_label(f'{CMI.standard_name} [°C]', size=9)
cb.ax.tick_params(labelsize=8)

# Titles
utc_dt = CMI.time_bounds.data[0]
if isinstance(utc_dt, np.datetime64):
    utc_dt = datetime.strptime(str(utc_dt)[:19], '%Y-%m-%dT%H:%M:%S')
if not isinstance(utc_dt, datetime):
    utc_dt = datetime.utcfromtimestamp(utc_dt.astype('datetime64[s]').astype(int))
utc_dt = utc_dt.replace(tzinfo=timezone.utc)
br_dt = utc_dt.astimezone(ZoneInfo('America/Sao_Paulo'))

fig.suptitle(
    f'{ds.attribute("platform_ID")} - Band {ds.variable("band_id").data[0]:02d}\n'
    f'{br_dt.strftime("%Y-%m-%d %H:%M BRT")}\n'
    f'{ds.variable("band_wavelength").data[0]:.1f} μm',
    y=0.98, fontsize=8, linespacing=1.5
)

# Map features
ax.add_feature(NaturalEarthFeature('cultural', 'admin_0_countries', '50m',
                   facecolor='none'), edgecolor='red', linewidth=0.8)
ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))

# Logos
add_logo(
    fig,
    r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png",
    x=-0.4, y=0, scale=0.12
)
add_logo(
    fig,
    r"C:\Users\ire0034\Downloads\BaiaDigital\BaiaDigital-02.png",
    x=0.2, y=0, scale=0.12
)

plt.show()