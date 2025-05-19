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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from PIL import Image  # para redimensionar logos

def add_logo(fig, logo_path, x, y, scale=0.15, alpha=1.0, zorder=3):
    """
    Abre um logo, redimensiona por `scale` e adiciona na figura em (x,y) pixels.
    """
    logo = Image.open(logo_path)
    w, h = logo.size
    logo_small = logo.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    logo_arr = np.array(logo_small)
    fig.figimage(logo_arr, x, y, zorder=zorder, alpha=alpha)

# 1) Dados GOES
path = r"D:\incoming\GOES-R-CMI-Imagery\Band13"
file = "OR_ABI-L2-CMIPF-M6C13_G19_s20251231900210_e20251231909530_c20251231909590.nc"
ds = GOES.open_dataset(os.path.join(path, file))

domain = [-73.9906, -26.5928, -33.7520, 6.2720]
CMI, LonCor, LatCor = ds.image('CMI', lonlat='corner', domain=domain)
CMI_c = CMI.data - 273.15
sat  = ds.attribute('platform_ID')
band = ds.variable('band_id').data[0]
wl   = ds.variable('band_wavelength').data[0]

# 2) Caminhos dos logos
logo_left_path  = r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png"
logo_right_path = r"C:\Users\ire0034\Downloads\Baia Digital\BaiaDigital-02.png"

# 3) Monta figura e eixo do mapa (reserva espaço para logos)
fig = plt.figure(figsize=(12, 4), dpi=200)
ax = fig.add_axes([0.12, 0.12, 0.75, 0.80],
                  projection=ccrs.PlateCarree(360 + (domain[0] + domain[1]) / 2))

# 4) Desenha fronteiras e pcolormesh
ax.add_feature(NaturalEarthFeature('cultural','admin_0_countries','50m',
                                   facecolor='none'),
               edgecolor='red', linewidth=0.5)
img = ax.pcolormesh(
    LonCor.data, LatCor.data, CMI_c,
    cmap=plt.cm.Greys_r,
    norm=mcolors.Normalize(vmin=-70, vmax=0),
    transform=ccrs.PlateCarree()
)

# 5) Colorbar como eixo separado
cbar_ax = fig.add_axes([0.20, 0.05, 0.60, 0.03])
kel = np.arange(180, 331, 10)
cel = kel - 273.15
cb = plt.colorbar(img, cax=cbar_ax, orientation='horizontal',
                  ticks=cel, extend='both')
cb.ax.set_xticklabels([f"{t:.0f}" for t in cel], fontsize=6)
cb.ax.tick_params(length=1.5, direction='out', pad=1.0)
cb.set_label(f'{CMI.standard_name} [°C]', size=6)
cb.outline.set_linewidth(0.5)

# 6) Títulos com horário BRT
utc_dt = CMI.time_bounds.data[0]
if isinstance(utc_dt, np.datetime64):
    utc_dt = utc_dt.astype('datetime64[ms]').astype(datetime)
utc_dt = utc_dt.replace(tzinfo=timezone.utc)
br_dt  = utc_dt.astimezone(ZoneInfo('America/Sao_Paulo'))
ax.set_title(f'{sat} - C{band:02d} [{wl:.1f} μm]', fontsize=8, loc='left')
ax.set_title(f'{br_dt.strftime("%Y/%m/%d %H:%M")} BRT', fontsize=8, loc='right')

# 7) Eixos e grade
dx = 15
xt = np.arange(domain[0], domain[1] + dx, dx)
yt = np.arange(domain[2], domain[3] + dx, dx)
ax.set_xticks(xt, crs=ccrs.PlateCarree())
ax.set_yticks(yt, crs=ccrs.PlateCarree())
ax.xaxis.set_major_formatter(LongitudeFormatter(dateline_direction_label=True))
ax.yaxis.set_major_formatter(LatitudeFormatter())
ax.set_xlabel('Longitude', fontsize=7)
ax.set_ylabel('Latitude', fontsize=7)
ax.tick_params(labelsize=6)
ax.gridlines(xlocs=xt, ylocs=yt, linestyle='--', linewidth=0.25, alpha=0.6)
ax.set_extent([domain[0] + 360, domain[1] + 360, domain[2], domain[3]],
              crs=ccrs.PlateCarree())

# 8) Adiciona logos redimensionados
add_logo(fig, logo_left_path, 10, 300, scale=0.15, alpha=1.0)
add_logo(fig, logo_right_path, 1050, 300, scale=0.15, alpha=1.0)

plt.show()
