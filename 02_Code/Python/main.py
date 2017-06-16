import pandas as pd
from _modules.rightmoveScraping import rmScrape as rm
import importlib  # DEBUG
importlib.reload(rm)  # DEBUG

# Fetch data for
search_location = "canons park station car park"
# Search = HA8 6RL
# Radius = 0.5 miles
# Types  = bungalow, detached, flat, semi-detached, terraced
# Include sold and under offer = True
# Added to the site = anytime
rightmove_url = 'http://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=POSTCODE%5E367890&insId=1&radius=0.5&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&includeSSTC=true&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false'
# Save in
data_folder = '/Users/duccioa/CLOUD/01_Cloud/01_Work/04_Projects/0034_TFL/05_Data/'

df = rm.Scrape(rightmove_url,'buy', data_folder, search_location, include_url=False, include_coords=False)

m = df['price'].median()
median_by_numBed = pd.DataFrame(df.groupby(['number_bedrooms'])['price'].median())
mean_by_numBed = pd.DataFrame(df.groupby(['number_bedrooms'])['price'].mean())
mean_by_numBed_roomprice = pd.DataFrame()
for i, row in mean_by_numBed.iterrows():
    bedroom_price = int(int(row['price'])/int(i))
    mean_by_numBed_roomprice = mean_by_numBed_roomprice.append(pd.DataFrame({'avg_price_per_bedroom': [bedroom_price]}, index=[i]))
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
