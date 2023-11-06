#importing libraries
import numpy as np
from pymongo import MongoClient
import pandas as pd
import time
import os
import requests
import json
from dotenv import load_dotenv
import geopandas as gpd
import geopy.distance
import folium
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster
from cartoframes.viz import Map, Layer, popup_element

import os
from dotenv import load_dotenv
load_dotenv() # load_env
cc = os.getenv("credit_card")
token = os.getenv("token")


#credentials:
client = MongoClient("localhost:27017")
db = client["Ironhack"]
companies = db.get_collection("Companies")

#querying MongoDB to get the companies:
condition_1 = {"category_code": "analytics"}
condition_2 = {"category_code": "ecommerce"}
condition_3 = {"category_code": "games_video"}
condition_4 = {"category_code": "software"}
condition_5 = {"category_code": "web"}
minimum_founding_year = 2010
condition_founded_year = {"founded_year": {"$gt":minimum_founding_year}}

projection = {"_id": 0, "name":1,"category_code":1, "founded_year":1, "offices.latitude":1, "offices.longitude":1}
conditions = [
    {"$and": [condition_1, condition_founded_year]},
    {"$and": [condition_2, condition_founded_year]},
    {"$and": [condition_3, condition_founded_year]},
    {"$and": [condition_4, condition_founded_year]},
    {"$and": [condition_5, condition_founded_year]},]

# Create the final query with the $or operator
the_5_different_categories = {"$or": conditions}
# Find companies that meet any of the specified conditions
list_narrowed_companies_to_benchmark = list(companies.find(the_5_different_categories, projection))

companies_to_benchmark = pd.DataFrame(list_narrowed_companies_to_benchmark)
companies_to_benchmark.sample(5)

#the coordinates are fuc*ed up all together in the same col. Let's split them:
def extract_latitude(office):
    if office !=[]:
        return office[0].get('latitude', None)
    else:
        return None

def extract_longitude(office):
    if office !=[]:
        return office[0].get('longitude', None)
    else:
        return None

companies_to_benchmark['latitude'] = companies_to_benchmark['offices'].apply(extract_latitude)
companies_to_benchmark['longitude'] = companies_to_benchmark['offices'].apply(extract_longitude)

#don't need the offices anymore, thank you for your service:
companies_to_benchmark.drop('offices',axis=1,inplace=True)
companies_to_benchmark.sample(5)

#companies with no coordinates off:
companies_to_benchmark_with_coordinates = companies_to_benchmark.dropna()
companies_to_benchmark_with_coordinates.head()

#an example with a company:
mokitown_lat = 37.09024
mokitown_long = -95.712891

lat = mokitown_lat
lon = mokitown_long


def requests_for_foursquare (query, lat, lon, radius=50000, limit=10):
    url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={lat}%2C{lon}&radius={radius}&limit={limit}"
    headers = {
        "accept": "application/json",
        "Authorization": token
    }
    
    try:
        return requests.get(url, headers=headers).json()
    except:
        print("no :(")

results_design_studios = requests_for_foursquare ("design studio", lat, lon, radius=50000, limit=10)

venues = results_design_studios.get('results', [])

venues_with_coordinates = []

for venue in venues:
    venue_name = venue.get('name', '')  

    geocodes = venue.get('geocodes', {}).get('main', {})
    venue_latitude = geocodes.get('latitude', None)
    venue_longitude = geocodes.get('longitude', None)

    if venue_name and venue_latitude is not None and venue_longitude is not None:
        venues_with_coordinates.append({
            'name': venue_name,
            'latitude': venue_latitude,
            'longitude': venue_longitude
        })

# In my dataframe I want a new column to store the nearby design studios
companies_to_benchmark_with_coordinates['Design Studios nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("design studio", lat, lon, radius=50000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Design Studios nearby'] = venues_with_coordinates


# Add a new column 'Design Studios Count' to store the count of design studios for each company
companies_to_benchmark_with_coordinates['Design Studios Count'] = companies_to_benchmark_with_coordinates['Design Studios nearby'].apply(lambda x: len(x) if x is not None else 0)






#I'm really just gonna make use of my previous code but replacing where needed. 

# In my dataframe I want a new column to store the nearby daycare
companies_to_benchmark_with_coordinates['Daycare nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Daycare", lat, lon, radius=50000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Daycare nearby'] = venues_with_coordinates

