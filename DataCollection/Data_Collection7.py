#!/usr/bin/env python
# coding: utf-8

# Import libraries
import os
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
import requests
from splinter import Browser
from requests import Session
from bs4 import BeautifulSoup as bs
import re
import json
from pprint import pprint

from datetime import datetime, date, time, timedelta
from time import sleep

import config

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# Fetch the service account key JSON file contents
cred = credentials.Certificate(config.firebase_file_path)
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': config.databaseURL
})


# Time variables
now = datetime.now()
year = now.strftime("%Y")
today = date.today()
today_full_date = today.strftime("%Y-%m-%d")
yesterday = date.today() - timedelta(days=1)
yesterday_year = yesterday.strftime("%Y")
yesterday_month_padding = yesterday.strftime("%m")
yesterday_month_no_padding = yesterday.strftime("%-m")
yesterday_full_date = yesterday.strftime("%Y-%m-%d")
yesterday_month_day = yesterday.strftime("%m_%d")
month_day_today = now.strftime("%m_%d")
month_day_yesterday = yesterday.strftime("%m_%d")


# In[35]:


data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "w+",
)
data_collection_log.write("----------------------------------------------")
data_collection_log.write(f"\nDATA COLLECTION LOG FOR {yesterday_full_date}")
data_collection_log.write("\n----------------------------------------------")


# # Init Browser

# In[31]:


# Start Browser
driver = webdriver.Chrome("/usr/local/bin/chromedriver")
sleep(5)

# Navigate to login page
driver.get("https://www.etsy.com/signin")
sleep(5)

try:
    # Populate sign in fields
    emailElem = driver.find_element_by_id("join_neu_email_field")
    emailElem.send_keys(config.email_address)

    sleep(5)

    passwordElem = driver.find_element_by_id("join_neu_password_field")
    passwordElem.send_keys(config.etsy_password)

    sleep(5)

    # Submit sign in information
    passwordElem.submit()

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Successful 1st Attempt Login")
    print("Successful 1st Attempt Login")
    sleep(5)


# If first login attempt is unsuccessful, refresh the page and make 2nd attempt.
except:
    # Navigate to login page
    driver.get("https://www.etsy.com/signin")
    sleep(5)

    # Populate sign in fields
    emailElem = driver.find_element_by_id("join_neu_email_field")
    emailElem.send_keys(config.email_address)
    sleep(5)

    passwordElem = driver.find_element_by_id("join_neu_password_field")
    passwordElem.send_keys(config.etsy_password)
    sleep(5)

    # Submit sign in information
    passwordElem.submit()
    sleep(5)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***SUCCESSFUL 2ND ATTEMPT LOGIN")
    print("Successful 2nd Attempt Login")


# # Scrape Favorites & Reviews




url = "https://www.etsy.com/your/shops/me/dashboard?ref=mcpa"

driver.get(url)
sleep(2)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")





# Button click count
r = 0

# Click button to reveal recent activity in activity panel
while r < 5:
    try:
        elm = driver.find_element_by_xpath(
            '//*[@id="recent-activity-content-region"]/div/div/span/button'
        )
        actions = ActionChains(driver)
        actions.move_to_element(elm).click().perform()
        sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(1)
        r += 1

    except:
        break





# ----------------- FAVORITES AND REVIEWS SCRAPE ------------------#
# Re-read HTML on page to included information revealed
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Find html in activity panel
activity_panel = soup.find("div", class_="activity-stream")

# Scrape favorites and reviews information from activity panel and append to lists
void = []
people = []
listing = []
date_liked = []

reviewer = []
date_reviewed = []

try:
    # Find unorder lists in activity panel
    for ul in activity_panel.find_all("ul"):
        # Find lists in unorder lists
        for li in ul.find_all("li"):

            # Split text in list
            for item in li:
                split_details = list(item.stripped_strings)

                # Only pull information from reviews
                if "left a review on your listing:" in split_details:
                    # Find shopper URL and append to list
                    link = item.find(
                        "a", href=re.compile("^https://www.etsy.com/people/")
                    )
                    reviewer.append(link["href"])

                    # Find date and append to list
                    date_format = "%Y-%m-%d"
                    date_of_favorite = item.find("span", class_="wt-text-caption").text

                    if date_of_favorite == "1 day ago":
                        date_value = date.today() - timedelta(days=1)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "2 days ago":
                        date_value = date.today() - timedelta(days=2)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "3 days ago":
                        date_value = date.today() - timedelta(days=3)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "4 days ago":
                        date_value = date.today() - timedelta(days=4)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "5 days ago":
                        date_value = date.today() - timedelta(days=5)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "6 days ago":
                        date_value = date.today() - timedelta(days=6)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "7 days ago":
                        date_value = date.today() - timedelta(days=7)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif "hours ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_reviewed.append(date_value)
                    elif "hour ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_reviewed.append(date_value)
                    else:
                        date_value = datetime.strptime(
                            date_of_favorite, "%b %d"
                        ).strftime(yesterday_year + "-%m-%d")
                        date_reviewed.append(date_value)

                if "left a review on your listing" in split_details:
                    # Find shopper URL and append to list
                    link = item.find(
                        "a", href=re.compile("^https://www.etsy.com/people/")
                    )
                    reviewer.append(link["href"])

                    # Find date and append to list
                    date_format = "%Y-%m-%d"
                    date_of_favorite = item.find("span", class_="wt-text-caption").text

                    if date_of_favorite == "1 day ago":
                        date_value = date.today() - timedelta(days=1)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "2 days ago":
                        date_value = date.today() - timedelta(days=2)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "3 days ago":
                        date_value = date.today() - timedelta(days=3)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "4 days ago":
                        date_value = date.today() - timedelta(days=4)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "5 days ago":
                        date_value = date.today() - timedelta(days=5)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "6 days ago":
                        date_value = date.today() - timedelta(days=6)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif date_of_favorite == "7 days ago":
                        date_value = date.today() - timedelta(days=7)
                        date_value = date_value.strftime(date_format)
                        date_reviewed.append(date_value)
                    elif "hours ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_reviewed.append(date_value)
                    elif "hour ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_reviewed.append(date_value)
                    else:
                        date_value = datetime.strptime(
                            date_of_favorite, "%b %d"
                        ).strftime(yesterday_year + "-%m-%d")
                        date_reviewed.append(date_value)

                # Only pull information from favorites
                if "favorited your item:" in split_details:

                    # Find shopper URL and append to list
                    link = item.find(
                        "a", href=re.compile("^https://www.etsy.com/people/")
                    )
                    people.append(link["href"])

                    # Find listing ID URL and append to list
                    link = item.find(
                        "a", href=re.compile("^https://www.etsy.com/listing/")
                    )
                    listing.append(link["href"])

                    # Find date and append to list
                    date_format = "%Y-%m-%d"
                    date_of_favorite = item.find("span", class_="wt-text-caption").text

                    if date_of_favorite == "1 day ago":
                        date_value = date.today() - timedelta(days=1)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif date_of_favorite == "2 days ago":
                        date_value = date.today() - timedelta(days=2)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif date_of_favorite == "3 days ago":
                        date_value = date.today() - timedelta(days=3)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif date_of_favorite == "4 days ago":
                        date_value = date.today() - timedelta(days=4)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif date_of_favorite == "5 days ago":
                        date_value = date.today() - timedelta(days=5)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif date_of_favorite == "6 days ago":
                        date_value = date.today() - timedelta(days=6)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif date_of_favorite == "7 days ago":
                        date_value = date.today() - timedelta(days=7)
                        date_value = date_value.strftime(date_format)
                        date_liked.append(date_value)
                    elif "hours ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_liked.append(date_value)
                    elif "hour ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_liked.append(date_value)
                    elif "minutes ago" in date_of_favorite:
                        date_value = yesterday_full_date
                        date_liked.append(date_value)
                    else:
                        date_value = datetime.strptime(
                            date_of_favorite, "%b %d"
                        ).strftime(yesterday_year + "-%m-%d")
                        date_liked.append(date_value)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Favorites and reviews scraped")
    print("Favorites and reviews scraped")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} ***ERROR: Favorites and reviews scrape"
    )
    print("***ERROR: Favorites and reviews scrape")





