andas as pd
import numpy as np
import tweepy
import datetime
import pytz
import time

# 取得したキーを格納
# BT = "himitu"
# CK = "himitu"
# CS = "himitu"
# AT = "himitu"

BT = "AAAAAAAAAAAAAAAAAAAAAEdLhgEAAAAAKyu0W6PIo7Zj%2FNB1BpINf%2Fcm6gE%3DT0EVYBss7PGh2rxZ70CXaOvKMrCifCwfVwsK37dXrcPSA851gg"
CK = "zScfmXxDONhXg9cIjp2SEk6m6"
CS = "fuAXsoZjTU5zvE1MkievSa7oITjF414wU6EGQUSgBwuTSfT44h"
AT = "1557281594955923456-ae2iV205fcP82YzSkCj3T9fPCQEEjh"
AS = "yOYPCy5G7ty8L6OikJWewpbSdEvGGbl1ETHgrRdw8ffGU"

api = tweepy.Client(bearer_token=BT, consumer_key=CK, consumer_secret=CS, access_token=AT, access_token_secret=AS, wait_on_rate_limit=True)

def utc2jst(timestamp_utc):
    datetime_utc = datetime.datetime.strptime(timestamp_utc + ".000+0000", "%Y-%m-%dT%H:%M:%SZ.%f%z")
    datetime_jst = datetime_utc.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
    timestamp_jst = datetime.datetime.strftime(datetime_jst, '%Y-%m-%dT%H:%M:%SZ')
    return timestamp_jst

def jst2utc(timestamp_jst):
    datatime_jst = datetime.datetime.strptime(timestamp_jst + ".000+0000", "%Y-%m-%dT%H:%M:%SZ.%f%z")
    datetime_utc = datatime_jst.astimezone(datetime.timezone(datetime.timedelta(hours=-9)))
    timestamp_utc = datetime.datetime.strftime(datetime_utc, '%Y-%m-%dT%H:%M:%SZ')
    return timestamp_utc

def twittertime2jst(timestamp):
    timestamp = timestamp.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
    return timestamp


def make_timestamp(yyyy,mm,dd):
    start_time =(str(yyyy) + '-' +str(mm)+ '-' +str(dd) +'T00:00:00Z')
    end_time = (str(yyyy) + '-' +str(mm)+ '-' +str(dd) +'T23:59:59Z')
    start_time = jst2utc(start_time)
    end_time = jst2utc(end_time)
    return start_time,end_time



def make_dataframe(search_word,start_time,end_time):
    list_tweets = []
    counter = 0
    for response in tweepy.Paginator(api.search_all_tweets,
                                    query = search_word,
                                    user_fields = ['username', 'public_metrics', 'description', 'location',],
                                    tweet_fields = ['created_at', 'geo', 'public_metrics', 'text', 'source', 'attachments'],
                                    media_fields = ['url', 'type', ],
                                    expansions = ['author_id', 'attachments.media_keys'],
                                    end_time=jst2utc(end_time),
                                    start_time=jst2utc(start_time),
                                    max_results=10):
        time.sleep(1)
        list_tweets.append(response)
    result = []
    user_dict = {}
    # Loop through each response object
    for response in list_tweets:
        # Take all of the users, and put them into a dictionary of dictionaries with the info we want to keep
        for user in response.includes['users']:
            user_dict[user.id] = {'username': user.username,
                                'followers': user.public_metrics['followers_count'],
                                'tweets': user.public_metrics['tweet_count'],
                                'description': user.description,
                                'location': user.location
                                }
        for tweet in response.data:
            # For each tweet, find the author's information
            author_info = user_dict[tweet.author_id]
            # Put all of the information we want to keep in a single dictionary for each tweet
            if tweet.geo != None:
                s = str(tweet['created_at'])
                created_at = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S%z")
                created_at = (str(created_at.year) + '-' + str(created_at.month) + '-' + str(created_at.day) + 'T'+'00:00:00Z')
                created_at = utc2jst(created_at)
                result.append({'author_id': tweet.author_id,
                            'username': author_info['username'],
                            'author_followers': author_info['followers'],
                            'author_tweets': author_info['tweets'],
                            'author_description': author_info['description'],
                            'author_location': author_info['location'],
                            'text': tweet.text,
                            'created_at': created_at,
                            'retweets': tweet.public_metrics['retweet_count'],
                            'replies': tweet.public_metrics['reply_count'],
                            'likes': tweet.public_metrics['like_count'],
                            'quote_count': tweet.public_metrics['quote_count'],
                            'place_id':tweet.geo['place_id']
                            })

    # Change this list of dictionaries into a dataframe
    df = pd.DataFrame(result)

    return df

if __name__ == '__main__':
    search_word = "place:japan  has:geo lang:ja"
    day_list = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
    tmp = ['01']
    for day in tmp:
        start_time,end_time = make_timestamp('2019','08',day)
        df = make_dataframe(search_word,start_time,end_time)
        df.to_csv('/home/is/shuntaro-o/dev/disaster_analysis_Twitter/data/tmp.csv')