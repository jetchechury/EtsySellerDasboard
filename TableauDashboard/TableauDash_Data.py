#!/usr/bin/env python
# coding: utf-8


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import pandas as pd

import dateutil.parser as dparser

import pygsheets

from datetime import datetime, date, time, timedelta

import requests

import config




# Fetch the service account key JSON file contents
cred = credentials.Certificate(config.firebase_file_path)
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {"databaseURL": config.databaseURL})


# Call firebase database
fb_file = "listing_stats.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    listing_stats = pd.DataFrame.from_dict(data, orient="columns")

# else:
#     data_collection_log= open(f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt","a")
#     data_collection_log.write(f"\n{datetime.now()} ***ERROR: Access Firebase Reviews")
#     print("ERROR: Access Firebase Reviews")



for index, item in listing_stats.iterrows():
    date_formatted = dparser.parse(item.record_date, fuzzy=True).date()
    listing_stats.loc[index, "date"] = date_formatted



listing_stats = listing_stats.astype(
    {"listingID": "int", "revenue": "float", "sold": "int", "visits": "int"}
)
listing_stats = listing_stats[["listingID", "date", "revenue", "sold", "visits"]]


listingStats_date = listing_stats.groupby(["date"]).sum()
listingStats_date = listingStats_date.reset_index()
listingStats_date = listingStats_date[["date", "revenue", "sold", "visits"]]


# Call firebase database
fb_file = "favorites.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    favorites = pd.DataFrame.from_dict(data, orient="columns")




for index, item in favorites.iterrows():
    date_formatted = dparser.parse(item.dateLiked, fuzzy=True).date()
    favorites.loc[index, "date"] = date_formatted

favorites = favorites.astype({"listingID": "int"})
favorites = favorites[["date", "listingID"]]

favorites_date = favorites.groupby(["date"]).count()
favorites_date = favorites_date.rename(columns=({"listingID": "total_favorites"}))
favorites_date = favorites_date.reset_index()

comp_listing_stats_date = pd.merge(
    listingStats_date, favorites_date, on="date", how="inner"
)
print (comp_listing_stats_date.head())

gc = pygsheets.authorize(
    service_file=config.google_api_file_path
)
sh = gc.open("J Etch Creations Dashboard")
wks = sh.worksheet("title", "Listing_Stats_Date")
wks.clear()
wks.set_dataframe(comp_listing_stats_date, (1, 1))


listingStats_ID = listing_stats.groupby(["listingID"]).sum()
listingStats_ID = listingStats_ID.reset_index()


favorites_ID = favorites.groupby(["listingID"]).count()
favorites_ID = favorites_ID.rename(columns=({"date": "total_favorites"}))
favorites_ID = favorites_ID.reset_index()


comp_listing_stats_ID = pd.merge(
    listingStats_ID, favorites_ID, on="listingID", how="inner"
)


# Call firebase database
fb_file = "listing_ids.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    listing_titles = pd.DataFrame.from_dict(data, orient="columns")

listing_titles = listing_titles.astype({"listingID": "int"})



comp_listing_stats_ID = pd.merge(
    comp_listing_stats_ID, listing_titles, on="listingID", how="inner"
)


favorites_sum = comp_listing_stats_ID["total_favorites"].sum(axis=0, skipna=True)

for index, item in comp_listing_stats_ID.iterrows():
    d = (item.total_favorites / favorites_sum) * 100
    comp_listing_stats_ID.loc[index, "% of favorites"] = d



revenue_sum = comp_listing_stats_ID["revenue"].sum(axis=0, skipna=True)

for index, item in comp_listing_stats_ID.iterrows():
    d = (item.revenue / revenue_sum) * 100
    comp_listing_stats_ID.loc[index, "% of revenue"] = d




sold_sum = comp_listing_stats_ID["sold"].sum(axis=0, skipna=True)

for index, item in comp_listing_stats_ID.iterrows():
    d = (item.sold / sold_sum) * 100
    comp_listing_stats_ID.loc[index, "% of sales"] = d



visits_sum = comp_listing_stats_ID["visits"].sum(axis=0, skipna=True)

for index, item in comp_listing_stats_ID.iterrows():
    d = (item.visits / visits_sum) * 100
    comp_listing_stats_ID.loc[index, "% of visits"] = d




# Call firebase database
fb_file = "listing_creation_dates.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    listing_creation_dates = pd.DataFrame.from_dict(data, orient="columns")

listing_creation_dates = listing_creation_dates.rename(
    columns=({"ListingID": "listingID"})
)
listing_creation_dates = listing_creation_dates.astype({"listingID": "int"})
listing_creation_dates = listing_creation_dates.drop_duplicates()



comp_listing_stats_ID = pd.merge(
    comp_listing_stats_ID, listing_creation_dates, on="listingID", how="inner"
)



now = datetime.now()
comp_listing_stats_ID["OriginallyCreated"] = pd.to_datetime(
    comp_listing_stats_ID["OriginallyCreated"], format="%Y-%m-%d"
)



for index, item in comp_listing_stats_ID.iterrows():
    age = (now - item.OriginallyCreated).total_seconds()
    d = age // 86400
    comp_listing_stats_ID.loc[index, "age"] = d