# ----------------- FAVORITES ------------------#

# Create temporary dataframe
favorites_temp = pd.DataFrame(
    {"listingLink": listing, "buyerLink": people, "dateLiked": date_liked}
)

# Turn all objects in dataframe to strings
favorites_temp = favorites_temp.applymap(str)

# Do the following if the dataframe is not empty
if favorites_temp.empty == False:

    # Extract listingID from listing link
    new = favorites_temp["listingLink"].str.split("/", expand=True)
    favorites_temp["listingID"] = new[4]

    # Extract buyerID from buyer link
    new2 = favorites_temp["buyerLink"].str.split("/", expand=True)
    favorites_temp["buyerID"] = new2[4]
    new3 = favorites_temp["buyerID"].str.split("?", n=1, expand=True)
    favorites_temp["buyerID"] = new3[0]

    # Create new df with clean data
    favorites = favorites_temp[["listingID", "buyerID", "dateLiked"]]

    # Fill n/a with whitespace
    favorites.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- favorites")
    print("DF Complete- favorites")
    # Append new favorites to database

    # Call firebase database
    fav_db = "favorites.json"
    r = requests.get(config.databaseURL + fav_db)
    r = r.json()

    # If database is not empty create df
    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)

    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR: Access Firebase Favorites"
        )
        print("***ERROR: Access Firebase Favorites")

    # Create tuples of data that already exisits in database
    favTuples = [
        (item.buyerID, item.dateLiked, item.listingID)
        for index, item in df_fb.iterrows()
    ]

    # Assign variable to database where information will be pushed
    ref = db.reference("favorites")

    # Count of items pushed to database
    count = 0

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    for index, item in favorites.iterrows():
        # Create tuples from local df
        var_o = item.buyerID, item.dateLiked, item.listingID

        if var_o not in favTuples:

            # Push item to db
            ref.push(item.to_dict())

            # Add to new favorites count
            count += 1

            # Convert tuples to string and place them in a text file
            tup = str(var_o).replace("(", "")
            str_tup = tup.replace(")", "")
            str_tup2 = str_tup.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/favorites.txt",
                "a",
            )
            txt_file.write(f"\n{str_tup2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to Favorites"
    )
    print(f"Firebase- {count} records added to Favorites")

else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- Favorites")
    print("DF EMPTY- Favorites")





# ----------------- REVIEWS ------------------#
# Create temporary dataframe
reviews_temp = pd.DataFrame({"reviewer": reviewer, "date_reviewed": date_reviewed})

# Turn all objects in dataframe to strings
reviews_temp = reviews_temp.applymap(str)





# Do the following if the dataframe is not empty
if reviews_temp.empty == False:

    # Extract buyerID from buyer link
    new2 = reviews_temp["reviewer"].str.split("/", expand=True)
    reviews_temp["buyerID"] = new2[4]
    new3 = reviews_temp["buyerID"].str.split("?", n=1, expand=True)
    reviews_temp["buyerID"] = new3[0]

    # Create new df with clean data
    reviews = reviews_temp[["buyerID", "date_reviewed"]]

    print(reviews)
    # Fill n/a with whitespace
    reviews.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- reviews")
    print("DF Complete- reviews")
    ## Append new reviews to database

    # Call firebase database
    reviews_db = "reviews.json"
    r = requests.get(config.databaseURL + reviews_db)
    r = r.json()

    # If database is not empty create df
    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR: Access Firebase Reviews"
        )
        print("ERROR: Access Firebase Reviews")

    # Create tuples of data that already exisits in database
    revTuples = [(item.buyerID, item.date_reviewed) for index, item in df_fb.iterrows()]

    # Assign variable to database where information will be pushed
    ref = db.reference("reviews")
    reviews.fillna("", inplace=True)

    # Count of items pushed to database
    count = 0

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    for index, item in reviews.iterrows():

        # Create tuples from local df
        var_o = item.buyerID, item.date_reviewed

        if var_o not in revTuples:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new favorites count
            count += 1

            # Convert tuples to string and place them in a text file
            tup = str(var_o).replace("(", "")
            str_tup = tup.replace(")", "")
            str_tup2 = str_tup.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/reviews.txt",
                "a",
            )
            txt_file.write(f"\n{str_tup2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to Reviews"
    )
    print(f"Firebase- {count} records added to Reviews")

else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- Reviews")
    print("DF EMPTY- Reviews")





# ----------------- REVIEWS2 ------------------#
# Scrape additional review information
url = "https://www.etsy.com/your/orders/sold/completed?ref=seller-platform-mcnav&page=1"

driver.get(url)
sleep(2)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")





email = []
orderID = []
buyer = []

try:
    for each in soup.find_all("div", class_="panel-body-row"):
        for item in each:
            split_details = list(item.stripped_strings)
            if "Review" in split_details:
                link = item.find(
                    "a",
                    href=re.compile(
                        "^https://www.etsy.com/shop/jetchcreations/reviews/"
                    ),
                )
                target_index = split_details.index("#")
                newList = split_details[: target_index + 2]
                orderNo = newList[-1]
                orderID.append(int(orderNo))
                buyerName = newList[0]
                buyer.append(buyerName)
                email_address = newList[-3]
                email.append(email_address)

    reviews2_df = pd.DataFrame({"orderID": orderID, "Name": buyer, "email": email})

    # Convert all objects in dataframe to strings and fill N/A with whitespace
    reviews2_df = reviews2_df.applymap(str)
    reviews2_df.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- reviews2_df")
    print("DF Complete- reviews2_df")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR: CREATING REVIEWS2_DF")
    print("***ERROR: CREATING REVIEWS2_DF")

