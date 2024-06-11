import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import statistics
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
import seaborn as sns

ds = xr.open_dataset('data_12012022.nc')

# επεξεργασία των μετρήσεων
df1 = ds.to_dataframe()
df1 = df1.reset_index()
df1.index = df1['time']
df1 = df1.drop(columns=['time'])
df1.columns = ['Lon', 'Lat', 'P(hPa)', 'Div', 'G(m2/s2)', 'O3(kg/kg)', 'PV(K m2/kg s)', 'T(K)', 'U(m/s)', 'V(m/s)']

# υπολογισμός της ταχύτητας του ανέμου από τις συνιστώσες του
df1['WS(m/s)'] = np.sqrt(df1['U(m/s)']**2 + df1['V(m/s)']**2)

# Φιλτράρισμα τιμών ώστε να έχω δεδομένα 5χ5 (ακέραιες τιμές γεωγραφικών μηκών που διαιρούνται με το 5)
Lon5 = df1[(df1['Lon'] % 5 == 0) & (df1['Lat'] % 5 == 0)]

# Μετατροπή 5 μοιρών γεωγραφικού πλάτους σε ακτίνια
rads = np.radians(5)
# Μετατροπή ακτινίων σε μέτρα (σε μια σφαιρική επιφάνεια όπως η Γη)
earth_radius = 6371  # Ακτίνα της Γης σε χιλιόμετρα
distance_in_km = rads * earth_radius

# Εντοπισμός μοναδικών τιμών για το γεωγραφικό μήκος στη στήλη 'Lon'
unique_lon_values = Lon5['Lon'].unique()

# Λεξικό για αποθήκευση των DataFrames ανά γεωγραφικό μήκος
dfs_by_lon = {}
Gs_10 = pd.DataFrame(columns=['G', 'Point'])
Ts_10 = pd.DataFrame(columns=['T', 'Point'])
WSs_10 = pd.DataFrame(columns=['WS', 'Point'])
Gs_50 = pd.DataFrame(columns=['G', 'Point'])
Ts_50 = pd.DataFrame(columns=['T', 'Point'])
WSs_50 = pd.DataFrame(columns=['WS', 'Point'])
points10_WS = pd.DataFrame(columns=['Point'])
points50_WS = pd.DataFrame(columns=['Point'])
points10_dt = pd.DataFrame(columns=['Point'])
points50_dt = pd.DataFrame(columns=['Point'])

