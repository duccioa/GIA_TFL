import pandas as pd
from _modules.rightmoveScraping import rmScrape as rm
import importlib  # DEBUG
importlib.reload(rm)  # DEBUG

# Fetch data for
search_location = "canons park station"
# Radius = 0.5 miles
# Types  = bungalow, detached, flat, semi-detached, terraced
# Include sold and under offer = True
# Added to the site = anytime
rightmove_url = 'http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=STATION%5E1754&radius=0.5&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced&includeSSTC=true&includeLetAgreed=false&areaSizeUnit=sqm'
# Save in
data_folder = '/Users/duccioa/CLOUD/01_Cloud/01_Work/04_Projects/0034_TFL/05_Data/'

df = rm.Scrape(rightmove_url,'buy', data_folder, search_location)
m = df['price'].median()
median_by_numBed = df.groupby(['number_bedrooms'])['price'].median()
mean_by_numBed = df.groupby(['number_bedrooms'])['price'].mean()
mean_by_numBed_roomprice = []
for i in range(0,len(s)):  #
    mean_by_numBed_roomprice.append(s[i]/int(s.index[i]))
median_by_propType = df.groupby(['property_type'])['price'].median()
print('Median price: £' + str(m))
print('Median price by number of bedrooms:')
print(median_by_numBed)
print('Average price by number of bedrooms:')
print(mean_by_numBed)
print('Average price of a bedroom by number of bedrooms: ')
print(mean_by_numBed_roomprice)
print('Median by property type: ')
print(median_by_propType)

search_location = 'islington'
rightmove_url = 'http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93965&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced%2Cland%2Cpark-home&includeSSTC=true&includeLetAgreed=false&areaSizeUnit=sqm'

df_islington = rm.Scrape(rightmove_url,'buy', data_folder, search_location)

search_location = 'london'
rightmove_url = 'http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&propertyTypes=flat%2Cterraced%2Csemi-detached%2Cdetached%2Cbungalow%2Cland%2Cpark-home&includeSSTC=true&dontShow=retirement%2CsharedOwnership'

df_london = rm.Scrape(rightmove_url,'buy', data_folder, search_location)




######

df = pd.read_csv('05_Data/rightmove_London_buy_results_RAW_2017-06-08.csv', index_col=0)