# Do the following if the dataframe is not empty
if reviews2_df.empty == False:

    # Append new favorites to database
    # Call firebase database
    reviews2_db = "reviews2.json"
    r = requests.get(config.databaseURL + reviews2_db)
    r = r.json()

    # If database is not empty create df
    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)

    else:
        txt_file = open(
            "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/data_collection_log.txt",
            "a",
        )
        txt_file.write(f"\n{datetime.now()} ***ERROR: Access Firebase Reviews2")
        print("***ERROR: Access Firebase Reviews2")

    # Create tuples of data that already exisits in database
    reviewsTuples = [
        (item.email, item.Name, item.orderID) for index, item in df_fb.iterrows()
    ]

    # Assign variable to database where information will be pushed
    ref = db.reference("reviews2")

    # Count of items pushed to database
    count = 0

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    for index, item in reviews2_df.iterrows():
        # Create tuples from local df
        var_o = item.email, item.Name, item.orderID

        if var_o not in reviewsTuples:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new favorites count
            count += 1

            # Convert tuples to string and place them in a text file
            tup = str(var_o).replace("(", "")
            str_tup = tup.replace(")", "")
            str_tup2 = str_tup.replace("'", "")

            data_collection_log = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/reviews2.txt",
                "a",
            )
            data_collection_log.write(f"\n{str_tup2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to Reviews2"
    )
    print(f"Firebase- {count} records added to Reviews2")

else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- Reviews2")
    print("DF EMPTY- Reviews2")


# # Scrape - Listing Ids

# In[5]:


# ----------------- LISTING ID SCRAPE ------------------#

try:
    # # Scrape - Listing IDs
    # Create list for listing ids and query urls to gather stats for individual listings
    active_listing_ids = []
    active_listing_query_urls = []

    # Page with all active listing ids
    request_url = "https://www.etsy.com/your/shops/jetchcreations/tools/listings/view:table,stats:true"

    # Navigate to page with all active listing ids
    driver.get(request_url)

    sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    listings_page = soup.find_all("a", class_="display-block")

    # Scrape listings page for listing id and create query urls
    for listing in listings_page:
        if listing.has_attr("href"):
            listing_ids = listing["href"]
            if "/your/shops/jetchcreations/tools/listings/" in listing_ids:
                listing_id = listing_ids.replace(
                    "/your/shops/jetchcreations/tools/listings/", ""
                ).replace("?ref=listing_row_image&from_page=/your/listings", "")
                active_listing_ids.append(listing_id)

                query_url = (
                    "https://www.etsy.com/your/shops/me/stats/listings/"
                    + listing_id
                    + "?date_range=yesterday"
                )
                active_listing_query_urls.append(query_url)


    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Listing IDs scraped")
    print("Listing IDs Scraped")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR: LISTING ID SCRAPE")
    print("***ERROR: LISTING ID SCRAPE")

try:
    active_listings=pd.DataFrame({"listingID":active_listing_ids})
    db.reference('active_listings').delete()
    ref = db.reference('active_listings')
    [ref.push(item.to_dict()) for index, item in active_listings.iterrows()]
except:
    data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR: LISTING ID SCRAPE")
    print("***ERROR: ACTIVE LISTING ID FIREBASE")

# ## Scrape Listing Stats




# ----------------- LISTING STATS ------------------#

# # Scrape - Listing Stats
# Create lists to hold query information
visits = []
itemsSold = []
revenue = []
try:
    # Loop through listings to gather stats
    for link in active_listing_query_urls:
        driver.get(link)
        sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        visit_location = soup.find_all("div", class_="block-grid-item")

        counter = 0

        for i in visit_location:

            visit = i.find("div", class_="col-xs-7 pl-xs-0 pr-xs-0 text-right").text
            if counter == 0:
                visit = visit.replace(" visits", "").replace(" visit", "")
                visits.append(visit)
            if counter == 1:
                visit = visit.replace(" items sold", "").replace(" item sold", "")
                itemsSold.append(visit)
            if counter == 2:
                visit = visit.replace("$", "")
                revenue.append(visit)
            counter += 1
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Listing stats scraped")
    print("Listing Stats Scraped")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR: LISTING STATS SCRAPE")
    print("***ERROR: LISTING STATS SCRAPE")


# # Listing_Stats DF




# Create listing_stats_df
listing_stats_df = pd.DataFrame(
    {
        "listingID": active_listing_ids,
        "visits": visits,
        "sold": itemsSold,
        "revenue": revenue,
    }
)
listing_stats_df["record_date"] = yesterday_full_date

# Turn all objects in dataframe to strings and fill NAN with whitespace
listing_stats_df = listing_stats_df.applymap(str)
listing_stats_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_stats_df")
print("DF Complete- listing_stats_df")





# Do the following if the dataframe is not empty
if listing_stats_df.empty == False:

    # Call firebase database
    fb_db = "listing_stats.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    # If database is not empty create df
    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Firebase Listing_Stats"
        )
        print("***ERROR- Access Firebase Listing_Stats")

    # Create tuples of data that already exisits in database
    df_fb_tups = [
        (item.listingID, item.record_date, item.revenue, item.sold, item.visits)
        for index, item in df_fb.iterrows()
    ]

    # Assign variable to database where information will be pushed
    ref = db.reference("listing_stats")

    # Count of items pushed to database
    count = 0

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    for index, item in listing_stats_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date, item.revenue, item.sold, item.visits

        if var_o not in df_fb_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new favorites count
            count += 1

            # Convert tuples to string and place them in a text file
            tup = str(var_o).replace("(", "")
            str_tup = tup.replace(")", "")
            str_tup2 = str_tup.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_stats.txt",
                "a",
            )
            txt_file.write(f"\n{str_tup2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{now} Firebase- {count} records added to Listing_Stats"
    )
    print(f"Firebase- {count} records added to Listing_Stats")

else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR- LISTING STATS")
    print("***ERROR- Firebase Listing_Stats")


# ## Scrape Open Orders




# ----------------- OPEN ORDERS ------------------#

# # Scrape - Open Orders
# Create lists to hold query information
open_order_id = []
open_order_query_urls = []
ship_by_date = []
order_time = []

email = []
orderID = []
buyer = []

# Navigate to page
open_order_page_url = "https://www.etsy.com/your/orders/sold?ref=seller-platform-mcnav"

