import numpy as np
import scipy.interpolate
import shapefile
from shapely.geometry import shape, Point
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

def get_uruguay_mask(lons, lats, shapefile_path='data/URY_adm0.shp'):
    """Genera una máscara booleana para el territorio uruguayo."""
    try:
        with shapefile.Reader(shapefile_path) as sf:
            polygon = shape(sf.shapes()[0])
    except Exception as e:
        print(f"Error al cargar shapefile: {e}")
        return None

    lon_grid, lat_grid = np.meshgrid(lons, lats)
    # Ajuste de longitud 0-360 a -180 a 180 si es necesario
    lon_to_check = np.where(lon_grid > 180, lon_grid - 360, lon_grid)
    
    # Vectorización para alto rendimiento
    mask_func = np.vectorize(lambda x, y: polygon.contains(Point(x, y)))
    return mask_func(lon_to_check, lat_grid)

def regrillado(obs, mod_shape, lonobs, latobs, lonmod, latmod):
    """Regrilla observaciones a la resolución del modelo."""
    X, Y = np.meshgrid(lonobs, latobs)
    XI, YI = np.meshgrid(lonmod, latmod)
    X = X + 360 # Normalización para coincidir con modelos[cite: 1, 2]
    
    # Reorganización de datos para interpolación[cite: 1, 2]
    obs_reshaped = obs.transpose([1, 2, 0]).reshape(-1, mod_shape[0])
    new_data = scipy.interpolate.griddata(
        (X.flatten(), Y.flatten()), 
        obs_reshaped, 
        (XI, YI), 
        method='linear'
    )
    return new_data.transpose([2, 0, 1])

def configurar_mapa_uy(ax, lons, lats):
    """Aplica formato estándar de Cartopy para mapas de Uruguay."""
    ax.coastlines()
    ax.add_feature(cfeat.RIVERS)
    ax.add_feature(cfeat.BORDERS)
    ax.set_extent([min(lons), max(lons), max(lats), min(lats)], crs=ccrs.PlateCarree())
    ax.set_xticks([295, 300, 305, 310], crs=ccrs.PlateCarree())
    ax.set_yticks([-25, -30, -35], crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True, number_format='.0f'))
    ax.yaxis.set_major_formatter(LatitudeFormatter())
