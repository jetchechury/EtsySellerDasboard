import config

import os, time

import pandas as pd
import numpy as np
from scipy.stats import beta

from flask import Flask, jsonify, render_template

from datetime import datetime, date, time, timedelta
from time import sleep
from pytz import timezone


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests


app = Flask(__name__)

# time.strftime('%X %x %Z')
# os.environ['TZ'] = 'US/Central'
# time.tzset()

# Fetch the service account key JSON file contents
cred = credentials.Certificate(config.firebase_file_path)
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': config.databaseURL
})


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/open_orders")
def openOrders():
    orders_db = "orders.json"
    r = requests.get(config.databaseURL + orders_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        orders_df = pd.DataFrame.from_dict(data, orient="columns")

    orders_df = orders_df.astype({"orderID": int})

    orderShipped_db = "order_shipped.json"
    r = requests.get(config.databaseURL + orderShipped_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        orders_shipped_df = pd.DataFrame.from_dict(data, orient="columns")

    orders_shipped_df = orders_shipped_df.astype({"orderID": int})

    order_2 = pd.merge(orders_df, orders_shipped_df, on="orderID", how="outer")

    buyers_db = "buyers.json"
    r = requests.get(config.databaseURL + buyers_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        buyers_df = pd.DataFrame.from_dict(data, orient="columns")

    buyers_df = buyers_df.astype({"orderID": int})

    buyers_df["lastInitial"] = buyers_df["lastName"].astype(str).str[0]
    buyers_df["firstThree"] = buyers_df["firstName"].astype(str).str[:3]

    buyers_df["name"] = buyers_df["firstThree"] + " " + buyers_df["lastInitial"]

    buyers_df = buyers_df[["name", "orderID"]]

    open_orders = pd.merge(buyers_df, order_2, on="orderID", how="inner")

    open_orders['orderDate'] = pd.to_datetime(open_orders['orderDate'])

    # open_orders['shipByDate'] = pd.to_datetime(open_orders['shipByDate'])

    open_orders_df = open_orders.loc[open_orders["dateShipped"].isnull()]

    # open_orders_df['processing_time'] = open_orders_df['shipByDate_local'].sub(open_orders_df['orderDate_local'], axis=0)

    now = datetime.now()
    now = timezone('US/Central').localize(now)

    open_orders_df['now'] = now

    for index, item in open_orders_df.iterrows():
        shipByDate = datetime.strptime(item.shipByDate, "%Y-%m-%d")
        shipByDate = timezone('US/Central').localize(shipByDate)

        shipByDate =shipByDate + timedelta(hours=22)

        open_orders_df.loc[index,'shipByDate_local']=shipByDate

    for index, item in open_orders_df.iterrows():
        timeLeft2=(item.shipByDate_local-item.now).total_seconds()
        d = int(timeLeft2//86400)
        h = int((timeLeft2%86400)//3600)
        open_orders_df.loc[index,'timeLeft']=f"{d} days {h} hours"

    open_orders_df = open_orders_df.sort_values(by="shipByDate", ascending=True)

    open_orders = []

    for index, item in open_orders_df.iterrows():
        openOrderDict={}
        openOrderDict['abuyerName']=item[0]
        openOrderDict['borderDate']=item[3].strftime('%m/%d/%y')
        openOrderDict['cshipByDate']=item[10].strftime('%m/%d/%y')
        openOrderDict['dtimeLeft']=str(item[-1])
        openOrderDict['eorderURL']=str(item[5])
        open_orders.append(openOrderDict)

    return jsonify(open_orders)


@app.route("/order_stats")
def orderStats():
    now = datetime.now()
    now = timezone('US/Central').localize(now)

    nowMonth=now.month
    nowYear=now.year
    nowMonth

    today=datetime.today()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=1)
    lastMonthYear=lastMonth.year
    lastMonthMonth=lastMonth.month


    orders_db = "orders.json"
    r = requests.get(config.databaseURL + orders_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        orders_df = pd.DataFrame.from_dict(data, orient='columns')
    orders_df = orders_df.astype({"orderID": int})

    orders_df=orders_df[['orderID','orderDate']]

    orderShipped_db = "order_shipped.json"
    r = requests.get(config.databaseURL + orderShipped_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        orders_shipped_df= pd.DataFrame.from_dict(data, orient='columns')
    orders_shipped_df = orders_shipped_df.astype({"orderID": int})

    order_2=pd.merge(orders_df,orders_shipped_df,on='orderID',how='outer')

    order_2['orderDate'] =  pd.to_datetime(order_2['orderDate'])
    order_2['dateShipped'] =  pd.to_datetime(order_2['dateShipped'], format='%m/%d/%y')
    order_2["month"] = order_2['orderDate'].map(lambda x: x.month)
    order_2["year"] = order_2['orderDate'].map(lambda x: x.year)

    prep_time = order_2[pd.notnull(order_2['dateShipped'])]

    prep_time["prepTime"] = prep_time["dateShipped"].sub(prep_time["orderDate"], axis=0)
    prep_time['prepTime'] = prep_time['prepTime'] / np.timedelta64(1, 'D')


    prepTimePrev = prep_time.loc[prep_time['month'] == lastMonthMonth,:]

    prepTimeAvg_prev=prepTimePrev['prepTime'].mean()

    prepTimeCur = prep_time.loc[prep_time['month'] == nowMonth,:]

    prepTimeAvg_cur=prepTimeCur['prepTime'].mean()

    prepTimeDiff=(prepTimeAvg_cur/prepTimeAvg_prev)*100
    prepTimeDiff=str(round(prepTimeDiff,1))
    prepTimeDiff=f"last month {prepTimeAvg_prev} days"

    prepTimeAvg_cur=round(prepTimeAvg_cur,1)

    prepTime=[]

    prepTime.append(f"{prepTimeAvg_cur} days")
    prepTime.append(prepTimeDiff)

    order_count3 = order_2.loc[order_2['year'] == nowYear,:]
    order_count_now = order_count3.loc[order_count3['month'] == nowMonth,:]


    orderCount=[]
    count_cur=order_count_now['orderID'].count()

    count_cur=int(count_cur)

    order_count4 = order_2.loc[order_2['year'] == lastMonthYear,:]
    order_count_lm = order_count4.loc[order_count4['month'] == lastMonthMonth,:]

    count_prev=order_count_lm['orderID'].count()

    count_prev = int(count_prev)

    count_diff=(count_cur/count_prev)*100

    count_cur=str(count_cur)

    count_diff=str(round(count_diff,1))
    count_diff=f"{count_diff}%"

    orderCount.append(count_cur)
    orderCount.append(count_diff)

    orderNet = "order_net.json"
    r = requests.get(config.databaseURL + orderNet)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        orderNet_df2= pd.DataFrame.from_dict(data, orient='columns')

    orderNet_df2["date"] = pd.to_datetime(orderNet_df2["date"])
    orderNet_df2 = orderNet_df2.astype({"orderNet": float})

    orderNet_df2["month"] = orderNet_df2['date'].map(lambda x: x.month)
    orderNet_df2["year"] = orderNet_df2['date'].map(lambda x: x.year)

    orderNet_df2 = orderNet_df2.groupby(['year','month'], as_index=False)['orderNet'].max()

    orderNet_df3 = orderNet_df2.loc[orderNet_df2['month'] == lastMonthMonth,:]

    orderNet_df4 = orderNet_df2.loc[orderNet_df2['month'] == nowMonth,:]

    net_prev=orderNet_df3.iloc[0]['orderNet']
    net_cur=orderNet_df4.iloc[0]['orderNet']

    orderNetdiff=(net_cur/net_prev)*100

    order_net_diff=str(round(orderNetdiff,1))

    order_net_diff=f"{order_net_diff}%"

    orderNetAmt=orderNet_df4.iloc[0]['orderNet']
    orderNetAmt=str(orderNetAmt)

    orderNet=[]
    orderNet.append(f"${orderNetAmt}")
    orderNet.append(order_net_diff)

    order_stats_df=pd.DataFrame({'avgOrderTime':prepTime,
                        'orderCount':orderCount,
                        'orderNet':orderNet})

    order_stats=[]

    for index, item in order_stats_df.iterrows():
        orderStatsDict={}
        orderStatsDict['avgOrderTime']=item[0]
        orderStatsDict['orderCount']=item[1]
        orderStatsDict['orderRevenue']=item[2]

        order_stats.append(orderStatsDict)

    return jsonify(order_stats)

@app.route("/list_stats")
def listStats():
    listing_stats_db = "listing_stats.json"
    r = requests.get(config.databaseURL + listing_stats_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        listingstats_df = pd.DataFrame.from_dict(data, orient='columns')

    listingstats_df['record_date']= pd.to_datetime(listingstats_df['record_date'])

    listingstats_df["record_date_local"] = listingstats_df.record_date.dt.tz_localize('US/Central')

    listingstats_df['week'] = listingstats_df['record_date_local'].dt.week

    listingstats_df=listingstats_df.sort_values(by='week',ascending=False)

    listingstats_df = listingstats_df.astype({"visits": int, "sold": int, 'revenue':float})

    cur_week_no=listingstats_df.iloc[0]['week']

    cur_week_stats=listingstats_df.loc[listingstats_df['week'] == cur_week_no,:]

    visits=[]

    cur_week_stats = cur_week_stats.astype({"visits": int, "sold": int, 'revenue':int})

    cur_visits_perweek=cur_week_stats['visits'].sum()

    prev_week_no=cur_week_no-1
    prev_week_stats=listingstats_df.loc[listingstats_df['week'] == prev_week_no,:]

    prev_visits_perweek=prev_week_stats['visits'].sum()

    visits_diff=(cur_visits_perweek/prev_visits_perweek)*100
    visits_diff = str(round(visits_diff, 1))

    visits.append(str(cur_visits_perweek))
    visits.append(visits_diff+'%')

    favs_db = "favorites.json"
    r = requests.get(config.databaseURL + favs_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        favs_df = pd.DataFrame.from_dict(data, orient='columns')

    favs_df['dateLiked']= pd.to_datetime(favs_df['dateLiked'])

    favs_df["dateLiked_local"] = favs_df.dateLiked.dt.tz_localize('US/Central')

    favs_df['week'] = (favs_df['dateLiked_local'] + pd.DateOffset(days=1)).dt.week
    cur_week_favs=favs_df.loc[favs_df['week'] == cur_week_no,:]

    cur_wk_fav_count=cur_week_favs['buyerID'].count()

    prev_week_favs=favs_df.loc[favs_df['week'] == prev_week_no,:]
    prev_wk_fav_count=prev_week_favs['buyerID'].count()

    wk_fav_diff=(cur_wk_fav_count/prev_wk_fav_count)*100
    wk_fav_diff = str(round(wk_fav_diff, 1))

    favs=[]

    favs.append(str(cur_wk_fav_count))
    favs.append(wk_fav_diff+'%')

    listing_stats_df=pd.DataFrame({'visitsPerWeek':visits,
                                 'favsPerWeek':favs})

    list_stats=[]

    for index, item in listing_stats_df.iterrows():
        stats={}
        stats['avisitsPerWeek']=item[0]
        stats['favsPerWeek']=(item[1])

        list_stats.append(stats)

    return jsonify(list_stats)

@app.route("/pending_reviews")
def pendingReviews():
    reviews_db = "reviews.json"
    r = requests.get(config.databaseURL + reviews_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        review_df = pd.DataFrame.from_dict(data, orient='columns')


    orders_db = "orders.json"
    r = requests.get(config.databaseURL + orders_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        order_df = pd.DataFrame.from_dict(data, orient='columns')
    order_df = order_df.astype({"orderID": int})

    orderShipped_db = "order_shipped.json"
    r = requests.get(config.databaseURL + orderShipped_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        orders_shipped_df = pd.DataFrame.from_dict(data, orient="columns")

    orders_shipped_df = orders_shipped_df.astype({"orderID": int})


    order_2 = pd.merge(order_df, orders_shipped_df, on="orderID", how="inner")


    reviews2_db = "reviews2.json"
    r = requests.get(config.databaseURL + reviews2_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        reviews2_df = pd.DataFrame.from_dict(data, orient='columns')
    reviews2_df = reviews2_df.astype({"orderID": int})


    df2=pd.merge(reviews2_df,order_2,on='orderID',how='outer')

    df3=pd.merge(review_df,df2,on='buyerID',how='outer')

    df3=df3[['buyerID','date_reviewed','orderID','orderURL','orderDate','dateShipped']]

    df3['date_reviewed'].fillna(0, inplace=True)
    df3['status']=''
    df3.loc[df3['date_reviewed'] == 0, ['status']] = 'pending'

    pending_reviews=df3.loc[df3['status']=='pending',:]

    buyers_db = "buyers.json"
    r = requests.get(config.databaseURL + buyers_db)
    r = r.json()

    if r:
        data = [r[i] for i in r]
        buyers_df = pd.DataFrame.from_dict(data, orient='columns')

    buyers_df['lastInitial'] = buyers_df['lastName'].astype(str).str[0]
    buyers_df['firstThree'] = buyers_df['firstName'].astype(str).str[:3]

    buyers_df['name']=buyers_df['firstThree']+" "+buyers_df['lastInitial']

    buyers_df=buyers_df[['name','orderID']]
    buyers_df = buyers_df.astype({"orderID": int})


    pending_reviews_df=pd.merge(buyers_df,pending_reviews,on='orderID',how='inner')


    now = datetime.now()
    now = timezone('US/Central').localize(now)
    pending_reviews_df['now'] = now

    for index, item in pending_reviews_df.iterrows():
        dateShipped = datetime.strptime(item.dateShipped, "%m/%d/%y")
        dateShipped = timezone('US/Central').localize(dateShipped)

        dateShipped =dateShipped + timedelta(hours=5)

        pending_reviews_df.loc[index,'dateShipped_local']=dateShipped


    for index, item in pending_reviews_df.iterrows():
        days=(item.now-item.dateShipped_local).total_seconds()
        d = days//86400
        pending_reviews_df.loc[index,'daysSinceShipped']=d


    reviews_under_100=pending_reviews_df.loc[pending_reviews_df['daysSinceShipped']<=100,:]
    reviews_under_100=reviews_under_100.sort_values(by='daysSinceShipped', ascending=False)
    reviews_under_100 = reviews_under_100.astype({"daysSinceShipped": int})

    outstanding_reviews=[]

    for index, item in reviews_under_100.iterrows():
        reviewdict={}
        reviewdict['a_buyerName']=item[0]
        reviewdict['c_orderURL']=item[4]
        reviewdict['b_daysSinceShipped']= item[10]
        outstanding_reviews.append(reviewdict)

    return jsonify(outstanding_reviews)

@app.route("/bayes")
def bayes():
    listingStatsDB  = "listing_stats.json"
    r = requests.get(config.databaseURL + listingStatsDB)
    r = r.json()
    # style_in_html = ""
    # data_in_html = ""
    if r:
        data = [r[i] for i in r]
        listing_stats_df = pd.DataFrame.from_dict(data, orient='columns')
    listing_stats_df = listing_stats_df.astype({"listingID": int,"revenue":float,"sold":int,"visits":int})


    listingCreationDB  = "listing_creation_dates.json"
    r = requests.get(config.databaseURL + listingCreationDB)
    r = r.json()
    # style_in_html = ""
    # data_in_html = ""
    if r:
        data = [r[i] for i in r]
        listing_creation_df = pd.DataFrame.from_dict(data, orient='columns')
    listing_creation_df = listing_creation_df.astype({"ListingID": int})


    listing_creation_df=listing_creation_df.drop_duplicates()
    listing_creation_df['OriginallyCreated'] = pd.to_datetime(listing_creation_df['OriginallyCreated'])

    #Get data from database
    activeListingsDB  = "active_listings.json"
    r = requests.get(config.databaseURL + activeListingsDB)
    r = r.json()
    # style_in_html = ""
    # data_in_html = ""
    if r:
        data = [r[i] for i in r]
        active_listings_df = pd.DataFrame.from_dict(data, orient='columns')

    active_listings_df = active_listings_df.astype({"listingID": int})

    listingIDs=active_listings_df['listingID']


    now = datetime.now()
    now = timezone('US/Central').localize(now)



    listingIDsAll=[]
    creationDateAll=[]
    listingViewsAll=[]
    totalSiteViewsAll=[]
    avg_views_day=[]
    max_views_day=[]
    min_views_day=[]
    editURLs=[]
    daysActive=[]

    for listing in listingIDs:
        #sort listing stats by listing
        listingIDsAll.append(listing)

        editURL=(f'https://www.etsy.com/your/shops/jetchcreations/tools/listings/view:table,stats:true/{listing}')
        editURLs.append(editURL)

        stats_by_listing=listing_stats_df.loc[listing_stats_df['listingID']==listing,:]

        #find the sum of views for the listing
        listingViews = stats_by_listing['visits'].sum()
        listingViewsAll.append(listingViews)

        #find the creation date for listing
        creation_date_by_listings=listing_creation_df.loc[listing_creation_df['ListingID']==listing,:]
        creation_date_by_listings=creation_date_by_listings.reset_index(drop=True)
        creationDate=creation_date_by_listings['OriginallyCreated'][0]
        creationDate = timezone('US/Central').localize(creationDate)
        creationDate =creationDate + timedelta(hours=5)
        creationDateAll.append(creationDate)

        noDaysSinceCreation= now - creationDate

        noDaysSinceCreation = noDaysSinceCreation/ np.timedelta64(1, 'D')

        daysActive.append(noDaysSinceCreation)

        #find total site views since the listing was created
        for index, item in listing_stats_df.iterrows():
            try:
                record_date = datetime.strptime(item.record_date, "%m/%d/%y")
                record_date = timezone('US/Central').localize(record_date)

                record_date =record_date + timedelta(hours=5)

                listing_stats_df.loc[index,'record_date_local']=record_date
            except:
                record_date = datetime.strptime(item.record_date, "%Y-%m-%d")
                record_date = timezone('US/Central').localize(record_date)

                record_date =record_date + timedelta(hours=5)

                listing_stats_df.loc[index,'record_date_local']=record_date

        total_views_since_creation=listing_stats_df.loc[listing_stats_df['record_date_local']>=creationDate]

        #find the sum of views for the listing
        total_views_since_creation = total_views_since_creation.astype({"visits": int})

        totalSiteViews = total_views_since_creation['visits'].sum()
        totalSiteViewsAll.append(totalSiteViews)

        averageViewsPerListingPerDay = 0.85
        averageViewsPerDay = 28.5

        averageViewsPerListingPerDay/averageViewsPerDay

        priorScale = 7 #one week
        priorAlpha = averageViewsPerListingPerDay * priorScale #average views per listing per day (success)
        priorBeta = (averageViewsPerDay * priorScale) - priorAlpha #average total views per day minus average listing views (failures)

        scale = 1 #scale to make graph pretty

        posteriorAlpha = priorAlpha + listingViews
        posteriorBeta = priorBeta + (totalSiteViews - listingViews)


        ntrials = 10000
        sample = beta.rvs(posteriorAlpha, posteriorBeta, scale=scale, size=ntrials)

        avg_views_day1=(np.mean(sample)/scale) * averageViewsPerDay
        avg_views_day.append(avg_views_day1)
        min_views_day1=(np.quantile(sample, .025)/ scale) * averageViewsPerDay
        min_views_day.append(min_views_day1)
        max_views_day1=(np.quantile(sample, .975)/ scale) * averageViewsPerDay
        max_views_day.append(max_views_day1)

    bayes_df=pd.DataFrame({'listingID':listingIDsAll,
    'creationDate':creationDateAll,
    'listingViews':listingViewsAll,
    'totalSiteViews':totalSiteViewsAll,
    'avg_views_day':avg_views_day,
    'max_views_day':max_views_day,
    'min_views_day':min_views_day,
    'edit_url':editURLs,
    'days_active':daysActive})

    bayes_df["curr_views_day"] = (bayes_df.listingViews / bayes_df.totalSiteViews) * 28.5

    bayes_test=[]

    for index, item in bayes_df.iterrows():
        bayesDict={}
        bayesDict['a_listingID']=item[0]
        bayesDict['b_daysActive']=round(item[8],1)
        bayesDict['c_ListingVisits']=round(item[2],4)
        bayesDict['d_TotalSiteVisits']=round(item[3],4)
        bayesDict['e_CurrentVisitsDay']=round(item[9],4)
        bayesDict['f_AvgListingVisits']=round(item[4],4)
        bayesDict['g_MinListingVisits']=round(item[6],4)
        bayesDict['h_MaxListingVisits']=round(item[5],4)
        bayesDict['i_EditURL']=item[7]

        bayes_test.append(bayesDict)

    return jsonify(bayes_test)


if __name__ == "__main__":
    app.run()