print(comp_listing_stats_ID.head())

gc = pygsheets.authorize(
    service_file=config.google_api_file_path
)
sh = gc.open("J Etch Creations Dashboard")
wks = sh.worksheet("title", "Listing_Stats_ID_Hist")
wks.clear()
wks.set_dataframe(comp_listing_stats_ID, (1, 1))



# Call firebase database
fb_file = "active_listings.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    active_listings = pd.DataFrame.from_dict(data, orient="columns")

active_listings = active_listings.astype({"listingID": "int"})




comp_act_listing_stats_ID = pd.merge(
    comp_listing_stats_ID, active_listings, on="listingID", how="inner"
)


comp_act_listing_stats_ID = comp_act_listing_stats_ID.sort_values(
    by="title", ascending=True
)
comp_act_listing_stats_ID = comp_act_listing_stats_ID.reset_index()

print (comp_act_listing_stats_ID.head())

gc = pygsheets.authorize(
    service_file=config.google_api_file_path
)
sh = gc.open("J Etch Creations Dashboard")
wks = sh.worksheet("title", "Listing_Stats_ID_Active")
wks.clear()
wks.set_dataframe(comp_act_listing_stats_ID, (1, 1))

# Call firebase database
fb_file = "orders.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    orders = pd.DataFrame.from_dict(data, orient="columns")

orders = orders.astype({"orderID": "int"})

# Call firebase database
fb_file = "order_shipped.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    order_shipped = pd.DataFrame.from_dict(data, orient="columns")

order_shipped = order_shipped.astype({"orderID": "int"})


order_info = pd.merge(orders, order_shipped, on="orderID", how="outer")


# Call firebase database
fb_file = "order_pay.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    order_pay = pd.DataFrame.from_dict(data, orient="columns")

order_pay = order_pay.astype({"orderID": "int"})


order_info = pd.merge(order_info, order_pay, on="orderID", how="outer")


# Call firebase database
fb_file = "shipping_addresses.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    shipping_addresses = pd.DataFrame.from_dict(data, orient="columns")

shipping_addresses = shipping_addresses.astype({"orderID": "int"})
shipping_addresses = shipping_addresses.drop(columns=["buyerID"])


order_info = pd.merge(order_info, shipping_addresses, on="orderID", how="outer")




order_info = order_info[
    [
        "orderDate",
        "orderID",
        "orderTime",
        "orderURL",
        "shipByDate",
        "dateShipped",
        "couponCode",
        "discountAmount",
        "fees",
        "giftCard",
        "orderNet",
        "orderTotal",
        "orderType",
        "orderValue",
        "paymentType",
        "salesTax",
        "shipping",
        "shippingDiscount",
        "buyerID",
        "city",
        "country",
        "state",
        "zipCode",
    ]
]
print(order_info.head())


gc = pygsheets.authorize(
    service_file=config.google_api_file_path
)
sh = gc.open("J Etch Creations Dashboard")
wks = sh.worksheet("title", "Orders")
wks.clear()
wks.set_dataframe(order_info, (1, 1))

# Call firebase database
fb_file = "order_items.json"
r = requests.get(config.databaseURL + fb_file)
r = r.json()

# If database is not empty create df
if r:
    data = [r[i] for i in r]
    order_items = pd.DataFrame.from_dict(data, orient="columns")

order_items = order_items.astype({"orderID": "int"})


search_terms = pd.read_csv(
    "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/search_terms.txt",
    sep=",",
    header=None,
)


new_header = search_terms.iloc[0]  # grab the first row for the header
search_terms = search_terms[1:]  # take the data less the header row
search_terms.columns = new_header  # set the header row as the df header



search_terms = search_terms.applymap(lambda x: x.replace("'", ""))
search_terms = search_terms.groupby(["searchTerms"]).count()
search_terms = search_terms.reset_index()
search_terms = search_terms[["searchTerms", "count"]]

print(search_terms.head())


gc = pygsheets.authorize(
    service_file=config.google_api_file_path
)
sh = gc.open("J Etch Creations Dashboard")
wks = sh.worksheet("title", "Search_Terms")
wks.clear()
wks.set_dataframe(search_terms, (1, 1))



import numpy as np
from scipy.stats import beta

# Get data from database
listingStatsDB = "listing_stats.json"
r = requests.get(config.databaseURL + listingStatsDB)
r = r.json()
# style_in_html = ""
# data_in_html = ""
if r:
    data = [r[i] for i in r]
    listing_stats_df = pd.DataFrame.from_dict(data, orient="columns")

listing_stats_df = listing_stats_df.astype(
    {"listingID": int, "revenue": float, "sold": int, "visits": int}
)


# Get data from database
listingCreationDB = "listing_creation_dates.json"
r = requests.get(config.databaseURL + listingCreationDB)
r = r.json()
# style_in_html = ""
# data_in_html = ""
if r:
    data = [r[i] for i in r]
    listing_creation_df = pd.DataFrame.from_dict(data, orient="columns")

listing_creation_df = listing_creation_df.astype({"ListingID": int})