driver.get(open_order_page_url)
sleep(2)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Gather buyer contact information
try:
    for each in soup.find_all("div", class_="panel-body-row"):
        for item in each:
            split_details = list(item.stripped_strings)
            if "View user profile" in split_details:
                # Find index of generic item in list
                target_index = split_details.index("#")
                # Create new shorter list and then extract information needed
                newList = split_details[: target_index + 2]
                orderNo = newList[-1]
                orderID.append(orderNo)
                buyerName = newList[0]
                buyer.append(buyerName)
                email_address = newList[-3]
                email.append(email_address)

    buyer_contact = pd.DataFrame({"orderID": orderID, "Name": buyer, "email": email})

    # Convert all objects in dataframe to strings and fill N/A with whitespace
    buyer_contact = buyer_contact.applymap(str)
    buyer_contact.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- buyer_contact")
    print("DF Complete- buyer_contact")

    # Locate html to scrape
    open_orders_page = soup.find_all("div", class_="col-xs-12 col-md-8")

    for orders in open_orders_page:
        customer_name = orders.find("span", id="unsanitize")

    open_orders_page = soup.find_all(
        "h2", class_="col-xs-5 col-md-12 text-body-smaller text-gray"
    )

    # Loop through html to find order IDs to create URLS
    for orders in open_orders_page:
        open_order_url = orders.find("a", class_="text-gray")["href"]

        open_order_id_value = open_order_url.replace(
            "/your/orders/sold?ref=seller-platform-mcnav&order_id=", ""
        ).replace("/your/orders/sold?order_id=", "")
        open_order_id.append(open_order_id_value)

        open_order_url = "https://www.etsy.com" + open_order_url
        open_order_query_urls.append(open_order_url)

    # Loop through open order pages and append target info to lists
    for url in open_order_query_urls:

        driver.get(url)
        sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        tomorrow = date.today() + timedelta(days=1)

        ship_by_date_values = (
            soup.find(
                "div",
                class_="flag-img flag-img-right no-wrap text-right vertical-align-bottom hide-xs hide-sm",
            )
            .find("div", class_="strong")
            .text
        )

        ship_by_date_values = ship_by_date_values.replace("Ship by ", "")

        def validate(date_text):
            try:
                datetime.strptime(ship_by_date_values, "%b %d, %Y")
                return True
            except ValueError:
                return False

        if validate(ship_by_date_values) == True:
            d = datetime.strptime(ship_by_date_values, "%b %d, %Y")
        elif ship_by_date_values == "today":
            d = today
        else:
            d = tomorrow

        ship_by_date_values = d.strftime("%Y-%m-%d")

        ship_by_date.append(ship_by_date_values)

        order_date_values = (
            soup.find(
                "div",
                class_="flag-img flag-img-right no-wrap text-right vertical-align-bottom hide-xs hide-sm",
            )
            .find("div", class_="text-body-smaller mt-xs-1")
            .text
        )

        order_date_values = order_date_values.replace("Ordered ", "")
        order_date_values = order_date_values.strip(" ")
        d = datetime.strptime(order_date_values, "%I:%M%p, %a, %b %d, %Y")
        order_date_values = d.strftime("%m%d%y")
        order_time_values = d.strftime("%H:%M")
        order_time.append(order_time_values)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Open orders scraped")
    print("Open orders scraped")

    orders_df_temp2 = pd.DataFrame(
        {
            "orderID": open_order_id,
            "orderURL": open_order_query_urls,
            "shipByDate": ship_by_date,
            "orderTime": order_time,
        }
    )
    orders_df_temp2["record_date"] = yesterday

    # Turn all objects in dataframe to strings and replace NaN with whitespace
    orders_df_temp2 = orders_df_temp2.applymap(str)
    orders_df_temp2.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- orders_df_temp2")
    print("DF Complete- orders_df_temp2")

    open_orders_df = pd.merge(orders_df_temp2, buyer_contact, on="orderID", how="inner")

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- open_orders_df")
    print("DF Complete- open_orders_df")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR: OPEN ORDERS SCRAPE")
    print("***ERROR: OPEN ORDERS SCRAPE")


# ## Scrape Search Terms

# ## Search Terms DF




# ----------------- SEARCH TERMS ------------------#
# # Scrape - Search Terms
search_terms_list = []
search_terms_list2 = []
search_terms_list3 = []
search_terms_list4 = []
search_terms_count = []
try:
    request_url = "https://www.etsy.com/your/shops/me/stats/traffic?ref=seller-platform-mcnav&date_range=yesterday"

    driver.get(request_url)
    sleep(3)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    soup = BeautifulSoup(html, "lxml")

    table = soup.find_all("table")[0]

    tr_data = table.find_all("tr")

    for tr in tr_data[1:]:
        td = tr.find_all("td")
        row = [tr.text for tr in td]
        search_terms_list.append(row)

    # turn list of lists into a single list
    for sublist in search_terms_list:
        for item in sublist:
            search_terms_list2.append(item)

    # split: \d is a digit (a character in the range 0-9), and + means 1 or more times. So, \d+ is 1 or more digits.
    for l in search_terms_list2:
        simple = re.split("(\d+)", l)
        search_terms_list3.append(simple[0])
        search_terms_count.append(simple[-2])

    for string in search_terms_list3:
        string = re.sub("[^a-zA-Z.\d\s]", "", string)
        search_terms_list4.append(string)

    # remove leading and trailing spaces
    search_terms_list4 = [x.strip(" ") for x in search_terms_list4]

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Search terms scraped")
    print("Search terms scraped")

    search_terms_df = pd.DataFrame(
        {"searchTerms": search_terms_list4, "count": search_terms_count}
    )
    search_terms_df["record_date"] = yesterday_full_date
    # Turn all objects in dataframe to strings and fill NAN with whitespace
    search_terms_df = search_terms_df.applymap(str)
    search_terms_df.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- search_terms_df")
    print("DF Complete- search_terms_df")

    # Convert df to list
    items = search_terms_df.values.tolist()

    # Loop through each item in list
    for item in items:
        # Remove brackets form list and write to text file
        new_val = ", ".join(repr(e) for e in item)
        new_val2 = new_val.replace("'", "")

        txt_file = open(
            "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/search_terms.txt",
            "a",
        )
        txt_file.write(f"\n{new_val2}")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR: SEARCH TERMS SCRAPE")
    print("***ERROR: SEARCH TERMS SCRAPE")


# ## Scrape - CSV Downloads




# ----------------- CSV DOWNLOADS ------------------#
try:
    # # Scrape - Download CSV Files
    # Navigate to download page
    driver.get("https://www.etsy.com/your/shops/jetchcreations/download")
    # Select options from dropdown lists & submit to begin download
    # After download the page will refresh to prevent system notifications
    select = Select(driver.find_element_by_id("filter-csv-type"))
    select.select_by_value("transaction-level")

    select = Select(driver.find_element_by_id("filter-year"))
    select.select_by_value(yesterday_year)

    button = driver.find_element_by_id("order-csv-form")
    button.submit()

    sleep(5)
    driver.refresh()
    sleep(3)

    select = Select(driver.find_element_by_id("filter-csv-type"))
    select.select_by_value("payments-level")

    select = Select(driver.find_element_by_id("filter-year"))
    select.select_by_value(yesterday_year)

    button = driver.find_element_by_id("order-csv-form")
    button.submit()

    sleep(5)
    driver.refresh()
    sleep(3)

    select = Select(driver.find_element_by_id("filter-csv-type"))
    select.select_by_value("order-level")

    select = Select(driver.find_element_by_id("filter-year"))
    select.select_by_value(yesterday_year)

    button = driver.find_element_by_id("order-csv-form")
    button.submit()

    sleep(5)
    driver.refresh()
    sleep(3)

    select = Select(driver.find_element_by_id("filter-csv-type"))
    select.select_by_value("disbursements-level")

    select = Select(driver.find_element_by_id("filter-year"))
    select.select_by_value(yesterday_year)

    button = driver.find_element_by_id("order-csv-form")
    button.submit()

    sleep(10)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} CSV download complete")
    print("CSV download complete")
except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR- CSV DOWNLOAD")
    print("***ERROR- CSV DOWNLOAD")