for lon_value in unique_lon_values:
    # Φιλτράρισμα του DataFrame για το συγκεκριμένο γεωγραφικό μήκος
    df_lon = df1.loc[df1['Lon'] == lon_value].copy()

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
    WSs_10 = pd.concat([WSs_10, pd.DataFrame({'WS': [max_W10], 'Point': [max_W10_coord]})], ignore_index=True)
    WSs_50 = pd.concat([WSs_50, pd.DataFrame({'WS': [max_W50], 'Point': [max_W50_coord]})], ignore_index=True)

    # εύρεση μέγιστης θερμοβαθμίδας (και συντεταγμένες)
    diff50 = abs(df_lon_50['T(K)'].diff())
    grad50 = diff50 / distance_in_km
    diff10 = abs(df_lon_10['T(K)'].diff())
    grad10 = diff10 / distance_in_km

    max_grad50 = grad50.max()
    max_grad50_idx = np.argmax(grad50)
    max_lat_50 = df_lon_10['Lat'][max_grad50_idx]
    max_lon_50 = df_lon_10['Lon'][max_grad50_idx]
    max_grad10 = grad10.max()
    max_grad10_idx = np.argmax(grad10)
    max_lat_10 = df_lon_10['Lat'][max_grad10_idx]
    max_lon_10 = df_lon_10['Lon'][max_grad10_idx]

    # συντεταγμένες μέγιστης ταχύτητας ανέμου και μέγιστης θερμοβαθμίδας και εύρεση των Τ, G
    coord10 = np.array([(max_W10_coord['Lon'][0], max_W10_coord['Lat'][0]), (max_lon_10, max_lat_10)])
    coord50 = np.array([(max_W50_coord['Lon'][0], max_W50_coord['Lat'][0]), (max_lon_50, max_lat_50)])
    T_10 = df_lon_10['T(K)'].loc[df_lon_10['Lat'] == max_lat_10]
    G_10 = df_lon_10['G(m2/s2)'].loc[df_lon_10['Lat'] == max_lat_10]
    T_50 = df_lon_50['T(K)'].loc[df_lon_50['Lat'] == max_lat_50]
    G_50 = df_lon_50['G(m2/s2)'].loc[df_lon_50['Lat'] == max_lat_50]
    Gs_10 = pd.concat([Gs_10, pd.DataFrame({'G': [G_10[0]], 'Point': [(max_lon_10, max_lat_10)]})], ignore_index=True)
    Ts_10 = pd.concat([Ts_10, pd.DataFrame({'T': [T_10[0]], 'Point': [(max_lon_10, max_lat_10)]})], ignore_index=True)
    Gs_50 = pd.concat([Gs_50, pd.DataFrame({'G': [G_50[0]], 'Point': [(max_lon_50, max_lat_50)]})], ignore_index=True)
    Ts_50 = pd.concat([Ts_50, pd.DataFrame({'T': [T_50[0]], 'Point': [(max_lon_50, max_lat_50)]})], ignore_index=True)
    points10_WS = pd.concat([points10_WS, pd.DataFrame({'Point': [coord10[0]]})], ignore_index=True)
    points50_WS = pd.concat([points50_WS, pd.DataFrame({'Point': [coord50[0]]})], ignore_index=True)
    points10_dt = pd.concat([points10_dt, pd.DataFrame({'Point': [coord10[1]]})], ignore_index=True)
    points50_dt = pd.concat([points50_dt, pd.DataFrame({'Point': [coord50[1]]})], ignore_index=True)

    # Δημιουργία του Basemap
    m = Basemap(projection='ortho', resolution='l', lat_0=90, lon_0=0)
    m.drawcoastlines()
    m.drawcountries()
    m.etopo()

    # Χάραξη γραμμής πάνω από τα σημεία μέγιστου ανέμου στο χάρτη
    x, y = m(coord50[0][0], coord50[0][1])
    m.plot(x, y, '.', c='red')

plt.title('Points of maximum wind speed at 50hPa')
plt.savefig('map50_ws_x5.png')
plt.show()
plt.close()

# Δημιουργούμε ένα πολύγωνο με βάση τα σημεία
polygon10 = Polygon(points10_dt['Point'])
polygon50 = Polygon(points50_dt['Point'])
area10 = polygon10.area
area50 = polygon50.area

G_mean10 = Gs_10['G'].mean()
G_stddev10 = statistics.stdev(Gs_10['G'])
G_mean50 = Gs_50['G'].mean()
G_stddev50 = statistics.stdev(Gs_50['G'])

f1, (ax_box1, ax_hist1) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
sns.boxplot(x=WSs_10['WS'], ax=ax_box1)
sns.histplot(x=WSs_10['WS'], bins=30, kde=True, stat='frequency', ax=ax_hist1)
ax_box1.set(yticks=[])
sns.despine(ax=ax_hist1)
sns.despine(ax=ax_box1, left=True)
plt.suptitle('Distribution of wind speed at 10hPa')
plt.show()
plt.savefig('hist_120122_10.png')

# Median
my_median1 = statistics.median(WSs_10['WS'])
print(my_median1)
# Quantiles
my_quantiles1 = statistics.quantiles(WSs_10['WS'])
print(my_quantiles1)
my_IQR1 = my_quantiles1[2]-my_quantiles1[0]
print(my_IQR1)


f2, (ax_box2, ax_hist2) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
sns.boxplot(x=WSs_50['WS'], ax=ax_box2)
sns.histplot(x=WSs_50['WS'], bins=30, kde=True, stat='frequency', ax=ax_hist2)
ax_box1.set(yticks=[])
sns.despine(ax=ax_hist2)
sns.despine(ax=ax_box2, left=True)
plt.suptitle('Distribution of wind speed at 50hPa')
plt.show()
plt.savefig('hist_120122_50.png')

# Median
my_median2 = statistics.median(WSs_50['WS'])
print(my_median2)
# Quantiles
my_quantiles2 = statistics.quantiles(WSs_50['WS'])
print(my_quantiles2)
my_IQR2 = my_quantiles2[2]-my_quantiles2[0]
print(my_IQR2)