listing_creation_df = listing_creation_df.drop_duplicates()


listing_creation_df["OriginallyCreated"] = pd.to_datetime(
    listing_creation_df["OriginallyCreated"]
)

# Get data from database
activeListingsDB = "active_listings.json"
r = requests.get(config.databaseURL + activeListingsDB)
r = r.json()
# style_in_html = ""
# data_in_html = ""
if r:
    data = [r[i] for i in r]
    active_listings_df = pd.DataFrame.from_dict(data, orient="columns")

active_listings_df = active_listings_df.astype({"listingID": int})



from datetime import datetime, date, time, timedelta


listingIDs = active_listings_df["listingID"]
from pytz import timezone

now = datetime.now()
now = timezone("US/Central").localize(now)


listingIDsAll = []
creationDateAll = []
listingViewsAll = []
totalSiteViewsAll = []
avg_views_day = []
max_views_day = []
min_views_day = []
editURLs = []
daysActive = []

for listing in listingIDs:
    # sort listing stats by listing
    listingIDsAll.append(listing)

    editURL = f"https://www.etsy.com/your/shops/jetchcreations/tools/listings/view:table,stats:true/{listing}"
    editURLs.append(editURL)

    stats_by_listing = listing_stats_df.loc[listing_stats_df["listingID"] == listing, :]

    # find the sum of views for the listing
    listingViews = stats_by_listing["visits"].sum()
    listingViewsAll.append(listingViews)

    # find the creation date for listing
    creation_date_by_listings = listing_creation_df.loc[
        listing_creation_df["ListingID"] == listing, :
    ]
    creation_date_by_listings = creation_date_by_listings.reset_index(drop=True)
    creationDate = creation_date_by_listings["OriginallyCreated"][0]
    creationDate = timezone("US/Central").localize(creationDate)
    creationDate = creationDate + timedelta(hours=5)
    creationDateAll.append(creationDate)

    noDaysSinceCreation = now - creationDate

    noDaysSinceCreation = noDaysSinceCreation / np.timedelta64(1, "D")

    daysActive.append(noDaysSinceCreation)

    # find total site views since the listing was created
    for index, item in listing_stats_df.iterrows():
        try:
            record_date = datetime.strptime(item.record_date, "%m/%d/%y")
            record_date = timezone("US/Central").localize(record_date)

            record_date = record_date + timedelta(hours=5)

            listing_stats_df.loc[index, "record_date_local"] = record_date
        except:
            record_date = datetime.strptime(item.record_date, "%Y-%m-%d")
            record_date = timezone("US/Central").localize(record_date)

            record_date = record_date + timedelta(hours=5)

            listing_stats_df.loc[index, "record_date_local"] = record_date

    total_views_since_creation = listing_stats_df.loc[
        listing_stats_df["record_date_local"] >= creationDate
    ]

    # find the sum of views for the listing
    total_views_since_creation = total_views_since_creation.astype({"visits": int})

    totalSiteViews = total_views_since_creation["visits"].sum()
    totalSiteViewsAll.append(totalSiteViews)

    averageViewsPerListingPerDay = 0.85
    averageViewsPerDay = 28.5

    averageViewsPerListingPerDay / averageViewsPerDay

    priorScale = 7  # one week
    priorAlpha = (
        averageViewsPerListingPerDay * priorScale
    )  # average views per listing per day (success)
    priorBeta = (
        averageViewsPerDay * priorScale
    ) - priorAlpha  # average total views per day minus average listing views (failures)

    scale = 1  # scale to make graph pretty

    posteriorAlpha = priorAlpha + listingViews
    posteriorBeta = priorBeta + (totalSiteViews - listingViews)

    ntrials = 10000
    sample = beta.rvs(posteriorAlpha, posteriorBeta, scale=scale, size=ntrials)

    avg_views_day1 = (np.mean(sample) / scale) * averageViewsPerDay
    avg_views_day.append(avg_views_day1)
    min_views_day1 = (np.quantile(sample, 0.025) / scale) * averageViewsPerDay
    min_views_day.append(min_views_day1)
    max_views_day1 = (np.quantile(sample, 0.975) / scale) * averageViewsPerDay
    max_views_day.append(max_views_day1)

bayes_df = pd.DataFrame(
    {
        "listingID": listingIDsAll,
        "creationDate": creationDateAll,
        "listingViews": listingViewsAll,
        "totalSiteViews": totalSiteViewsAll,
        "avg_views_day": avg_views_day,
        "max_views_day": max_views_day,
        "min_views_day": min_views_day,
        "edit_url": editURLs,
        "days_active": daysActive,
    }
)

bayes_df["curr_views_day"] = (bayes_df.listingViews / bayes_df.totalSiteViews) * 28.5



bayes_df = pd.merge(bayes_df, listing_titles, on="listingID", how="inner")


print (bayes_df.head())

gc = pygsheets.authorize(
    service_file=config.google_api_file_path
)
sh = gc.open("J Etch Creations Dashboard")
wks = sh.worksheet("title", "Bayes")
wks.clear()
wks.set_dataframe(bayes_df, (1, 1))