try:
    # Read in CSVs to dataframes
    sold_orders_file_path = (
        f"/Users/jessicaetchechury/Downloads/EtsySoldOrders{yesterday_year}.csv"
    )
    sold_orders_df = pd.read_csv(sold_orders_file_path)
    # Convert data types to string
    sold_orders_df = sold_orders_df.applymap(str)

    sold_order_items_file_path = (
        f"/Users/jessicaetchechury/Downloads/EtsySoldOrderItems{yesterday_year}.csv"
    )
    sold_order_items_df = pd.read_csv(sold_order_items_file_path)
    # Convert data types to string
    sold_order_items_df = sold_order_items_df.applymap(str)

    direct_checkout_payments_file_path = f"/Users/jessicaetchechury/Downloads/EtsyDirectCheckoutPayments{yesterday_year}.csv"
    direct_checkout_payments_df = pd.read_csv(direct_checkout_payments_file_path)
    # Convert data types to string
    direct_checkout_payments_df = direct_checkout_payments_df.applymap(str)

    deposits_file_path = (
        f"/Users/jessicaetchechury/Downloads/EtsyDeposits{yesterday_year}.csv"
    )
    deposits_df = pd.read_csv(deposits_file_path)
    # Convert data types to string
    deposits_df = deposits_df.applymap(str)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} CSV to pandas df complete")
    print("CSV to pandas df complete")

    # Move CSVs to storage
    os.rename(
        f"/Users/jessicaetchechury/Downloads/EtsySoldOrders{yesterday_year}.csv",
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/CSV_Downloads/EtsySoldOrders{yesterday_full_date}.csv",
    )
    os.rename(
        f"/Users/jessicaetchechury/Downloads/EtsyDirectCheckoutPayments{yesterday_year}.csv",
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/CSV_Downloads/EtsyDirectCheckoutPayments{yesterday_full_date}.csv",
    )
    os.rename(
        f"/Users/jessicaetchechury/Downloads/EtsySoldOrderItems{yesterday_year}.csv",
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/CSV_Downloads/EtsySoldOrderItems{yesterday_full_date}.csv",
    )
    os.rename(
        f"/Users/jessicaetchechury/Downloads/EtsyDeposits{yesterday_year}.csv",
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/CSV_Downloads/EtsyDeposits{yesterday_full_date}.csv",
    )

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} CSV transfer complete")
    print("CSV transfer complete")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR- CSV TO PANDAS DF")
    print("***ERROR- CSV TO PANDAS DF")


# ## Scrape Revenue




# ----------------- REVENUE ------------------#
try:
    # Scrape Revenue
    url = "https://www.etsy.com/your/account/payments?ref=seller-platform-mcnav"

    driver.get(url)
    sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    sales_credits = driver.find_element_by_xpath(
        '//*[@id="root"]/div/div[3]/div/div[4]/div/div[2]/div[1]/div/div[1]/div[2]/h4/span/span[2]'
    ).text

    fees_taxes = driver.find_element_by_xpath(
        '//*[@id="root"]/div/div[3]/div/div[4]/div/div[2]/div[2]/div/div[1]/div[2]/h4/span/span/span[2]'
    ).text

    orderRevenue = []
    orderNet = float(sales_credits) - float(fees_taxes)

    orderRevenue.append(orderNet)

    orderNet_df = pd.DataFrame({"orderNet": orderRevenue})
    orderNet_df["date"] = today.strftime("%Y-%m-%d")

    # Convert all objects in dataframe to strings and fill NaN with whitespace
    orderNet_df = orderNet_df.applymap(str)
    orderNet_df.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- orderNet_df")
    print("DF Complete- orderNet_df")

    # Do the following if the dataframe is not empty
    if orderNet_df.empty == False:

        # Append new favorites to database

        # Call firebase database
        fb_db = "order_net.json"
        r = requests.get(config.databaseURL + fb_db)
        r = r.json()

        # If database is not empty create df
        if r:
            data = [r[i] for i in r]
            df_fb = pd.DataFrame.from_dict(data, orient="columns")
            df_fb = df_fb.applymap(str)

        else:
            data_collection_log = open(
                f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
                "a",
            )
            data_collection_log.write(
                f"\n{datetime.now()} ***ERROR- Acess Firebase Order_Net"
            )
            print("***ERROR- Acess Firebase Order_Net")

        # Create tuples of data that already exisits in database
        df_fb_tups = [(item.date, item.orderNet) for index, item in df_fb.iterrows()]

        # Assign variable to database where information will be pushed
        ref = db.reference("order_net")

        # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
        for index, item in orderNet_df.iterrows():
            # Create tuples from local df
            var_o = item.date, item.orderNet
            if var_o not in df_fb_tups:
                # Push item to db
                ref.push(item.to_dict())

                # Convert tuples to string and place them in a text file
                tup = str(var_o).replace("(", "")
                str_tup = tup.replace(")", "")
                str_tup2 = str_tup.replace("'", "")

                txt_file = open(
                    "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/order_net.txt",
                    "a",
                )
                txt_file.write(f"\n{str_tup2}")

            else:
                data_collection_log = open(
                    "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/order_net.txt",
                    "a",
                )
                data_collection_log.write(
                    f"\n{datetime.now()} Order_net already in database"
                )
                print("Order_net already in database")
except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR- ORDER NET")
    print("***ERROR- ORDER NET")


# ## API CALL




# ----------------- API CALL ------------------#

# # API Call - Listing Images
image_listing_id = []
listing_image_id = []
listing_image_url_fullxfull = []
listing_image_rank = []

try:
    for listing in active_listing_ids:
        query_url = (
            "https://openapi.etsy.com/v2/listings/"
            + listing
            + "/images?api_key="
            + config.api_key
        )
        listing_images_query = requests.get(query_url).json()

        try:
            listing_images_results = listing_images_query["results"]

            for item in listing_images_results:
                for key, value in item.items():
                    if key == "listing_image_id":
                        listing_image_id.append(value)
                    if key == "url_fullxfull":
                        listing_image_url_fullxfull.append(value)
                    if key == "listing_id":
                        image_listing_id.append(value)
                    if key == "rank":
                        listing_image_rank.append(value)

        except (KeyError, IndexError):
            print("error")

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Listing images scraped")
    print("Listing information scraped")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} ***ERROR- Listing images Scrape")
    print("***ERROR- Listing Images Scrape")





# # API Call - Listing Inforamtion
listing_id = []
state = []
category_id = []
listing_title = []
title = []
description = []
date_created = []
date_expires = []
last_modified = []
price = []
quantity = []
tags = []
category_path = []
shop_section_id = []
listing_url = []
shipping_template_id = []
processing_min = []
processing_max = []
item_weight = []
item_weight_unit = []
item_length = []
item_width = []
item_height = []
item_dimensions_unit = []
occasion = []
is_customizable = []
is_digital = []
has_variations = []
views = []
num_favorites = []

