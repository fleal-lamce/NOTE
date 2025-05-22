import os
import time
import glob
import logging
from datetime import datetime, timezone, timedelta

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset

# Set up logging
logging.basicConfig(
    filename='goes_loop.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def calculate_lat_lon(nc):
    """
    Robust GOES ABI fixed-grid to lat/lon conversion.
    Filters out invalid discriminant values before sqrt to avoid warnings.
    """
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    proj = nc.variables['goes_imager_projection']
    lon0 = proj.longitude_of_projection_origin
    H = proj.perspective_point_height + proj.semi_major_axis
    r_eq = proj.semi_major_axis
    r_pol = proj.semi_minor_axis

    xx, yy = np.meshgrid(x, y)
    lambda0 = np.deg2rad(lon0)

    a = (np.sin(xx)**2 +
         (np.cos(xx)**2) * (np.cos(yy)**2 + (r_eq/r_pol)**2 * np.sin(yy)**2))
    b = -2 * H * np.cos(xx) * np.cos(yy)
    c = H**2 - r_eq**2

    discriminant = b**2 - 4*a*c

    # Prepare array for slant range (rs), mask invalid discriminant
    rs = np.full_like(xx, np.nan)
    mask = discriminant > 0
    rs[mask] = (-b[mask] - np.sqrt(discriminant[mask])) / (2 * a[mask])

    # Satellite-centric coordinates
    sx =  rs * np.cos(xx) * np.cos(yy)
    sy = -rs * np.sin(xx)
    sz =  rs * np.cos(xx) * np.sin(yy)

    # Prepare output arrays
    lat = np.full_like(xx, np.nan)
    lon = np.full_like(xx, np.nan)
    valid = ~np.isnan(rs)

    # Compute geographic lat/lon only where valid
    lat[valid] = np.rad2deg(
        np.arctan((r_eq**2 / r_pol**2) *
                  sz[valid] / np.sqrt((H - sx[valid])**2 + sy[valid]**2))
    )
    lon[valid] = np.rad2deg(
        lambda0 - np.arctan2(sy[valid], (H - sx[valid]))
    )

    return lat, lon

def add_logo(fig, logo_path, position="lower right", zoom=0.1):
    """ Places a logo on the figure at one of the four corners. """
    try:
        logo_img = plt.imread(logo_path)
    except FileNotFoundError:
        logging.warning(f"Logo {logo_path} not found.")
        return

    # Define axes for logo depending on requested corner
    if position == "upper left":
        ax_l = fig.add_axes([0.01, 0.85, zoom, zoom], anchor='NW', zorder=10)
    elif position == "upper right":
        ax_l = fig.add_axes([0.95-zoom, 0.85, zoom, zoom], anchor='NE', zorder=10)
    elif position == "lower left":
        ax_l = fig.add_axes([0.01, 0.01, zoom, zoom], anchor='SW', zorder=10)
    else:  # lower right
        ax_l = fig.add_axes([0.95-zoom, 0.01, zoom, zoom], anchor='SE', zorder=10)

    ax_l.imshow(logo_img)
    ax_l.axis('off')

# Geographic extent and colormap per band
extent = [-73.9906, -26.5928, -33.7520, 6.2720]
band_cmaps = {
    1: 'Reds',   2: 'Oranges', 3: 'Greens',  4: 'Purples',
    5: 'Blues',  6: 'Greys',   7: 'YlOrBr',  8: 'PuBu',
    9: 'PuRd',  10: 'BuGn',   11: 'Wistia', 12: 'Greys',
    13:'gray',  14: 'YlGn',   15: 'cool',   16: 'hot'
}

# Infinite processing loop
while True:
    incoming_base = r"D:\teste"
    organized_base = r"D:\GOES-Organized"

    for band_folder in sorted(os.listdir(incoming_base)):
        band_path = os.path.join(incoming_base, band_folder)
        if not os.path.isdir(band_path):
            continue

        # Extract numeric band number, e.g. "Band13" → 13
        band_num = int(''.join(filter(str.isdigit, band_folder)))

        for file_path in sorted(glob.glob(os.path.join(band_path, "*.nc"))):
            try:
                nc = Dataset(file_path)

                # Platform & time metadata
                platform = getattr(nc, 'platform_ID',
                                   nc.getncattr('platform_ID') if 'platform_ID' in nc.ncattrs() else 'G16')
                platform_str = f"GOES-{platform[1:]}" if platform.startswith('G') else platform

                # Lat/Lon calculation (now robust)
                lat, lon = calculate_lat_lon(nc)

                # Domain mask
                in_domain = (lat >= extent[2]) & (lat <= extent[3]) & \
                            (lon >= extent[0]) & (lon <= extent[1])
                if not np.any(in_domain):
                    logging.warning(f"No data in domain for {file_path}")
                    nc.close()
                    continue

                # Read CMI variable for this band
                var_name = f"CMI_C{band_num:02d}"
                if var_name not in nc.variables:
                    logging.error(f"{var_name} missing in {file_path}")
                    nc.close()
                    continue
                data = nc.variables[var_name][:].astype(float)

                # Kelvin → Celsius for emissive bands
                if 7 <= band_num <= 16:
                    data -= 273.15
                    units = "°C"
                else:
                    units = "Reflectance"

                # Mask outside domain
                data = np.ma.array(data, mask=~in_domain)

                # Prepare timestamp for title & folder
                tstr = getattr(nc, 'time_coverage_end', None)
                if tstr:
                    dt_utc = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S.%fZ')
                else:
                    dt_utc = datetime.utcnow()
                brt = timezone(timedelta(hours=-3))
                dt_brt = dt_utc.replace(tzinfo=timezone.utc).astimezone(brt)
                time_label = dt_brt.strftime('%Y-%m-%d %H:%M:%S') + " BRT"

                # Plot
                fig = plt.figure(figsize=(8,8))
                ax = plt.axes(projection=ccrs.PlateCarree())
                ax.set_extent(extent, crs=ccrs.PlateCarree())
                ax.add_feature(cfeature.BORDERS, edgecolor='red')
                ax.add_feature(cfeature.COASTLINE)
                ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

                cmap = band_cmaps.get(band_num, 'viridis')
                img = ax.imshow(data, origin='upper', cmap=cmap,
                                extent=extent, transform=ccrs.PlateCarree(),
                                interpolation='nearest')

                wavelength = {
                    1:"0.47 μm",2:"0.64 μm",3:"0.86 μm",4:"1.378 μm",
                    5:"1.61 μm",6:"2.25 μm",7:"3.9 μm", 8:"6.185 μm",
                    9:"6.95 μm",10:"7.34 μm",11:"8.5 μm",12:"9.61 μm",
                    13:"10.35 μm",14:"11.2 μm",15:"12.3 μm",16:"13.3 μm"
                }.get(band_num,"")

                ax.set_title(f"{platform_str} - {time_label} - Band {band_num} ({wavelength})",
                             fontsize=12)

                cb = plt.colorbar(img, ax=ax, orientation='horizontal', pad=0.05)
                cb.set_label(units)

                # Add your two logos
                add_logo(fig, r"path\to\logo1.png", position='lower left', zoom=0.15)
                add_logo(fig, r"path\to\logo2.png", position='lower right', zoom=0.15)

                # Save outputs
                out_dir = os.path.join(
                    organized_base,
                    f"{dt_brt.year:04d}",
                    f"{dt_brt.month:02d}",
                    f"{dt_brt.day:02d}",
                    f"{dt_brt.hour:02d}"
                )
                os.makedirs(out_dir, exist_ok=True)

                base = os.path.splitext(os.path.basename(file_path))[0]
                jpeg_path = os.path.join(out_dir, base + ".jpg")
                fig.savefig(jpeg_path, format='jpeg', dpi=150)
                plt.close(fig)

                nc.close()
                os.rename(file_path, os.path.join(out_dir, os.path.basename(file_path)))

                logging.info(f"Processed {file_path} → {jpeg_path}")
            except Exception:
                logging.exception(f"Error with file {file_path}")

    # Wait 10 minutes
    time.sleep(600)
