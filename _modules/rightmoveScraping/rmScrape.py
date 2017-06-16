
def removeDuplicates(df):
    from difflib import SequenceMatcher
    df = df.assign(checked=False, selected=False)
    df.sort_values(['price', 'added_date'], ascending=True, inplace=True)
    for i, row1 in df.iterrows():
        if row1['checked']:
            #print('Already checked')
            continue
        else:
            row1_price = row1['price']
            row1_propertyType = row1['property_type']
            row1_numBed = row1['number_bedrooms']
            row1_address = row1['address']

            df_temp = df[(abs(df['price'] - row1_price) < 40000) & (df['number_bedrooms'] == row1_numBed) & (df['property_type'] == row1_propertyType)]

            if df_temp.shape[0] == 1:
                df['checked'].loc[df_temp.index] = True
                df['selected'].loc[df_temp.index] = True
                #print('One single line')
            else:
                #print('More than one line')
                duplicates = df_temp.apply(lambda row:(SequenceMatcher(None, row1_address, row['address']).ratio() > 0.5), axis=1)
                df_temp['checked'].ix[duplicates] = True
                df['checked'].loc[df_temp.index] = True
                line = df_temp.query('checked == True').sort_values('added_date', ascending=False).iloc[0]
                df['selected'].loc[line.name] = True
    outcome = df.query('selected==True')
    outcome.drop(['checked', 'selected'], axis=1,inplace=True)
    return outcome

def fetchCoordinates(url):
    from lxml import html
    import requests
    import re
    url = 'http://www.rightmove.co.uk/property-for-sale/property-45212490.html'  # DEBUG
    page = requests.get(url)
    tree = html.fromstring(page.content)
    for el in tree.xpath('//div[contains(@class, "pos-rel")]//a'):
        coords_url = el.xpath('img/@src')[0]
    try:
        lat = float(re.search('latitude=(-?\d+\.\d+)', coords_url).group(1))
        lon = float(re.search('longitude=(-?\d+\.\d+)', coords_url).group(1))
        d = {'lat':lat, 'lon':lon}
        print('Fetching succesful')
        print(d)
        return(d)
    except:
        return {'lat': None, 'lon':None}


