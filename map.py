import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Δημιουργία ενός νέου χάρτη
map = Basemap(llcrnrlat=30, urcrnrlat=90, llcrnrlon=0, urcrnrlon=40, resolution='i')

# Σχεδίαση των συνόρων των χωρών
map.drawcoastlines()
map.drawcountries()
map.etopo()
map.drawmeridians(range(0, 41, 10), labels=[True, False, False, True])
map.drawparallels(range(30, 91, 10), labels=[True, False, False, True])

# Ορισμός των γεωγραφικών συντεταγμένων του πολυγώνου
lats = [40, 41]
lons = [19.5, 26]

# Σχεδίαση του κόκκινου πολυγώνου
x, y = map(lons, lats)
map.plot(x, y, marker=None, color='red', linewidth=2)

# Εμφάνιση του χάρτη
plt.show()