try:
    for listing in active_listing_ids:

        query_url = (
            "https://openapi.etsy.com/v2/listings/"
            + listing
            + "?api_key="
            + config.api_key
        )

        listing_info_query = requests.get(query_url).json()

        try:
            listing_info_results = listing_info_query["results"]

            for item in listing_info_results:

                for key, value in item.items():
                    if key == "views":
                        views.append(value)
                    if key == "num_favorers":
                        num_favorites.append(value)
                    if key == "listing_id":
                        listing_id.append(value)
                    if key == "state":
                        state.append(value)
                    if key == "category_id":
                        category_id.append(value)
                    if key == "title":
                        listing_title.append(value)
                    if key == "description":
                        description.append(value)
                    if key == "creation_tsz":
                        date_created.append(value)
                    if key == "ending_tsz":
                        date_expires.append(value)
                    if key == "last_modified_tsz":
                        last_modified.append(value)
                    if key == "price":
                        price.append(value)
                    if key == "quantity":
                        quantity.append(value)
                    if key == "tags":
                        tags.append(value)
                    if key == "category_path":
                        category_path.append(value)
                    if key == "shop_section_id":
                        shop_section_id.append(value)
                    if key == "url":
                        listing_url.append(value)
                    if key == "shipping_template_id":
                        shipping_template_id.append(value)
                    if key == "processing_min":
                        processing_min.append(value)
                    if key == "processing_max":
                        processing_max.append(value)
                    if key == "item_weight":
                        item_weight.append(value)
                    if key == "item_weight_unit":
                        item_weight_unit.append(value)
                    if key == "item_length":
                        item_length.append(value)
                    if key == "item_width":
                        item_width.append(value)
                    if key == "item_height":
                        item_height.append(value)
                    if key == "item_dimensions_unit":
                        item_dimensions_unit.append(value)
                    if key == "occasion":
                        occasion.append(value)
                    if key == "is_customizable":
                        is_customizable.append(value)
                    if key == "is_digital":
                        is_digital.append(value)
                    if key == "has_variations":
                        has_variations.append(value)

        except (KeyError, IndexError):
            print("error")

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} Listing information scraped")
    print("Listing information scraped")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} ***ERROR- Listing Information Scrape"
    )
    print("***ERROR- Listing Information Scrape")


# ## Listing_IDs DF




# Create listing_id_df
listing_id_df = pd.DataFrame({"listingID": active_listing_ids, "title": listing_title})
listing_id_df["title"] = listing_id_df["title"].str.split(": ").str[1]

listing_id_df = listing_id_df.applymap(str)
listing_id_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_id_df")
print("DF Complete- listing_id_df")





# Do the following if the dataframe is not empty
if listing_id_df.empty == False:

    # Only push new records
    listingIds_db = "listing_ids.json"
    r = requests.get(config.databaseURL + listingIds_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_id_df"
        )
        print("***ERROR- Acess Firebase listing_id_df")

    listingIdsTuples = [
        (item.listingID, item.title) for index, item in df_fb.iterrows()
    ]

    ref = db.reference("listing_ids")

    # New record count
    count = 0
    new_ListingID = []
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    for index, item in listing_id_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.title

        if var_o not in listingIdsTuples:
            # Push item to db
            ref.push(item.to_dict())
            # Add to new record count
            count += 1
            # Convert tuples to string and place them in a text file
            tup = str(var_o).replace("(", "")
            str_tup = tup.replace(")", "")
            str_tup2 = str_tup.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_ids.txt",
                "a",
            )
            txt_file.write(f"\n{str_tup2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to Listing_IDs"
    )
    print(f"Firebase- {count} records added to Listing_IDs")

else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- Listing_IDs")
    print("DF EMPTY- Listing_IDs")





# Create dataframe of new listingIDs to be added to listing creation database
try:
    listing_id_creation_df = pd.DataFrame({"ListingID": new_ListingID})
    listing_id_creation_df["OriginallyCreated"] = yesterday_full_date

    # Convert all objects in dataframe to strings and fill N/A with whitespace
    listing_id_creation_df = listing_id_creation_df.applymap(str)
    listing_id_creation_df.fillna("", inplace=True)

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_id_creation_df")
    print("DF Complete- listing_id_creation_df")

except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} ***ERROR: DF- listing_id_creation_df"
    )
    print("***ERROR: DF- listing_id_creation_df")


if listing_id_creation_df.empty == False:
    fb_db = "listing_creation_dates.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_creation_dates"
        )
        print("***ERROR- Acess Firebase listing_creation_dates")

    df_tups = [
        (item.ListingID, item.OriginallyCreated) for index, item in df_fb.iterrows()
    ]

    ref = db.reference("listing_creation_dates")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in listing_id_creation_df.iterrows():

        # Create tuples from local df
        var_o = item.ListingID, item.OriginallyCreated

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_creation.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")
            print(new_val2)
        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to listing_creation_dates"
    )
    print(f"Firebase- {count} records added to listing_creation_dates")

else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- listing_id_creation_df")
    print("DF EMPTY- listing_id_creation_df")


# # Listing_Info DF




# Create listing_info_df
listing_info_df = pd.DataFrame(
    {
        "listingID": active_listing_ids,
        "listingTitle": listing_title,
        "state": state,
        "digital": is_digital,
        "customizable": is_customizable,
        "variations": has_variations,
        "dateCreated": date_created,
        "dateExpires": date_expires,
        "lastModified": last_modified,
        "url": listing_url,
    }
)


listing_info_df["dateCreated"] = pd.to_datetime(
    listing_info_df["dateCreated"], unit="s"
)
listing_info_df["dateCreated"] = listing_info_df["dateCreated"].dt.strftime("%Y-%m-%d")

listing_info_df["dateExpires"] = pd.to_datetime(
    listing_info_df["dateExpires"], unit="s"
)
listing_info_df["dateExpires"] = listing_info_df["dateExpires"].dt.strftime("%Y-%m-%d")

listing_info_df["lastModified"] = pd.to_datetime(
    listing_info_df["lastModified"], unit="s"
)
listing_info_df["lastModified"] = listing_info_df["lastModified"].dt.strftime(
    "%Y-%m-%d"
)

listing_info_df["record_date"] = yesterday_full_date

listing_info_df = listing_info_df.applymap(str)
listing_info_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_info_df")
print("DF Complete- listing_info_df")





# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if listing_info_df.empty == False:
    fb_db = "listing_info.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_info_df"
        )
        print("***ERROR- Acess Firebase listing_info_df")

    df_tups = [(item.listingID, item.record_date) for index, item in df_fb.iterrows()]

    ref = db.reference("listing_info")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in listing_info_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_info.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to Listing_IDs"
    )
    print(f"Firebase- {count} records added to Listing_IDs")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- Listing_Info")
    print("DF EMPTY- Listing_Info")


# # List_Shipping DF




listing_shipping_df = pd.DataFrame(
    {
        "listingID": active_listing_ids,
        "shippingTemplateID": shipping_template_id,
        "itemWeight": item_weight,
        "itemWeightUnit": item_weight_unit,
        "itemLength": item_length,
        "itemWidth": item_width,
        "itemHeight": item_height,
        "itemDimensionalUnit": item_dimensions_unit,
    }
)

listing_shipping_df["record_date"] = yesterday_full_date

listing_shipping_df = listing_shipping_df.applymap(str)
listing_shipping_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_shipping_df")
print("DF Complete- listing_shipping_df")





# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if listing_shipping_df.empty == False:
    fb_db = "listing_shipping.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_shipping"
        )
        print("***ERROR- Acess Firebase listing_shipping")

    df_tups = [(item.listingID, item.record_date) for index, item in df_fb.iterrows()]

    ref = db.reference("listing_shipping")

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    # New record count
    count = 0

    for index, item in listing_shipping_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_shipping.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to listing_shipping"
    )
    print(f"Firebase- {count} records added to listing_shipping")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- listing_shipping")
    print("DF EMPTY- listing_shipping")


# # Listing_Images df




