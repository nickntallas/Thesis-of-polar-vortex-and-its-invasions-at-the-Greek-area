import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from shapely.geometry import Polygon
from mpl_toolkits.basemap import Basemap

# άνοιγμα του αρχείου
ds = xr.open_dataset('monthly_1961_2020.nc')

# θέλουμε να ελέγξουμε ξεχωριστά κάθε μήνα της τριακονταετίας 1991-2020
for year in range(1991, 2021):
    for month in range(1, 13):
        df_1991_2020 = ds.sel(time=slice(str(year) + '-' + str(month).zfill(2), str(year) + '-'
                                         + str(month).zfill(2))).to_dataframe()

        # επεξεργασία των μετρήσεων
        df_1991_2020 = df_1991_2020.reset_index()
        df_1991_2020 = df_1991_2020[(df_1991_2020['longitude'] % 5 == 0) & (df_1991_2020['latitude'] % 5 == 0)]
        df_1991_2020.index = df_1991_2020['time']
        df_1991_2020 = df_1991_2020.drop(columns=['time'])
        df_1991_2020.columns = ['Lon', 'Lat', 'P(hPa)', 'U(m/s)', 'V(m/s)']

        # υπολογισμός της ταχύτητας του ανέμου από τις συνιστώσες του
        df_1991_2020['WS(m/s)'] = np.sqrt(df_1991_2020['U(m/s)'].pow(2) + df_1991_2020['V(m/s)'].pow(2))

        # Εντοπισμός μοναδικών τιμών για το γεωγραφικό μήκος στη στήλη 'Lon'
        unique_lon_values = df_1991_2020['Lon'].unique()

        # Λεξικό για αποθήκευση των DataFrames ανά γεωγραφικό μήκος
        dfs_by_lon = {}

        # δημιουργία dataframes για την αποθήκευση των σημείων μέγιστου ανέμου
        points10_WS = pd.DataFrame(columns=['Lat', 'Lon'])
        points50_WS = pd.DataFrame(columns=['Lat', 'Lon'])

        for lon_value in unique_lon_values:
            # Φιλτράρισμα του DataFrame για το συγκεκριμένο γεωγραφικό μήκος
            df_lon = df_1991_2020.loc[df_1991_2020['Lon'] == lon_value].copy()

            # Αποθήκευση του DataFrame με τη συγκεκριμένη ονομασία στο λεξικό
            df_name = f"Lon1_{lon_value}"
            dfs_by_lon[df_name] = df_lon

            # διαχωρισμός των μετρήσεων με βάση την πίεση
            df_lon_10 = df_lon[df_lon['P(hPa)'] == 10]
            df_lon_50 = df_lon[df_lon['P(hPa)'] == 50]

            # εύρεση μέγιστων τιμών ταχύτητας ανέμου και των συντεταγμένων τους
            max_W10 = max(df_lon_10['WS(m/s)'])
            max_W10_coord = df_lon_10.loc[df_lon_10['WS(m/s)'] == max_W10, ['Lat', 'Lon']]
            max_W50 = max(df_lon_50['WS(m/s)'])
            max_W50_coord = df_lon_50.loc[df_lon_50['WS(m/s)'] == max_W50, ['Lat', 'Lon']]

            # αποθήκευση αυτών των σημείων σε dataframes που δημιουργήθηκαν προηγουμένως
            points10_WS = pd.concat([points10_WS, pd.DataFrame({'Lat': [max_W10_coord['Lat'][0]],
                                                                'Lon': [max_W10_coord['Lon'][0]],
                                                                'WS': [max_W10]})], ignore_index=True)
            points50_WS = pd.concat([points50_WS, pd.DataFrame({'Lat': [max_W50_coord['Lat'][0]],
                                                                'Lon': [max_W50_coord['Lon'][0]],
                                                                'WS': [max_W50]})], ignore_index=True)

            # αποθήκευση των σημείων μέγιστου ανέμου σε αρχεία csv
            points10_WS.to_csv('points10_x5_' + str(year) + str(month).zfill(2) + '_WS.csv')
            points50_WS.to_csv('points50_x5_'+str(year) + str(month).zfill(2) + '_WS.csv')

            # Δημιουργία του Basemap ανάλογα το ισοβαρικό επίπεδο που χρειάζεται
            m = Basemap(projection='ortho', resolution='l', lat_0=90, lon_0=0)
            m.drawcoastlines()
            m.drawcountries()
            m.etopo()

            # Χάραξη γραμμής πάνω από τα σημεία μέγιστου ανέμου στο χάρτη
            x, y = m(points50_WS['Lon'], points50_WS['Lat'])
            m.plot(x, y, '.', c='red')

            plt.title('Polar vortex at 50hPa, '+str(month).zfill(2)+'/'+str(year))
            plt.savefig('map_'+str(month).zfill(2)+'_'+str(year)+'_50_x5.png')
            plt.show()
            plt.close()

# Δημιουργία λίστας με τα σημεία μέγιστου ανέμου
points10 = [(lon, lat) for lon, lat in zip(points10_WS['Lon'], points10_WS['Lat'])]
points50 = [(lon, lat) for lon, lat in zip(points50_WS['Lon'], points50_WS['Lat'])]

# Δημιουργία πολυγώνου από τα σημεία μέγιστου ανέμου
polygon10 = Polygon(points10)
polygon50 = Polygon(points50)

# Υπολογισμός εμβαδού
area10 = polygon10.area
area50 = polygon50.area

# επιλογή του φακέλου που βρισκόμαστε
directory = os.getcwd()

# δημιουργία λίστας με τα ονόματα των αρχείων που πρέπει να ελεγχθούν
files_to_check = [f for f in os.listdir(directory) if f.endswith('_WS.csv')]
match_files = []
non_match_files = []

# Εύρεση των ονομάτων των αρχείων που περιέχουν τιμές με τις συγκεκριμένες συνθήκες
for file in files_to_check:
    data = pd.read_csv(file)

    # Ελέγχουμε τις συνθήκες για τις στήλες Lat και Lon
    condition = (data['Lat'].between(40, 41)) & (data['Lon'].between(19.5, 26))
    filtered_data = data[condition]

    # Προσθέτουμε στην κατάλληλη λίστα τα αρχεία που πληρούν/δεν πληρούν τις συνθήκες
    if not filtered_data.empty:
        match_files.append(file)
    else:
        non_match_files.append(file)

# Αποθήκευση των αρχείων σε ένα νέο αρχείο
with open('matching_files_1991_2020.txt', 'w') as f:
    for file in match_files:
        f.write(f"{file}\n")

# αποθήκευση των ημερομηνιών σε αρχείο csv
with open('final_results.csv', 'w') as f:
    f.write(f"Date,Pressure_Level,Condition\n")

    for file in match_files:
        f.write(f"{str(file[12:16])+str(file[16:18])+','+str(file[6:8])+',1'}\n")

    for file in non_match_files:
        f.write(f"{str(file[12:16])+str(file[16:18])+','+str(file[6:8])+',0'}\n")
