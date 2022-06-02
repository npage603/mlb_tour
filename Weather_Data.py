# Create working Weather file with Rain Probabilities

# Import the appropriate libraries
from bs4 import BeautifulSoup
import requests
import datetime as dt
import pandas as pd
import numpy as np
import os
import zipfile
from collections import OrderedDict

pd.options.display.max_columns = 100

# Get the current working directory
cwd = os.getcwd()

# Print the current working directory
print("Current working directory: {0}".format(cwd))

# Unzip the file and read the CSV to get the weather DataFrame
file_name = '2967026'
zf = zipfile.ZipFile(cwd + '\\' + file_name + '.zip')
weather = pd.read_csv(zf.open(file_name + '.csv'), sep=',')

# Drop all columns except station, date, and probability of >= 0.01 rain
rainProb = pd.DataFrame(weather, columns=['STATION','NAME','DATE','DLY-PRCP-PCTALL-GE001HI'])

# Filter out bad data
# Exclude NULL from analysis
rainProb['DLY-PRCP-PCTALL-GE001HI'].fillna('EXCLUDE', inplace=True)
bad = len(rainProb)
new = []
for row in rainProb.itertuples(index=False):
    if type(row[3]) == float:
        new.append(row)

new = pd.DataFrame(new, columns=['STATION','NAME','DATE','DLY-PRCP-PCTALL-GE001HI'])
rainProb = new
good = len(rainProb)
print("Bad Rows Filtered Out: " + str(bad-good))
print("Total Rows: " + str(good))

# Read the CSV to get the station lookup DataFrame
file_name = '\\weather_station_lookup.csv'
lookup = pd.read_csv(cwd+file_name)
lookup.rename(columns=lambda x: x.strip(), inplace=True)

# Merge to bring in Zip Code, latitude, and longitude
rainProb = rainProb.merge(lookup, left_on='STATION', right_on='Station Code', how='left')
rainProb["Zip Code"] = rainProb["Zip Code"].astype('str')
rainProb["Zip Code"] = rainProb["Zip Code"].apply(lambda x: '0'+ x if len(x)==4 else x)

uniqueCity = pd.DataFrame(rainProb, columns=['City','State']).drop_duplicates().reset_index(drop=True)
print(uniqueCity)

# Write daily weather DataFrame to a CSV
export_csv = rainProb.to_csv(cwd + '\\Daily_Rain_Probability_By_City.csv')
print(export_csv)