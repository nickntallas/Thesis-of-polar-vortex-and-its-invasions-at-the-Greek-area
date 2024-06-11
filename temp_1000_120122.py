import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata

# άνοιγμα του αρχείου
ds = xr.open_dataset('temps_1000_120122.nc')

df = ds.to_dataframe()

# επεξεργασία των μετρήσεων
df = df.reset_index()
df = df[(df['longitude'] % 5 == 0) & (df['latitude'] % 5 == 0)]
df.index = df['time']
df = df.drop(columns=['time'])
df.columns = ['Lon', 'Lat', 'T(K)']

# διαχωρισμός των μετρήσεων με βάση την πίεση
df = df.copy()
last_rows = df[-11:].copy()
last_rows.loc[:, 'Lon'] = last_rows['Lon'] + 5
df = pd.concat([df, last_rows])

# Δημιουργία ομοιόμορφου πλέγματος
lon_range = np.arange(df['Lon'].min(), df['Lon'].max() + 5, 5)
lat_range = np.arange(df['Lat'].min(), df['Lat'].max() + 5, 5)
lon_grid, lat_grid = np.meshgrid(lon_range, lat_range)

# Αντιστοίχιση των θερμοκρασιών στο πλέγμα
temp_grid = griddata((df['Lon'], df['Lat']), df['T(K)'], (lon_grid, lat_grid), method='linear')

# δημιουργία του χάρτη
plt.figure(figsize=(10, 8))
m = Basemap(projection='ortho', lat_0=90, lon_0=0, resolution='l')

m.drawcoastlines()
m.drawcountries()
m.etopo()

x, y = m(lon_grid, lat_grid)

m.contourf(x, y, temp_grid, cmap='coolwarm', alpha=0.7)

plt.colorbar(label='Temperature (K)')
plt.title('Temperature map at 1000hPa, 12/01/2022')
plt.savefig('t_1000_120122.png')
plt.close()