listing_images_df = pd.DataFrame(
    {
        "listingID": image_listing_id,
        "listingImageID": listing_image_id,
        "listingImageURL": listing_image_url_fullxfull,
        "listingImageRank": listing_image_rank,
    }
)

listing_images_df["record_date"] = yesterday_full_date

listing_images_df = listing_images_df.applymap(str)
listing_images_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_images_df")
print("DF Complete- listing_images_df")





# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if listing_images_df.empty == False:
    fb_db = "listing_images.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_images"
        )
        print("***ERROR- Acess Firebase listing_images")

    df_tups = [(item.listingID, item.record_date) for index, item in df_fb.iterrows()]

    ref = db.reference("listing_images")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in listing_images_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_images.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to Listing_Images"
    )
    print(f"Firebase- {count} records added to Listing_Images")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- Listing_Images")
    print("DF EMPTY- Listing_Images")


# # Listing_Categories df




listing_categorical_df = pd.DataFrame(
    {
        "listingID": active_listing_ids,
        "categoryID": category_id,
        "shopSectionID": shop_section_id,
        "occasion": occasion,
    }
)
listing_categorical_df["record_date"] = yesterday_full_date

listing_categorical_df = listing_categorical_df.applymap(str)
listing_categorical_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_categorical_df")
print("DF Complete- listing_categorical_df")








# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if listing_categorical_df.empty == False:
    fb_db = "listing_categories.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_categories"
        )
        print("***ERROR- Acess Firebase listing_categories")

    df_tups = [(item.listingID, item.record_date) for index, item in df_fb.iterrows()]

    ref = db.reference("listing_categories")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in listing_categorical_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_categories.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to listing_categories"
    )
    print(f"Firebase- {count} records added to listing_categories")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- listing_categorical_df")
    print("DF EMPTY- listing_categorical_df")


# # Listing_tags DF




# Create listing tags dataframe
listing_tags_df = pd.DataFrame({"listingID": active_listing_ids, "tags": tags})
# Split list of tags into columns
listing_tags_df = listing_tags_df.assign(
    **pd.DataFrame(listing_tags_df.tags.values.tolist()).add_prefix("tag_")
)
# Melt dataframe to reduce amount of columns
listing_tags_df = pd.melt(
    listing_tags_df,
    id_vars=["listingID"],
    value_vars=[
        "tag_0",
        "tag_1",
        "tag_2",
        "tag_3",
        "tag_4",
        "tag_5",
        "tag_6",
        "tag_7",
        "tag_8",
        "tag_9",
        "tag_10",
        "tag_11",
        "tag_12",
    ],
)
# Drop any rows that do not have a tag
listing_tags_df = listing_tags_df.dropna(axis=0, subset=["value"])
# Rename value column to tag
listing_tags_df = listing_tags_df.rename(columns={"value": "tag"})
# Drop tags column
listing_tags_df = listing_tags_df[["listingID", "tag"]]

listing_tags_df["record_date"] = yesterday_full_date

listing_tags_df = listing_tags_df.applymap(str)
listing_tags_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- listing_tags_df")
print("DF Complete- listing_tags_df")








# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if listing_tags_df.empty == False:
    fb_db = "listing_tags.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase listing_tags"
        )
        print("***ERROR- Acess Firebase listing_tags")

    df_tups = [(item.listingID, item.record_date) for index, item in df_fb.iterrows()]

    ref = db.reference("listing_tags")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in listing_tags_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/listing_tags.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to listing_tags"
    )
    print(f"Firebase- {count} records added to listing_tags")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- listing_tags_df")
    print("DF EMPTY- listing_tags_df")


# # Production_et DF




production_time_df = pd.DataFrame(
    {
        "listingID": active_listing_ids,
        "processingTimeMin": processing_min,
        "processingTimeMax": processing_max,
    }
)

production_time_df["record_date"] = yesterday_full_date

production_time_df = production_time_df.applymap(str)
production_time_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- production_time_df")
print("DF Complete- production_time_df")








# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if production_time_df.empty == False:
    fb_db = "production_et.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase production_et"
        )
        print("***ERROR- Acess Firebase production_et")

    df_tups = [(item.listingID, item.record_date) for index, item in df_fb.iterrows()]

    ref = db.reference("production_et")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in production_time_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.record_date

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/production_et.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to production_et"
    )
    print(f"Firebase- {count} records added to production_et")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- production_time_df")
    print("DF EMPTY- production_time_df")


# # Order_items

# Drop columns not needed for database table
order_sold_items_df = sold_order_items_df[
    ["Order ID", "Transaction ID", "Listing ID", "Quantity", "Variations"]
]
order_sold_items_df = order_sold_items_df.rename(
    columns={
        "Order ID": "orderID",
        "Transaction ID": "transactionID",
        "Listing ID": "listingID",
        "Quantity": "quantity",
        "Variations": "variations",
    }
)

order_sold_items_df["record_date"] = yesterday_full_date

order_sold_items_df = order_sold_items_df.applymap(str)
order_sold_items_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- order_sold_items_df")
print("DF Complete- order_sold_items_df")



# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if order_sold_items_df.empty == False:
    fb_db = "order_items.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)

    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase order_items"
        )
        print("***ERROR- Acess Firebase order_items")

    df_tups = [(item.listingID, item.orderID) for index, item in df_fb.iterrows()]

    ref = db.reference("order_items")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in order_sold_items_df.iterrows():

        # Create tuples from local df
        var_o = item.listingID, item.orderID
        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/order_items.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to order_items"
    )
    print(f"Firebase- {count} records added to order_items")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- order_sold_items_df")
    print("DF EMPTY- order_sold_items_df")


# # Buyers DF


try:
    # Rename columns that will be used
    sold_orders_df2 = sold_orders_df.rename(
        columns={
            "Sale Date": "orderDate",
            "Order ID": "orderID",
            "Buyer User ID": "buyerID",
            "First Name": "firstName",
            "Last Name": "lastName",
            "Date Shipped": "dateShipped",
            "Street 1": "street1",
            "Street 2": "street2",
            "Ship City": "city",
            "Ship State": "state",
            "Ship Zipcode": "zipCode",
            "Ship Country": "country",
            "Order Value": "orderValue",
            "Coupon Code": "couponCode",
            "Coupon Details": "details",
            "Discount Amount": "discountAmount",
            "Shipping Discount": "shippingDiscount",
            "Shipping": "shipping",
            "Sales Tax": "salesTax",
            "Order Total": "orderTotal",
            "Card Processing Fees": "fees",
            "Order Net": "orderNet",
            "Adjusted Order Total": "adjustedTotal",
            "Adjusted Card Processing Fees": "adjustedFees",
            "Adjusted Net Order Amount": "adjustedNet",
            "Order Type": "orderType",
            "Payment Type": "paymentType",
        }
    )
except:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} ***ERROR: Unable to rename sold_orders_df columns"
    )
    print("***ERROR: Unable to rename sold_orders_df columns")



buyers_df = sold_orders_df2[["orderID", "buyerID", "firstName", "lastName"]]


buyer_info_df = pd.merge(buyers_df, buyer_contact, on="orderID", how="outer")
buyer_info_df = buyer_info_df.drop(["Name"], axis=1)
buyer_info_df


buyer_info_df["record_date"] = yesterday_full_date