def Scrape(rightmove_url, rent_or_buy, dest_folder, location, include_url=False, include_coords = False):
    # imports
    from lxml import html
    import requests
    import pandas as pd
    #pd.set_option('precision', 2)
    #pd.set_option('display.max_rows', 50)
    #pd.set_option('display.max_columns', 500)
    #pd.set_option('display.width', 1000)
    #pd.set_option('display.float_format', lambda x: '%.3f' % x)
    import datetime as dt
    import re

    # Initialise a pandas DataFrame to store the results
    df = pd.DataFrame(columns=['price', 'property_type', 'address', 'url', 'added_date'])

    # Get the total number of results returned by the search
    page = requests.get(rightmove_url)
    tree = html.fromstring(page.content)
    xp_result_count = '//span[@class="searchHeader-resultCount"]/text()'
    result_count = int(tree.xpath(xp_result_count)[0].replace(",", ""))
    print('Counted ' + str(result_count) + ' results')
    if result_count > 1050:
        print('Error: the number of results exceeds the maximum number that it is possible to fetch from the website (max results 1050)')

    # Convert the total number of search results into the number of iterations required for the loop
    loop_count = int(result_count / 24)
    if result_count % 24 > 0:
        loop_count = loop_count + 1

    # Set the Xpath variables for the loop
    if rent_or_buy == 'rent':
        xp_prices = '//span[@class="propertyCard-priceValue"]/text()'
    elif rent_or_buy == 'buy':
        xp_prices = '//div[@class="propertyCard-priceValue"]/text()'

    xp_titles = '//div[@class="propertyCard-details"]//a[@class="propertyCard-link"]//h2[@class="propertyCard-title"]/text()'
    xp_addresses = '//span[@data-bind="text: displayAddress"]/text()'
    xp_weblinks = '//div[@class="propertyCard-details"]//a[@class="propertyCard-link"]/@href'
    xp_date = '//span[@class="propertyCard-branchSummary-addedOrReduced"]/text()'

    # Start the loop through the search result web pages
    print('Fetching data')
    for pages in range(0, loop_count, 1):
        url = rightmove_url +'&index=' + str(pages * 24)
        page = requests.get(url)
        tree = html.fromstring(page.content)

        # Reset variables
        price_pcm, titles, addresses, weblinks, added_date, loc = [], [], [], [], [], []

        # Create data lists from Xpaths
        for val in tree.xpath(xp_prices):
            price_pcm.append(val)
        for val in tree.xpath(xp_titles):
            titles.append(val)
        for val in tree.xpath(xp_addresses):
            addresses.append(val)
        for val in tree.xpath(xp_weblinks):
            weblinks.append('http://www.rightmove.co.uk' + val)
        for val in tree.xpath(xp_date):
            added_date.append(val)
            loc.append(location)

        # Convert data to temporary DataFrame
        data = [price_pcm, titles, addresses, loc, weblinks, added_date]
        temp_df = pd.DataFrame(data)
        temp_df = temp_df.transpose()
        temp_df.columns = ['price', 'property_type', 'address', 'location','url', 'added_date']

        # Drop empty rows from DataFrame which come from placeholders in rightmove html
        if len(temp_df) > 0:  # This condition is required because rightmove tells you it has more results than it returns, and the below will error if temp_df is empty
            temp_df = temp_df[temp_df.url != 'http://www.rightmove.co.uk' + '/property-for-sale/property-0.html']
        # Join temporary DataFrame to main results DataFrame
        frames = [df, temp_df]
        df = pd.concat(frames)
    print('DONE')

    print('Start processing data')
    # Renumber results DataFrame index to remove duplicate index values
    df = df.reset_index(drop=True)
    print('Processing index')
    # Convert price column to numeric values for analysis
    df.price.replace(regex=True, inplace=True, to_replace=r'\D', value=r'')
    df.price = pd.to_numeric(df.price)
    print('DONE')
    # Extract postcode stems to a separate column
    print('Processing postcodes')
    df['postcode'] = df['address'].str.extract(r'\b([A-Za-z][A-Za-z]?[0-9][0-9]?[A-Za-z]?)\b', expand=True)
    print('DONE')
    # Extract number of bedrooms from 'type' to a separate column
    print('Processing number of bedrooms')
    df['number_bedrooms'] = df['property_type'].str.extract(r'\b([\d][\d]?)\b', expand=True)
    df.loc[df['property_type'].str.contains('studio', case=False, na=False), 'number_bedrooms'] = str(0)
    df['number_bedrooms'] = df['number_bedrooms'].astype(int)
    print('DONE')
    # Add in search_date column to record the date the search was run (i.e. today's date)
    print('Adding date collection date')
    now = dt.datetime.today().strftime("%d/%m/%Y")
    df['search_date'] = now
    print('DONE')
    # Processing added date
    print('Processing added date')
    yesterday = dt.date.today() - dt.timedelta(1)
    df['added_date'].loc[df['added_date'].str.contains(r'\b(Added yesterday)', case=False, na=now)] = yesterday.strftime("%d/%m/%Y")  # Convert 'Added yesterday' yesterday's date
    df['added_date'] = df['added_date'].str.extract(r'\b([0-9]{2}?[/][0-9][0-9]?[/][0-9]{4})\b', expand=True)
    df = df.assign(added_date=pd.to_datetime(df['added_date']))
    print('DONE')
    # Add search type column
    df['rent_or_buy'] = rent_or_buy
    # Processing types
    print('Processing type of properties')
    labels = []
    for type_label in df['property_type']:
        if re.search(r'\b[dD](etache)[aA-zZ] [Hh](ouse)\b', type_label) or re.search(r'\b[cC](halet)\b',
                                                                               type_label):  # Detached house, chalet
            labels.append('detached')
        elif re.search(r'\b[sS](emi-detached)\b', type_label):  # semi-detached
            labels.append('semi-detached')
        elif re.search(r'\b[aA](partment)\b', type_label) or re.search(r'\b[fF](lat)\b', type_label) or re.search(
                r'\b[mM](aisonette)\b', type_label) or re.search(r'\b[sS](tudio)\b', type_label) or re.search(r'\b[pP](enthouse)\b',
                                                                                                  type_label):  # Apartment, flat, maisonette, studio, penthouse
            labels.append('flat')
        elif re.search(r'\b[tT](errace)[d ]\b', type_label) or re.search(r'\b[mM](ew)[sS ]\b', type_label):  # terraced house
            labels.append('terraced')
        elif re.search(r'\b[lL](and)\b', type_label) or re.search(r'\b[pP](lot)\b', type_label):
            labels.append('land')
        elif re.search(r'\b[pP](roperty)\b', type_label):
            labels.append('property')
        elif re.search(r'\b[hH](ouse)\b', type_label):
            labels.append('detached')
        else:
            labels.append('other')
    print('DONE')

    # Reformat the dataframe
    df_output = df[['search_date','added_date', 'address', 'location', 'postcode', 'rent_or_buy', 'number_bedrooms','price', 'url']]
    df_output = df_output.assign(property_type=labels)
    # Remove duplicates
    print('Remove duplicates')
    df_output = removeDuplicates(df_output)
    # Fetch coordinates
    df_output.index.name = 'index'
    if include_coords:
        print('Fetching the coordinates')
        coords = pd.DataFrame()
        for i, row in df_output.iterrows():
            url_c = row['url']
            df_coords = pd.DataFrame([fetchCoordinates(url_c)], index=[i])
            print(df_coords)
            coords = coords.append(df_coords)
        coords.index.name = 'index'
        df_output = pd.merge(df_output, coords, left_index=True, right_index=True)
    # Remove url
    if not include_url:
        df_output.drop('url', axis=1, inplace=True)
    # Export the results to CSV
    csv_filename = dest_folder + 'rightmove__' + location.replace(' ', '-') + '_' + rent_or_buy + '_results_' + str(
        dt.datetime.today().strftime("%Y-%m-%d_%Hh%Mm")) + '.csv'
    df_output.to_csv(csv_filename, encoding='utf-8')
    print(len(df_output), 'results saved as \'', csv_filename, '\'')

    # Print message to validate search has run showing number of results received and name of csv file.
    #print(df.head())
    #print(df.describe)
    #print(df.info())

    return df_output


