import os
import re
import time
import glob
import logging
import gc
from datetime import datetime, timezone
import shutil
import numpy as np
import matplotlib.pyplot as plt
plt.ioff()
import matplotlib.colors as mcolors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from PIL import Image
import GOES
import multiprocessing as mp
import xarray as xr


def check_nas_space(path, min_gb_free=10):
    """
    Verifica o espaço livre no NAS. Retorna True se tiver espaço suficiente.
    """
    try:
        total, used, free = shutil.disk_usage(path)
        free_gb = free / (1024 ** 3)
        if free_gb < min_gb_free:
            logging.warning(f"NAS com pouco espaço livre: {free_gb:.2f} GB disponíveis (mínimo exigido: {min_gb_free} GB).")
            return False
        return True
    except Exception as e:
        logging.error(f"Erro ao verificar espaço do NAS ({path}): {e}")
        return False




# Diretórios
INCOMING_DIR  = r"E:\incoming\GOES-R-CMI-Imagery"
ORGANIZED_DIR = r"E:\GOES-Organized"
LOGO_LEFT_PATH  = r"C:\Users\ire0034\Downloads\AssVisual_LAMCE\assVisual_LAMCE_COR_SemTextoTransparente.png"
LOGO_RIGHT_PATH = r"C:\Users\ire0034\Downloads\BaiaDigital\BaiaDigital-03.png"
logo_left_img = plt.imread(LOGO_LEFT_PATH)
logo_right_img = plt.imread(LOGO_RIGHT_PATH)
DOMAIN        = [-73.9906, -26.5928, -33.7520, 6.2720]
DOMAIN_SUDESTE = [-54.0, -32.0, -27.5, -13.0]
CHECK_INTERVAL = 60  # segundos entre varreduras


def recortar_e_salvar_netcdf(nc_path, destino_dir, timestamp_utc):
    try:
        ds = xr.open_dataset(nc_path)


        if not set(['x', 'y']).issubset(ds.dims) or 'CMI' not in ds.data_vars:
            raise ValueError("Arquivo não possui as dimensões esperadas ou a variável CMI")


        x = ds['x'].values
        y = ds['y'].values
        X, Y = np.meshgrid(x, y)


        H = ds.goes_imager_projection.perspective_point_height
        r_eq = ds.goes_imager_projection.semi_major_axis
        r_pol = ds.goes_imager_projection.semi_minor_axis
        lon_0 = ds.goes_imager_projection.longitude_of_projection_origin


        a = r_eq
        b = r_pol
        lambda_0 = np.deg2rad(lon_0)


        a_sq = a ** 2
        b_sq = b ** 2
        cos_x = np.cos(X)
        cos_y = np.cos(Y)
        sin_x = np.sin(X)
        sin_y = np.sin(Y)


        r1 = (H * cos_x * cos_y) ** 2
        r2 = (cos_y ** 2) * (a_sq * cos_x ** 2 + b_sq * sin_x ** 2)
        r3 = - (H ** 2 - a_sq)
        a_coef = r1 - r2
        b_coef = 2 * H * cos_x * cos_y
        c_coef = r3


        discriminant = b_coef ** 2 - 4 * a_coef * c_coef
        discriminant[discriminant < 0] = np.nan
        r_s = (-b_coef - np.sqrt(discriminant)) / (2 * a_coef)


        s_x = r_s * cos_x * cos_y
        s_y = r_s * sin_x * cos_y
        s_z = r_s * sin_y


        lon = np.rad2deg(lambda_0 + np.arctan(-s_x / (H - s_y)))
        lat = np.rad2deg(np.arctan((a_sq / b_sq) * (s_z / np.sqrt((H - s_x) ** 2 + s_y ** 2))))


        mask = (
            (lon >= DOMAIN[0]) & (lon <= DOMAIN[1]) &
            (lat >= DOMAIN[2]) & (lat <= DOMAIN[3])
        )


        if not np.any(mask):
            raise ValueError("Recorte vazio — nenhum dado no domínio definido.")


        y_idx, x_idx = np.where(mask)
        y_min, y_max = y_idx.min(), y_idx.max()
        x_min, x_max = x_idx.min(), x_idx.max()


        ds_recorte = ds.isel(x=slice(x_min, x_max + 1), y=slice(y_min, y_max + 1))


        os.makedirs(destino_dir, exist_ok=True)
        nome_recorte = f"recorte_{timestamp_utc.strftime('%Y-%m-%d_%H-%M')}_UTC_{os.path.basename(nc_path)}"
        caminho_final = os.path.join(destino_dir, nome_recorte)
        ds_recorte.to_netcdf(caminho_final)


        ds.close()
        ds_recorte.close()
        return caminho_final


    except Exception as e:
        logging.warning(f"Erro ao recortar e salvar NetCDF: {nc_path} → {e}")
        return None
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
def add_logo_on_map(ax, logo_img, lon, lat, width_deg=5, anchor='bottom-left'):
    try:
        aspect_ratio = logo_img.shape[1] / logo_img.shape[0]
        height_deg = width_deg / aspect_ratio
        left = lon
        right = lon + width_deg
        bottom = lat
        top = lat + height_deg


        if anchor == 'top-right':
            left = lon - width_deg
            bottom = lat - height_deg
            top = lat
            right = lon


        ax.imshow(
            logo_img,
            extent=(left, right, bottom, top),
            transform=ccrs.PlateCarree(),
            alpha=logo_img[:, :, 3] if logo_img.shape[2] == 4 else 1,
            origin='upper',
            zorder=10
        )
    except Exception as e:
        logging.warning(f"Erro ao posicionar logo em ({lon}, {lat}): {e}")