buyer_info_df = buyer_info_df.applymap(str)
buyer_info_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- buyer_info_df")
print("DF Complete- buyer_info_df")

# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if buyer_info_df.empty == False:
    fb_db = "buyers.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase buyer_info_df"
        )
        print("***ERROR- Acess Firebase buyer_info_df")

    df_tups = [(item.buyerID, item.orderID) for index, item in df_fb.iterrows()]

    ref = db.reference("buyers")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in buyer_info_df.iterrows():

        # Create tuples from local df
        var_o = item.buyerID, item.orderID

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/buyers.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to buyers"
    )
    print(f"Firebase- {count} records added to buyers")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- buyer_info_df")
    print("DF EMPTY- buyer_info_df")


# # Shipping_Addresses DF

shipping_addresses_df = sold_orders_df2[
    ["buyerID", "city", "country", "orderID", "state", "street1", "street2", "zipCode"]
]

shipping_addresses_df = shipping_addresses_df.applymap(str)
shipping_addresses_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- shipping_addresses_df")
print("DF Complete- shipping_addresses_df")


# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if shipping_addresses_df.empty == False:
    fb_db = "shipping_addresses.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase shipping_addresses_df"
        )
        print("***ERROR- Acess Firebase shipping_addresses_df")

    df_tups = [(item.buyerID, item.orderID) for index, item in df_fb.iterrows()]

    ref = db.reference("shipping_addresses")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in shipping_addresses_df.iterrows():

        # Create tuples from local df
        var_o = item.buyerID, item.orderID

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/shipping_addresses.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to shipping_addresses"
    )
    print(f"Firebase- {count} records added to shipping_addresses")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- shipping_addresses_df")
    print("DF EMPTY- shipping_addresses_df")


## Orders DF

# Create data frame from CSV
orders_df_temp1 = sold_orders_df2[["orderID", "orderDate", "buyerID"]]

# Only return open orders
orders_df = pd.merge(orders_df_temp1, orders_df_temp2, on="orderID", how="outer")

orders_df = orders_df[
    ["orderID", "orderDate", "orderTime", "shipByDate", "buyerID", "orderURL"]
]

orders_df["orderDate"] = pd.to_datetime(
    orders_df["orderDate"], format="%m/%d/%y", errors="coerce"
).dt.strftime("%Y-%m-%d")

orders_df = orders_df.applymap(str)
orders_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- orders_df")
print("DF Complete- orders_df")



# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if orders_df.empty == False:
    fb_db = "orders.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(f"\n{datetime.now()} ***ERROR- Acess Firebase orders")
        print("***ERROR- Acess Firebase orders")

    orderIDs_ = df_fb.orderID.values

    ref = db.reference("orders")

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database
    # New record count
    count = 0

    for index, item in orders_df.iterrows():
        if item.orderID not in orderIDs_:
            # push
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/orders.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")
            txt_file.close()

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to orders"
    )
    print(f"Firebase- {count} records added to orders")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- orders_df")
    print("DF EMPTY- orders_df")


# # Order_shipped DF

orders_shipped_df = sold_orders_df2[["orderID", "dateShipped"]]
# delete rows that contain NaN/null - only want to import complete records
orders_shipped_df2 = orders_shipped_df[
    ~orders_shipped_df.dateShipped.str.contains("nan")
]
orders_shipped_df3 = orders_shipped_df2.applymap(str)
orders_shipped_df3.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- orders_shipped_df")
print("DF Complete- orders_shipped_df")



# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if orders_shipped_df3.empty == False:
    fb_db = "order_shipped.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase order_shipped"
        )
        print("***ERROR- Acess Firebase order_shipped")

    df_tups = [(item.orderID, item.dateShipped) for index, item in df_fb.iterrows()]

    ref = db.reference("order_shipped")
    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    for index, item in orders_shipped_df3.iterrows():

        # Create tuples from local df
        var_o = item.orderID, item.dateShipped

        if var_o not in df_tups:
            # Push item to db
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/order_shipped.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")
            txt_file.close()

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to order_shipped"
    )
    print(f"Firebase- {count} records added to order_shipped")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- orders_shipped_df3")
    print("DF EMPTY- orders_shipped_df3")


# # Order_pay df

order_payment_df_temp1 = direct_checkout_payments_df[["Order ID", "Gift Card Applied?"]]
order_payment_df_temp1 = order_payment_df_temp1.rename(
    columns={"Order ID": "orderID", "Gift Card Applied?": "giftCard"}
)
order_payment_df_temp2 = sold_orders_df2[
    [
        "orderID",
        "orderValue",
        "couponCode",
        "discountAmount",
        "shippingDiscount",
        "shipping",
        "salesTax",
        "orderTotal",
        "fees",
        "orderNet",
        "orderType",
        "paymentType",
    ]
]
# Join data frames on orderID
order_payment_df = pd.merge(
    order_payment_df_temp2, order_payment_df_temp1, on="orderID", how="outer"
)

order_payment_df = order_payment_df.applymap(str)
order_payment_df.fillna("", inplace=True)

data_collection_log = open(
    f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
    "a",
)
data_collection_log.write(f"\n{datetime.now()} DF Complete- order_payment_df")
print("DF Complete- order_payment_df")



# Only push new records
order_pay_db = "order_pay.json"
r = requests.get(config.databaseURL + order_pay_db)
r = r.json()

if r:
    data = [r[i] for i in r]
    df_fb = pd.DataFrame.from_dict(data, orient="columns")



# Check that records for the day have not already been added
# Do the following if the dataframe is not empty
if order_payment_df.empty == False:
    fb_db = "order_pay.json"
    r = requests.get(config.databaseURL + fb_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        df_fb = pd.DataFrame.from_dict(data, orient="columns")
        df_fb = df_fb.applymap(str)
    else:
        data_collection_log = open(
            f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
            "a",
        )
        data_collection_log.write(
            f"\n{datetime.now()} ***ERROR- Acess Firebase order_pay"
        )
        print("***ERROR- Acess Firebase order_pay")

    # Compare tuples from Firebase database and tuples from local df.  Only add tuples that do not already exist in Firebase database

    # New record count
    count = 0

    orderIDs_ = df_fb.orderID.values

    ref = db.reference("order_pay")

    for index, item in order_payment_df.iterrows():
        if item.orderID not in orderIDs_:
            # push
            ref.push(item.to_dict())

            # Add to new record count
            count += 1

            items = item.values.tolist()

            new_val = ", ".join(repr(e) for e in items)

            new_val2 = new_val.replace("'", "")

            txt_file = open(
                "/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/Data/order_pay.txt",
                "a",
            )
            txt_file.write(f"\n{new_val2}")

        else:
            pass

    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(
        f"\n{datetime.now()} Firebase- {count} records added to order_pay"
    )
    print(f"Firebase- {count} records added to order_pay")


else:
    data_collection_log = open(
        f"/Users/jessicaetchechury/Desktop/JEtchCreationsDashboard/DataCollection/logs/{yesterday_full_date}_data_collection_log.txt",
        "a",
    )
    data_collection_log.write(f"\n{datetime.now()} DF EMPTY- order_payment_df")
    print("DF EMPTY- order_payment_df")

driver.quit()
