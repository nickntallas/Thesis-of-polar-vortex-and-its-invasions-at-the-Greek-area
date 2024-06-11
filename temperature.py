import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata

# άνοιγμα του αρχείου
ds = xr.open_dataset('temps.nc')
years10 = [1961, 1962, 1963, 1964, 1966, 1967, 1968, 1971, 1973, 1975, 1977, 1978, 1979, 1980, 1981, 1982, 1986, 1987,
           1988, 1989, 1990, 1992, 1993, 1996, 1997, 1998, 1999, 2000, 2001, 2004, 2005, 2006, 2007, 2009, 2010, 2011,
           2013, 2014, 2015, 2016, 2017, 2019]
years50 = [1968, 1970, 1974, 1987, 1996, 1998, 1999, 2001, 2003, 2004, 2006, 2007, 2009, 2013, 2016]
months = [1, 2, 3, 10, 11, 12]

# επιλογή των κατάλληλων ετών ανάλογα με το ισοβαρικό επίπεδο που χρειάζεται
for year in years50:
    for month in months:
        df = ds.sel(time=slice(str(year)+'-'+str(month).zfill(2), str(year)+'-'+str(month).zfill(2))).to_dataframe()

        # επεξεργασία των μετρήσεων
        df = df.reset_index()
        df = df[(df['longitude'] % 5 == 0) & (df['latitude'] % 5 == 0)]
        df.index = df['time']
        df = df.drop(columns=['time'])
        df.columns = ['Lon', 'Lat', 'P(hPa)', 'T(K)']

        # διαχωρισμός των μετρήσεων με βάση την πίεση
        df_10 = df[df['P(hPa)'] == 50].copy()
        last_rows = df_10[-11:].copy()
        last_rows.loc[:, 'Lon'] = last_rows['Lon'] + 5
        df_10 = pd.concat([df_10, last_rows])

        # Δημιουργία ομοιόμορφου πλέγματος
        lon_range = np.arange(df_10['Lon'].min(), df_10['Lon'].max() + 5, 5)
        lat_range = np.arange(df_10['Lat'].min(), df_10['Lat'].max() + 5, 5)
        lon_grid, lat_grid = np.meshgrid(lon_range, lat_range)

        # Αντιστοίχιση των θερμοκρασιών στο πλέγμα
        temp_grid = griddata((df_10['Lon'], df_10['Lat']), df_10['T(K)'], (lon_grid, lat_grid), method='linear')

        # δημιουργία του χάρτη
        plt.figure(figsize=(10, 8))
        m = Basemap(projection='ortho', lat_0=90, lon_0=0, resolution='l')

        m.drawcoastlines()
        m.drawcountries()
        m.etopo()

        x, y = m(lon_grid, lat_grid)

        m.contourf(x, y, temp_grid, cmap='coolwarm', alpha=0.7)

        plt.colorbar(label='Temperature (K)')
        plt.title('Temperature map at 50hPa, '+str(month).zfill(2)+' / '+str(year))
        plt.savefig('t_50_'+str(month).zfill(2)+'_'+str(year))
        plt.close()