def process_nc_file(band_num, band_folder, nc_path):  # <- recebe os 3 argumentos diretamente
    try:
        ds = GOES.open_dataset(nc_path)


        try:
            result = ds.image('CMI', lonlat='corner', domain=DOMAIN)
            if result is None or any(r is None for r in result):
                logging.warning(f"Arquivo {nc_path} não possui dados válidos para CMI/Lon/Lat.")
                return
            CMI, Lon, Lat = result


            if CMI.data is None or np.all(np.isnan(CMI.data)):
                logging.warning(f"CMI inválido ou vazio no arquivo {nc_path}")
                return


            if not hasattr(CMI, 'time_bounds') or CMI.time_bounds.data is None:
                logging.warning(f"Arquivo {nc_path} sem time_bounds definido.")
                return


        except Exception as e:
            logging.warning(f"Erro ao extrair CMI/Lon/Lat de {nc_path}: {e}")
            return


        data = CMI.data.astype(float, copy=False)
        utc_dt = CMI.time_bounds.data[0]
        band_id = ds.variable('band_id').data[0]
        wl = ds.variable('band_wavelength').data[0]
        platform = ds.attribute("platform_ID")
        del ds


        if band_num >= 7:
            data -= 273.15
        else:
            data *= 100


        cmap = cmap_lookup[band_num]
        vmin, vmax = vmin_vmax[band_num]


        product = colormaps.get(band_num, "Unknown")


        # ---------- Gráfico Brasil ----------
        fig = plt.figure(figsize=(12, 9), dpi=200)
        gs = fig.add_gridspec(nrows=20, ncols=24)
        ax = fig.add_subplot(gs[1:17, 2:22], projection=ccrs.PlateCarree())
        ax.set_extent([DOMAIN[0]+360, DOMAIN[1]+360, DOMAIN[2], DOMAIN[3]])
        cbar_ax = fig.add_subplot(gs[18, 2:22])
        mesh = ax.pcolormesh(Lon.data, Lat.data, data, cmap=cmap,
                             norm=mcolors.Normalize(vmin=vmin, vmax=vmax))
        cb = plt.colorbar(mesh, cax=cbar_ax, orientation='horizontal', extend='both')
        cb.set_label('Brightness Temperature (°C)' if band_num >= 7 else 'Reflectance (%)', size=9)
        cb.ax.tick_params(labelsize=8)


        if isinstance(utc_dt, np.datetime64):
            utc_dt = datetime.strptime(str(utc_dt)[:19], '%Y-%m-%dT%H:%M:%S')
        if utc_dt.tzinfo is None or utc_dt.tzinfo.utcoffset(utc_dt) is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)


        fig.suptitle(f'{platform} - Band {band_id:02d}: {product}\n'
                     f'{utc_dt.strftime("%Y-%m-%d %H:%M UTC")}\n{wl:.1f} µm',
                     y=0.98, fontsize=8, linespacing=1.5)


        ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_countries', '50m', facecolor='none'),
                       edgecolor='white', linewidth=0.8)
        ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
        ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
        ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))


        add_logo_on_map(ax, logo_left_img, lon=DOMAIN[0] + 1.0, lat=DOMAIN[2] + 1.5, width_deg=13.5)
        add_logo_on_map(ax, logo_right_img, lon=DOMAIN[1] - 1.0, lat=DOMAIN[3] - 0.5, width_deg=14.5, anchor='top-right')


        out_dir = os.path.join(ORGANIZED_DIR, band_folder, f"{utc_dt.year:04d}", f"{utc_dt.month:02d}", f"{utc_dt.day:02d}")
        timestamp_str = utc_dt.strftime('%Y-%m-%d_%H-%M')
        jpeg_name = f'{timestamp_str}_Band{band_num:02d}_Brasil_{os.path.basename(nc_path).replace(".nc", "")}.jpg'
        jpeg_path = os.path.join(out_dir, 'Brasil', jpeg_name)
        os.makedirs(os.path.dirname(jpeg_path), exist_ok=True)
        fig.savefig(jpeg_path, format='jpeg', bbox_inches='tight')
        fig.clf()
        plt.close(fig)
        gc.collect()


        # ---------- Gráfico Sudeste ----------
        fig = plt.figure(figsize=(12, 9), dpi=200)
        gs = fig.add_gridspec(nrows=20, ncols=24)
        ax = fig.add_subplot(gs[1:17, 2:22], projection=ccrs.PlateCarree())
        ax.set_extent([DOMAIN_SUDESTE[0]+360, DOMAIN_SUDESTE[1]+360, DOMAIN_SUDESTE[2], DOMAIN_SUDESTE[3]])
        cbar_ax = fig.add_subplot(gs[18, 2:22])
        mesh = ax.pcolormesh(Lon.data, Lat.data, data, cmap=cmap,
                             norm=mcolors.Normalize(vmin=vmin, vmax=vmax))
        cb = plt.colorbar(mesh, cax=cbar_ax, orientation='horizontal', extend='both')
        cb.set_label('Brightness Temperature (°C)' if band_num >= 7 else 'Reflectance (%)', size=9)
        cb.ax.tick_params(labelsize=8)


        fig.suptitle(f'{platform} - Band {band_id:02d}: {product}\n'
                     f'{utc_dt.strftime("%Y-%m-%d %H:%M UTC")}\n{wl:.1f} µm',
                     y=0.98, fontsize=8, linespacing=1.5)


        ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_countries', '50m', facecolor='none'),
                       edgecolor='white', linewidth=0.8)
        ax.add_feature(cfeature.STATES, edgecolor='white', linewidth=0.5)
        ax.gridlines(draw_labels=False, linestyle='--', alpha=0.7)
        ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.0f°'))
        ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.0f°'))


        add_logo_on_map(ax, logo_left_img, lon=DOMAIN_SUDESTE[0] + 1.0, lat=DOMAIN_SUDESTE[2] + 1.0, width_deg=4.5)
        add_logo_on_map(ax, logo_right_img, lon=DOMAIN_SUDESTE[1] - 1.0, lat=DOMAIN_SUDESTE[3] - 0.5, width_deg=5.5, anchor='top-right')


        jpeg_sudeste_name = f'{timestamp_str}_Band{band_num:02d}_Sudeste_{os.path.basename(nc_path).replace(".nc", "")}.jpg'
        jpeg_sudeste_dir = os.path.join(out_dir, 'Sudeste')
        os.makedirs(jpeg_sudeste_dir, exist_ok=True)
        jpeg_sudeste_path = os.path.join(jpeg_sudeste_dir, jpeg_sudeste_name)
        fig.savefig(jpeg_sudeste_path, format='jpeg', bbox_inches='tight')
        fig.clf()
        plt.close(fig)
        gc.collect()


        nc_dest = os.path.join(out_dir, "NetCDF")
        os.makedirs(nc_dest, exist_ok=True)
        os.rename(nc_path, os.path.join(nc_dest, os.path.basename(nc_path)))
        recorte_dir = os.path.join(out_dir, "NetCDF")
        caminho_recortado = recortar_e_salvar_netcdf(nc_path, recorte_dir, utc_dt)


        if caminho_recortado:
            os.remove(nc_path)  # Só remove se recorte foi bem-sucedido
        else:
            logging.warning(f"Recorte falhou — mantendo o arquivo original: {nc_path}")


        logging.info(f"Processado NetCDF: {nc_path} → JPEGs: {jpeg_path}, {jpeg_sudeste_path}")


    except Exception as e:
        logging.exception(f"Erro ao processar {nc_path}: {e}")


