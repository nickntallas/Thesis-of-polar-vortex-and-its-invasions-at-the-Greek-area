import pandas as pd
import matplotlib.pyplot as plt

# άνοιγμα του αρχείου
df = pd.read_csv('final_results.csv')

# Μετατροπή της στήλης 'Date' σε datetime
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')

# Φιλτράρισμα για τα έτη
df_6190 = df[(df['Date'].dt.year >= 1961) & (df['Date'].dt.year <= 1990)]
df_9120 = df[(df['Date'].dt.year >= 1991) & (df['Date'].dt.year <= 2020)]

# Διαχωρισμός των δεδομένων ανά ισοβαρικό επίπεδο
df_6190_10 = df_6190[df_6190['Pressure_Level'] == 10]
df_6190_50 = df_6190[df_6190['Pressure_Level'] == 50]
df_9120_10 = df_9120[df_9120['Pressure_Level'] == 10]
df_9120_50 = df_9120[df_9120['Pressure_Level'] == 50]

# Φιλτράρισμα για εμφάνιση συγκεκριμένων μηνών
df_6190_10_filt = df_6190_10[df_6190_10['Date'].dt.month.isin([10, 11, 12, 1, 2, 3])]
df_6190_50_filt = df_6190_50[df_6190_50['Date'].dt.month.isin([10, 11, 12, 1, 2, 3])]
df_9120_10_filt = df_9120_10[df_9120_10['Date'].dt.month.isin([10, 11, 12, 1, 2, 3])]
df_9120_50_filt = df_9120_50[df_9120_50['Date'].dt.month.isin([10, 11, 12, 1, 2, 3])]

# Δημιουργία των ιστογραμμάτων
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))
fig.suptitle('Εntry of the polar vortex into the Greek area', fontsize=16)

# Ιστόγραμμα για 6190_10
(df_6190_10_filt[df_6190_10_filt['Condition'] == 1].groupby(df_6190_10_filt['Date'].dt.month)['Date'].count().
 plot(kind='bar', ax=axes[0, 0], color='blue'))
axes[0, 0].set_title('1961-1990, P=10hPa')
axes[0, 0].set_xlabel('')

# Ιστόγραμμα για 6190_50
(df_6190_50_filt[df_6190_50_filt['Condition'] == 1].groupby(df_6190_50_filt['Date'].dt.month)['Date'].count().
 plot(kind='bar', ax=axes[0, 1], color='red'))
axes[0, 1].set_title('1961-1990, P=50hPa')
axes[0, 1].set_xlabel('')
