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

def add_logo(fig, logo_path, position, padding=0.02, scale=0.12, alpha=1.0):
    """
    Position logos relative to figure edges with dynamic scaling and error checks.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to draw the logo on.
    logo_path : str
        Path to the PNG logo file.
    position : {'left', 'right'}
        Where to place the logo.
    padding : float
        Fraction of figure width/height to pad from the edge.
    scale : float
        Fraction of figure width to scale the logo.
    alpha : float
        Transparency.
    """
    # Try to open the image
    try:
        logo = Image.open(logo_path)
    except Exception as e:
        raise FileNotFoundError(f"Could not load logo at {logo_path!r}: {e}")

    # Compute new size in pixels
    dpi = fig.dpi
    fig_w, fig_h = fig.get_size_inches()
    new_w = fig_w * scale
    new_h = new_w * (logo.height / logo.width)
    logo = logo.resize((int(new_w * dpi), int(new_h * dpi)), Image.LANCZOS)
    logo_arr = np.array(logo)

    pad_x = padding * fig_w * dpi
    pad_y = padding * fig_h * dpi

    if position == 'left':
        # Left edge + padding, vertical center
        xpos = pad_x
        ypos = (fig_h * dpi - logo_arr.shape[0]) / 2
    elif position == 'right':
        # Right edge - logo width - padding, bottom padding
        xpos = fig_w * dpi - logo_arr.shape[1] - pad_x
        ypos = pad_y
    else:
        raise ValueError(f"Position must be 'left' or 'right', got {position!r}")

    fig.figimage(logo_arr, xo=int(xpos), yo=int(ypos), alpha=alpha, zorder=1000)


# 1) Data processing
path = r"D:\incoming\GOES-R-CMI-Imagery\Band13"
file = "OR_ABI-L2-CMIPF-M6C13_G19_s20251231900210_e20251231909530_c20251231909590.nc"
ds = GOES.open_dataset(os.path.join(path, file))

domain = [-73.9906, -26.5928, -33.7520, 6.2720]
CMI, LonCor, LatCor = ds.image('CMI', lonlat='corner', domain=domain)
CMI_c = CMI.data - 273.15

# 2) Figure setup with constrained layout
fig = plt.figure(figsize=(12, 5.5), dpi=200, constrained_layout=True)
gs = fig.add_gridspec(nrows=20, ncols=20)

# 3) Main map axis
ax = fig.add_subplot(gs[3:18, 2:18], projection=ccrs.PlateCarree())
ax.set_extent([domain[0] + 360, domain[1] + 360, domain[2], domain[3]])

# 4) Plot data
mesh = ax.pcolormesh(LonCor.data, LatCor.data, CMI_c,
                     cmap='Greys_r', norm=mcolors.Normalize(vmin=-70, vmax=0))

# 5) Colorbar in dedicated grid space
cax = fig.add_subplot(gs[19, 2:18])
cb = plt.colorbar(mesh, cax=cax, orientation='horizontal', extend='both')
cb.set_label(f'{CMI.standard_name} [°C]', size=9)
cb.ax.tick_params(labelsize=8)

# 6) Titles with automatic datetime conversion
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

# 7) Map decorations
ax.add_feature(NaturalEarthFeature('cultural', 'admin_0_countries', '50m',
                   facecolor='none'), edgecolor='red', linewidth=0.8)
ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))

# 8) Logo positioning
logos = [
    (r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png", 'left'),
    (r"C:\Users\ire0034\Downloads\Baia Digital\BaiaDigital-02.png", 'right')
]

for path, pos in logos:
    add_logo(fig, path, pos, padding=0.03, scale=0.1)

plt.show()
