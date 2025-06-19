import os
import re
import time
import glob
import logging
import gc
from datetime import datetime, timezone

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from PIL import Image
import GOES

# Diretórios
INCOMING_DIR  = r"E:\incoming\GOES-R-CMI-Imagery"
ORGANIZED_DIR = r"E:\GOES-Organized"
LOGO_LEFT     = r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png"
LOGO_RIGHT    = r"C:\Users\ire0034\Downloads\BaiaDigital\BaiaDigital-03.png"
DOMAIN        = [-73.9906, -26.5928, -33.7520, 6.2720]
CHECK_INTERVAL = 60  # segundos entre varreduras

# Logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

LOG_PATH = os.path.abspath("goes_loop.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    filemode='a'  # ou 'w' se quiser sobrescrever toda vez
)

logging.info("Logger configurado e iniciado com sucesso.")

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

# Parte 3: Função de logo modificada
def add_logo_on_map(ax, logo_path, lon, lat, width_deg=5, anchor='bottom-left'):
    """
    Adiciona um logo georreferenciado ao mapa
    - anchor: 'bottom-left' ou 'top-right' para controle da ancoragem
    - width_deg: largura aproximada do logo em graus de longitude
    """
    try:
        # Carrega o logo com transparência
        logo = plt.imread(logo_path)
        
        # Calcula a proporção de aspecto
        aspect_ratio = logo.shape[1] / logo.shape[0]
        
        # Calcula altura em graus de latitude
        height_deg = width_deg / aspect_ratio
        
        # Calcula a extensão do logo
        left = lon
        right = lon + width_deg
        bottom = lat
        top = lat + height_deg
        
        # Ajusta a ancoragem
        if anchor == 'top-right':
            left = lon - width_deg
            bottom = lat - height_deg
            top = lat
            right = lon
        
        # Exibe o logo como imagem georreferenciada
        ax.imshow(
            logo,
            extent=(left, right, bottom, top),
            transform=ccrs.PlateCarree(),
            alpha=logo[:, :, 3] if logo.shape[2] == 4 else 1,  # Respeita transparência
            origin='upper',
            zorder=10
        )
    except Exception as e:
        logging.warning(f"Erro ao posicionar logo em ({lon}, {lat}): {e}")

# Parte 4: Loop principal modificado
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

                    # Criar figura mais alta para caber melhor o título e colorbar
                    fig = plt.figure(figsize=(12, 9), dpi=200)
                    gs = fig.add_gridspec(nrows=20, ncols=24)

                    # Subplot principal bem centralizado e maior
                    ax = fig.add_subplot(gs[1:17, 2:22], projection=ccrs.PlateCarree())
                    ax.set_extent([DOMAIN[0]+360, DOMAIN[1]+360, DOMAIN[2], DOMAIN[3]])

                    # Colorbar: logo abaixo do gráfico, mesmo comprimento horizontal
                    cbar_ax = fig.add_subplot(gs[18, 2:22])


                    mesh = ax.pcolormesh(Lon.data, Lat.data, data, cmap=cmap,
                                         norm=mcolors.Normalize(vmin=vmin, vmax=vmax))

              

                    cb = plt.colorbar(mesh, cax=cbar_ax, orientation='horizontal', extend='both')

                    cb.set_label('Brightness Temperature (°C)' if band_num >= 7 else 'Reflectance (%)', size=9)
                    cb.ax.tick_params(labelsize=8)


                    utc_dt = CMI.time_bounds.data[0]
                    if isinstance(utc_dt, np.datetime64):
                        utc_dt = datetime.strptime(str(utc_dt)[:19], '%Y-%m-%dT%H:%M:%S')
                    if utc_dt.tzinfo is None or utc_dt.tzinfo.utcoffset(utc_dt) is None:
                        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

                    band_id = ds.variable('band_id').data[0]
                    wl = ds.variable('band_wavelength').data[0]
                    product = colormaps.get(band_num, "Unknown")

                    fig.suptitle(
                    f'{ds.attribute("platform_ID")} - Band {band_id:02d}: {product}\n'
                    f'{utc_dt.strftime("%Y-%m-%d %H:%M UTC")}\n'
                    f'{wl:.1f} µm',
                    y=0.98, fontsize=8, linespacing=1.5
                )


                    ax.add_feature(cfeature.NaturalEarthFeature(
                        'cultural', 'admin_0_countries', '50m', facecolor='none'),
                        edgecolor='white', linewidth=0.8)
                    ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
                    ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
                    ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))

                    # POSICIONAMENTO DOS LOGOS MODIFICADOS
                    # Logo LAMCE - canto inferior esquerdo (ajustado para esquerda)
                    add_logo_on_map(
                        ax, 
                        LOGO_LEFT, 
                        lon=DOMAIN[0] + 1.0,   # levemente mais para a esquerda
                        lat=DOMAIN[2] + 1.5, 
                        width_deg=13.5,
                        anchor='bottom-left'
                    )

                    # Logo Baía Digital - canto superior direito (ajustado para cima/direita e menor)
                    add_logo_on_map(
                        ax, 
                        LOGO_RIGHT, 
                        lon=DOMAIN[1] - 1.0,   # levemente mais para a direita
                        lat=DOMAIN[3] - 0.5,   # levemente mais para cima
                        width_deg=14.5,
                        anchor='top-right'
                    )

                    out_dir = os.path.join(ORGANIZED_DIR, band_folder,
                       f"{utc_dt.year:04d}", f"{utc_dt.month:02d}", f"{utc_dt.day:02d}")
                    timestamp_str = utc_dt.strftime('%Y-%m-%d_%H-%M')

                    jpeg_name = f'{timestamp_str}_Band{band_num:02d}_{os.path.basename(nc_path).replace(".nc", ".jpg")}'
                    jpeg_path = os.path.join(out_dir, jpeg_name)
                    os.makedirs(os.path.dirname(jpeg_path), exist_ok=True)

                    fig.savefig(jpeg_path, format='jpeg', bbox_inches='tight')
                    plt.close(fig)

                    del ds
                    gc.collect()
                    os.rename(nc_path, os.path.join(out_dir, os.path.basename(nc_path)))
                    logging.info(f"Processed {nc_path} → {jpeg_path}")

                except Exception:
                    logging.exception(f"Error processing {nc_path}")
    except Exception:
        logging.exception("Fatal error in main loop")
    try:
        import subprocess
        powershell_script = r"E:\scripts\sync_goes_to_nas.ps1"
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script])
        logging.info("Sincronização com NAS concluída com sucesso.")
    except Exception as e:
        logging.exception(f"Erro ao sincronizar com o NAS: {e}")
    time.sleep(CHECK_INTERVAL)