from datetime import timedelta


def limpar_arquivos_antigos(base_dir, dias_para_manter):
    """
    Remove pastas mais antigas que dias_para_manter a partir do diretório base_dir.
    Espera estrutura base_dir/Banda/AAAA/MM/DD.
    """
    hoje = datetime.utcnow().date()
    limite = hoje - timedelta(days=dias_para_manter)


    for banda in os.listdir(base_dir):
        banda_path = os.path.join(base_dir, banda)
        if not os.path.isdir(banda_path):
            continue


        for ano in os.listdir(banda_path):
            ano_path = os.path.join(banda_path, ano)
            if not ano.isdigit():
                continue


            for mes in os.listdir(ano_path):
                mes_path = os.path.join(ano_path, mes)
                if not mes.isdigit():
                    continue


                for dia in os.listdir(mes_path):
                    dia_path = os.path.join(mes_path, dia)
                    try:
                        data_pasta = datetime.strptime(f"{ano}-{mes}-{dia}", "%Y-%m-%d").date()
                    except ValueError:
                        continue


                    if data_pasta < limite:
                        try:
                            shutil.rmtree(dia_path)
                            logging.info(f"Apagada pasta antiga: {dia_path}")
                        except Exception as e:
                            logging.warning(f"Erro ao apagar {dia_path}: {e}")