# Add a new column 'Daycare Count' to store the count of design studios for each company
companies_to_benchmark_with_coordinates['Daycare Count'] = companies_to_benchmark_with_coordinates['Daycare nearby'].apply(lambda x: len(x) if x is not None else 0)






def requests_for_foursquare_starbucks(query, lat, lon, chains, radius=5000, limit=10):
    chain_code_starbucks = 'ab4c54c0-d68a-012e-5619-003048cad9da'

    url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={lat}%2C{lon}&radius={radius}&chains={chain_code_starbucks}&limit={limit}"

    headers = {
        "accept": "application/json",
        "Authorization": token
    }

    try:
        return requests.get(url, headers=headers).json()
    except:
        print("no :(")


companies_to_benchmark_with_coordinates['Starbucks nearby'] = None
chain_code_starbucks = 'ab4c54c0-d68a-012e-5619-003048cad9da'

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare_starbucks("Starbucks", lat, lon, chains=chain_code_starbucks, radius=5000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Starbucks nearby'] = venues_with_coordinates



# Add a new column 'Starbucks Count' to store the count of design studios for each company
companies_to_benchmark_with_coordinates['Starbucks Count'] = companies_to_benchmark_with_coordinates['Starbucks nearby'].apply(lambda x: len(x) if x is not None else 0)









companies_to_benchmark_with_coordinates['Airport nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Airport", lat, lon, radius=5000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Airport nearby'] = venues_with_coordinates

companies_to_benchmark_with_coordinates['Airport Count'] = companies_to_benchmark_with_coordinates['Airport nearby'].apply(lambda x: len(x) if x is not None else 0)








companies_to_benchmark_with_coordinates['Train nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Train", lat, lon, radius=5000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Train nearby'] = venues_with_coordinates


companies_to_benchmark_with_coordinates['Train Count'] = companies_to_benchmark_with_coordinates['Train nearby'].apply(lambda x: len(x) if x is not None else 0)







companies_to_benchmark_with_coordinates['Metro Station nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Metro Station", lat, lon, radius=5000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Metro Station nearby'] = venues_with_coordinates

companies_to_benchmark_with_coordinates['Metro Station Count'] = companies_to_benchmark_with_coordinates['Metro Station nearby'].apply(lambda x: len(x) if x is not None else 0)






companies_to_benchmark_with_coordinates['Night Club nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Night Club", lat, lon, radius=5000, limit=20)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Night Club nearby'] = venues_with_coordinates


companies_to_benchmark_with_coordinates['Night Club Count'] = companies_to_benchmark_with_coordinates['Night Club nearby'].apply(lambda x: len(x) if x is not None else 0)







#let's limit to 5 cause come on
companies_to_benchmark_with_coordinates['Strip Club nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Strip Club", lat, lon, radius=5000, limit=5)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframeStrip Club Club nearby'] = venues_with_coordinates
    companies_to_benchmark_with_coordinates.at[index, 'Strip Club nearby'] = venues_with_coordinates

companies_to_benchmark_with_coordinates['Strip Club Count'] = companies_to_benchmark_with_coordinates['Strip Club nearby'].apply(lambda x: len(x) if x is not None else 0)









companies_to_benchmark_with_coordinates['Cocktail Bar nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Cocktail Bar", lat, lon, radius=5000, limit=20)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Cocktail Bar nearby'] = venues_with_coordinates


companies_to_benchmark_with_coordinates['Cocktail Bar Count'] = companies_to_benchmark_with_coordinates['Cocktail Bar nearby'].apply(lambda x: len(x) if x is not None else 0)








companies_to_benchmark_with_coordinates['Vegan and Vegetarian Restaurant nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Vegan and Vegetarian Restaurant", lat, lon, radius=5000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Vegan and Vegetarian Restaurant nearby'] = venues_with_coordinates

companies_to_benchmark_with_coordinates['Vegan and Vegetarian Restaurant Count'] = companies_to_benchmark_with_coordinates['Vegan and Vegetarian Restaurant nearby'].apply(lambda x: len(x) if x is not None else 0)







companies_to_benchmark_with_coordinates['Basketball Stadium nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Basketball Stadium", lat, lon, radius=10000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Basketball Stadium nearby'] = venues_with_coordinates

companies_to_benchmark_with_coordinates['Basketball Stadium Count'] = companies_to_benchmark_with_coordinates['Basketball Stadium nearby'].apply(lambda x: len(x) if x is not None else 0)





companies_to_benchmark_with_coordinates['Pet Grooming Service nearby'] = None

# Iterate through the DataFrame jsut like the previous code
for index, row in companies_to_benchmark_with_coordinates.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    results = requests_for_foursquare("Pet Grooming Service", lat, lon, radius=5000, limit=10)
    venues = results.get('results', [])

    venues_with_coordinates = []

    for venue in venues:
        venue_name = venue.get('name', '') 

        geocodes = venue.get('geocodes', {}).get('main', {})
        venue_latitude = geocodes.get('latitude', None)
        venue_longitude = geocodes.get('longitude', None)

        if venue_name and venue_latitude is not None and venue_longitude is not None:
            venues_with_coordinates.append({
                'name': venue_name,
                'latitude': venue_latitude,
                'longitude': venue_longitude
            })

    #I am placing these results in my dataframe 
    companies_to_benchmark_with_coordinates.at[index, 'Pet Grooming Service nearby'] = venues_with_coordinates


companies_to_benchmark_with_coordinates['Pet Grooming Service Count'] = companies_to_benchmark_with_coordinates['Pet Grooming Service nearby'].apply(lambda x: len(x) if x is not None else 0)










#let's just reset the index so it's easier to work with and the columns, let's reorder them and remove duplicates
companies_to_benchmark_with_coordinates.reset_index(inplace=True,drop=True)
new_column_order = ["name","category_code","founded_year","latitude","longitude","Design Studios nearby",
                    "Design Studios Count","Starbucks nearby","Starbucks Count","Daycare nearby",
                    "Daycare Count","Airport nearby","Airport Count","Train nearby","Train Count",
                    "Metro Station nearby","Metro Station Count","Night Club nearby","Night Club Count",
                    "Strip Club nearby","Strip Club Count","Cocktail Bar nearby","Cocktail Bar Count",
                    "Vegan and Vegetarian Restaurant nearby","Vegan and Vegetarian Restaurant Count",
                    "Basketball Stadium nearby","Basketball Stadium Count","Pet Grooming Service nearby",
                    "Pet Grooming Service Count"]
companies_to_benchmark_with_coordinates = companies_to_benchmark_with_coordinates[new_column_order]
companies_to_benchmark_with_coordinates.drop_duplicates(subset=['name'],inplace=True)
companies_to_benchmark_with_coordinates.head()




#calculating average distances from points of interest to the companies:

import math

def haversine(coord1, coord2):
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    return meters

average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    daycares = row['Daycare nearby']
    total_distance = 0

    for daycare in daycares:
        daycare_coordinates = (daycare['latitude'], daycare['longitude'])
        distance = haversine(company_coordinates, daycare_coordinates)
        total_distance += distance

    if daycares:
        average_distance = total_distance / len(daycares)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average Daycare distance'] = average_distances




#for starbucks
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    starbucks = row['Starbucks nearby']
    total_distance = 0

    for starbucks in starbucks:
        starbucks_coordinates = (starbucks['latitude'], starbucks['longitude'])
        distance = haversine(company_coordinates, starbucks_coordinates)
        total_distance += distance

    if starbucks:
        average_distance = total_distance / len(starbucks)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average Starbucks distance'] = average_distances



#for design studios
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    design_studios = row['Design Studios nearby']
    total_distance = 0

    for studio in design_studios:
        studio_coordinates = (studio['latitude'], studio['longitude'])
        distance = haversine(company_coordinates, studio_coordinates)
        total_distance += distance

    if design_studios:
        average_distance = total_distance / len(design_studios)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average design_studios distance'] = average_distances




#Airport
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    airport = row['Airport nearby']
    total_distance = 0

    for airport in airport:
        airport_coordinates = (airport['latitude'], airport['longitude'])
        distance = haversine(company_coordinates, airport_coordinates)
        total_distance += distance

    if airport:
        average_distance = total_distance / len(airport)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average airport distance'] = average_distances




#Train
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    train = row['Train nearby']
    total_distance = 0

    for train in train:
        train_coordinates = (train['latitude'], train['longitude'])
        distance = haversine(company_coordinates, train_coordinates)
        total_distance += distance

    if train:
        average_distance = total_distance / len(train)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average train distance'] = average_distances




#Metro station
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    metro_station = row['Metro Station nearby']
    total_distance = 0

    for metro in metro_station:
        metro_coordinates = (metro['latitude'], metro['longitude'])
        distance = haversine(company_coordinates, metro_coordinates)
        total_distance += distance

    if metro_station:
        average_distance = total_distance / len(metro_coordinates)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average metro distance'] = average_distances




#Night Club
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    night_club = row['Night Club nearby']
    total_distance = 0

    for club in night_club:
        club_coordinates = (club['latitude'], club['longitude'])
        distance = haversine(company_coordinates, club_coordinates)
        total_distance += distance

    if night_club:
        average_distance = total_distance / len(night_club)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average night_club distance'] = average_distances



#Strip club
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    strip_club = row['Strip Club nearby']
    total_distance = 0

    for strip in strip_club:
        strip_coordinates = (strip['latitude'], strip['longitude'])
        distance = haversine(company_coordinates, strip_coordinates)
        total_distance += distance

    if strip_club:
        average_distance = total_distance / len(strip_club)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average strip_coordinates distance'] = average_distances



#Cocktail bar
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    cocktail_bar = row['Cocktail Bar nearby']
    total_distance = 0

    for cocktail in cocktail_bar:
        cocktail_coordinates = (cocktail['latitude'], cocktail['longitude'])
        distance = haversine(company_coordinates, cocktail_coordinates)
        total_distance += distance

    if cocktail_bar:
        average_distance = total_distance / len(cocktail_bar)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average cocktail_bar distance'] = average_distances



#Vegan rest
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    vegan_rest = row['Vegan and Vegetarian Restaurant nearby']
    total_distance = 0

    for vegan in vegan_rest:
        vegan_coordinates = (vegan['latitude'], vegan['longitude'])
        distance = haversine(company_coordinates, vegan_coordinates)
        total_distance += distance

    if vegan_rest:
        average_distance = total_distance / len(vegan_rest)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average vegan_rest distance'] = average_distances




#Basketball stadium
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    basket_stadium = row['Basketball Stadium nearby']
    total_distance = 0

    for basket in basket_stadium:
        basket_coordinates = (basket['latitude'], basket['longitude'])
        distance = haversine(company_coordinates, basket_coordinates)
        total_distance += distance

    if basket_stadium:
        average_distance = total_distance / len(basket_stadium)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average basket_stadium distance'] = average_distances



#Pet grooming
average_distances = []

for index, row in companies_to_benchmark_with_coordinates.iterrows(): #I'm getting the coordinates of the company
    company_coordinates = (row['latitude'], row['longitude'])
    pet_grooming = row['Pet Grooming Service nearby']
    total_distance = 0

    for pet in pet_grooming:
        pet_coordinates = (pet['latitude'], pet['longitude'])
        distance = haversine(company_coordinates, pet_coordinates)
        total_distance += distance

    if pet_grooming:
        average_distance = total_distance / len(pet_grooming)
    else:
        average_distance = None
    average_distances.append(average_distance)

companies_to_benchmark_with_coordinates['Average pet_grooming distance'] = average_distances




#attributing weights to the several criaterion and ranking companies:
import pandas as pd
import numpy as np

criteria_weights = {
    "Average Starbucks distance": 0.07,
    "Average design_studios distance": 0.1,
    "Average Daycare distance": 0.15,
    "Average airport distance": 0.1,
    "Average train distance": 0.13,
    "Average metro distance": 0.15,
    "Average night_club distance": 0.15,
    "Average strip_coordinates distance": 0.15,
    "Average cocktail_bar distance": 0.15,
    "Average vegan_rest distance": 0.15,
    "Average basket_stadium distance": 0.15,
    "Average pet_grooming distance": 0.15}

companies_to_benchmark_with_coordinates['Total Points'] = 0

# Loop through each criterion
for criterion, weight in criteria_weights.items():
    #I want companies that are closer to points of interest to receive more points for each criterion:
    companies_to_benchmark_with_coordinates = companies_to_benchmark_with_coordinates.sort_values(by=criterion, ascending=True)

    # I am creating a new column that's called basically
    #the name of the criterion and add "points" at the end of it.
    #I then calculate points for each company based on the inverse of the 
    #distance to the specific point of interest. Companies with shorter distances
    #receive higher points, while companies with longer distances receive fewer points
    companies_to_benchmark_with_coordinates[criterion + ' Points'] = 1 / companies_to_benchmark_with_coordinates[criterion]

    # replacing NaN  with 0 points cause these companies don't have this point of interest nearby
    companies_to_benchmark_with_coordinates[criterion + ' Points'] = companies_to_benchmark_with_coordinates[criterion + ' Points'].fillna(0)

    # Apply the weight to the points
    companies_to_benchmark_with_coordinates[criterion + ' Points'] = companies_to_benchmark_with_coordinates[criterion + ' Points'] * weight

    # Accumulate the criterion points to the Total Points (I multiply by 1000 cause otherwise the inverse of the distance 
    #would give me very little points)
    companies_to_benchmark_with_coordinates['Total Points'] += companies_to_benchmark_with_coordinates[criterion + ' Points']*1000

#this is the ordered ranking by points!
companies_to_benchmark_with_coordinates = companies_to_benchmark_with_coordinates.sort_values(by='Total Points', ascending=False)

#top 1 company should be this:
best_company = companies_to_benchmark_with_coordinates.iloc[0]

# Print the name of the best company
print(f"The best company is: {best_company['name']} with a total of {best_company['Total Points']} points!")


#final database to export:
companies_to_benchmark_with_coordinates.to_csv('../Data/benchmarking_companies.csv')


#new dataframe only with winner:
company_to_benchmark = companies_to_benchmark_with_coordinates.head(1)


#plotting on the map:
# Company's coordinates and the map
company_latitude = company_to_benchmark.iloc[0]["latitude"]
company_longitude = company_to_benchmark.iloc[0]["longitude"]
company_map = folium.Map(location=[company_latitude, company_longitude], zoom_start=15)

# here I am customizing the company's icon
company_icon = folium.Icon(
    icon="building-flag",
    prefix="fa",
    icon_color="black",
    color="white",
    icon_size=(40, 40)
)

# and here I am actually creating it
company_marker = folium.Marker(
    location=[company_latitude, company_longitude],
    icon=company_icon,
    popup='our Company is here!'
)
company_marker.add_to(company_map)

# These are the criteria I used in my dataframe classification and for each criteria I'll customize a marker
criteria_to_customize = [
    'Design Studios nearby',
    'Starbucks nearby',
    'Daycare nearby',
    'Airport nearby',
    'Train nearby',
    'Metro Station nearby',
    'Night Club nearby',
    'Strip Club nearby',
    'Cocktail Bar nearby',
    'Vegan and Vegetarian Restaurant nearby',
    'Basketball Stadium nearby',
    'Pet Grooming Service nearby'
]

for criterion in criteria_to_customize:
    # Retrieve the data associated with the current criterion
    places = company_to_benchmark.iloc[0][criterion]

    # Loop through the places for the current criterion
    for place in places:
        location = [place['latitude'], place['longitude']]
        name = place['name']

        # Customize the icon based on the criterion
        icon = None  # Initialize as None

        if criterion == 'Design Studios nearby':
            icon = folium.Icon(
                icon='pencil',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )
        elif criterion == 'Starbucks nearby':
            icon = folium.Icon(
                icon='mug-hot',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )
        elif criterion == 'Daycare nearby':
            icon = folium.Icon(
                icon='child',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )            
        elif criterion == 'Airport nearby':
            icon = folium.Icon(
                icon='plane-departure',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )              
        elif criterion == 'Train nearby':
            icon = folium.Icon(
                icon='train',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )       
        elif criterion == 'Metro Station nearby':
            icon = folium.Icon(
                icon='m',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )                   
        elif criterion == 'Night Club nearby':
            icon = folium.Icon(
                icon='moon',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )              
        elif criterion == 'Strip Club nearby':
            icon = folium.Icon(
                icon='eye-slash',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )  
        elif criterion == 'Cocktail Bar nearby':
            icon = folium.Icon(
                icon='martini-glass',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )       
        elif criterion == 'Vegan and Vegetarian Restaurant nearby':
            icon = folium.Icon(
                icon='seedling',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )                
        elif criterion == 'Basketball Stadium nearby':
            icon = folium.Icon(
                icon='basketball',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )                
        elif criterion == 'Pet Grooming Service nearby':
            icon = folium.Icon(
                icon='dog',
                prefix="fa",
                icon_color="white",
                color="darkblue"
            )                  
            
            
        if icon is not None:
            place_marker = folium.Marker(
                location=location,
                icon=icon,
                popup=name
            )
            place_marker.add_to(company_map)

# Display the map
company_map













