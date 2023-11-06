# Project-3
**Welcome to the readme for the 3rd Project of our Bootcamp! It's all about location location location**
![location!](https://media.giphy.com/media/5wWf7GMbT1ZUGTDdTqM/giphy.gif)

## 1 Context and introduction
This project will work around the location for our fabulous new company given some conditions we want to meet. Namely, hypothetically we are to find the best location for our company that is comprised of:

- 20 Designers
- 5 UI/UX Engineers
- 10 Frontend Developers
- 15 Data Engineers
- 5 Backend Developers
- 20 Account Managers
- 1 Maintenance guy that loves basketball
- 10 Executives
- 1 CEO/President

In the search for the best location possible we are to meet some criteria:
- Designers like to go to design talks and share knowledge. There must be some nearby companies that also do design.
- 30% of the company staff have at least 1 child.
- Developers like to be near successful tech startups that have raised at least 1 Million dollars.
- Executives like Starbucks A LOT. Ensure there's a starbucks not too far.
- Account managers need to travel a lot.
- Everyone in the company is between 25 and 40, give them some place to go party.
- The CEO is vegan.
- If you want to make the maintenance guy happy, a basketball stadium must be around 10 Km.
- The office dog—"Dobby" needs a hairdresser every month. Ensure there's one not too far away.

Several options are given to us as to how to approach this challenge - we can either work with a database of companies in MongoDB and from there locate the best one based on the said criteria; we can start from a blank page throwing a dart at the map and checking what's around and if it meets our criteria (or just about other approach as long as justified).

**I am taking the first approach - stealing a location from an existing comapany.**


## 2 The approach

For this project I will be importing:
- numpy
- pymongo
- pandas (our dearest pandas obv)
- requests
- json
- dotenv
- geopandas
- folium
- cartoframes

### What's my action plan?
I will be working with a collection of companies from MongoDB. My initial approach was to filter companies that are to be found in the categories: **analytics, ecommerce, games_video, software and web**. This is so because our company itself is a gaming company. On top of this I will be filtering for **companies founded after 2010** as I have interest in recent modern companies. This leaves us to a **total of 19 benchmarkable companies**.

From here, I will be querying [FourSquare's API](https://foursquare.com/developers/home) to answer to most of the criteria we were set to respect finding the coordinates for the points of interest around our company. Practical example:

- *30% of the company staff have at least 1 child* - this led me to find Daycare units in a radius of 10km around the location of each of the benchmarkbale company (if it exists)
- *The office dog—"Dobby" needs a hairdresser every month. Ensure there's one not too far away* - this led me to query for pet grooming businesses in a radius of 5 km around the benchmarkable companies.

**Finally** I will:
1. Attribute a weight to each of the criteria:

criteria_weights:
- Average Starbucks distance = 7% (cause executives assume an important role in the company)
- Average design_studios distance = 11% (cause developers account for a big portion of our headcount)
- Average Daycare distance = 16% (cause we are such a caring company)
- Average airport distance = 10% (accesses are important)
- Average train distance = 13% (same)
- Average metro distance = 15% (especially metro for being an inexpensive mtraportation method)
- Average night_club distance = 5% 
- Average strip_coordinates distance = 3% (let's not be prude)
- Average cocktail_bar distance = 4%
- Average vegan_rest distance = 6%
- Average basket_stadium distance = 4%
- Average pet_grooming distance = 6% 

The weights were constructed in a way that we can easily change them into replicating the analysis quickly and get different results immediately.

2. Rank the companies based on their proximity to the services (the bigger the distance, the less points they get)
3. Calculate a final score for each company and find a big winner

## 3 The findings
- Not every benchmarkable company had coordinates in our collection, so I dropped some of them.
- Not every company with coordinates has got all the services around it, so the ranking system turns to be even more relevant penalizing those and benefiting the ones "better" located
- The winning company which location we are stealing is called "Kidos" and its address takes us to NY (one would expect this): lat/long: 40.768058/-73.956599  founded in 2011.
- The final dataframe was exported into the Data folder in this project, and so was the html for the map with the plotting of our future location and the services around. There is also an image (static) to be found found there.

<iframe width="800" height="600" src="Figures/company_map.html"></iframe>

Guess we are going to New York.

###### New York City is known for its iconic skyline, and it's home to some of the world's most famous skyscrapers. One interesting fact is that the Empire State Building, one of the city's most iconic landmarks, has its own zip code, 10118. This zip code is exclusive to the building, and it receives more than 1,000 pieces of mail every day. It's a testament to the scale and importance of this historic skyscraper in the heart of Manhattan.