if __name__ == "__main__":
    while True:
        logging.info("Iniciando nova varredura de arquivos...")
        try:
            args_list = []
            for band_folder in sorted(os.listdir(INCOMING_DIR)):
                band_path = os.path.join(INCOMING_DIR, band_folder)
                if not os.path.isdir(band_path): continue
                m = re.match(r'Band\s*0*([1-9]\d?)', band_folder, re.IGNORECASE)
                if not m: continue
                band_num = int(m.group(1))
                if band_num not in colormaps: continue


                for nc_path in sorted(glob.glob(os.path.join(band_path, '*.nc'))):
                    args_list.append((band_num, band_folder, nc_path))


            if args_list:
                with mp.Pool(processes=3) as pool:
                    pool.starmap(process_nc_file, args_list)


        except Exception:
            logging.exception("Fatal error in main loop")


        try:
            import subprocess
            powershell_script = r"E:\scripts\sync_goes_to_nas.ps1"
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script],
                check=True,
                timeout=60
            )
            logging.info("Sincronização com NAS concluída com sucesso.")
        except subprocess.TimeoutExpired:
            logging.warning("Sincronização com NAS expirou por timeout.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Falha no PowerShell: código de saída {e.returncode}")
        except Exception as e:
            logging.exception(f"Erro inesperado na sincronização com NAS: {e}")


        try:
            limpar_arquivos_antigos(ORGANIZED_DIR, dias_para_manter=7)
            limpar_arquivos_antigos(r"Z:\GOES_Organized", dias_para_manter=178)
        except Exception as e:
            logging.exception(f"Erro durante limpeza de arquivos antigos: {e}")
       
        time.sleep(CHECK_INTERVAL)

