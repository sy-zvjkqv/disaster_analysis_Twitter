import time
import datetime

from pymongo import MongoClient
import tweepy

from twitter_authentication import bearer_token

bearer_token = bearer_token
tweet_client = tweepy.Client(bearer_token, wait_on_rate_limit=True)


def main():
    #print('logの番号を入力してください: ')
    #log_name = int(input())
    log_name = 100001

    with MongoClient() as client:

        #loading since_id
        db = client['shizuku']
        collection = db['hot_since_2022_07_03']
        #最後のデータを持ってくる場合
        #cursor = collection.find().sort([('_id', -1)]).limit(1)
        #for i in cursor:
        #    since_id = int(i['id'])
        #最初のデータを持ってくる場合
        cursor = collection.find().limit(1)
        for i in cursor:
            since_id = int(i['id'])

        #print(since_id)
        #since_id = 1466931125717000194
        #print(since_id)


        #loading until_id
        db = client['shizuku']
        collection = db['hot_since_2022_08_31']
        #collection = db['cold_try']
        cursor = collection.find().sort([('_id', -1)]).limit(1)
        for i in cursor:
            until_id = int(i['id'])
        #print(until_id)

        #loading main collection
        db = client['shizuku']
        collection = db['hot_since_2022_08_31']

        next_token = ""
        get_times = 0

        while next_token is not None:
            start = time.time()
            for response in tweepy.Paginator(tweet_client.search_all_tweets,
                                                 query = '暑い -is:retweet lang:ja',
                                                 user_fields = ['username', 'public_metrics', 'description', 'location',],
                                                 tweet_fields = ['created_at', 'geo', 'public_metrics', 'text', 'source', 'attachments'],
                                                 media_fields = ['url', 'type', ],
                                                 expansions = ['author_id', 'attachments.media_keys'],
                                                 since_id = since_id,
                                                 until_id = until_id,
                                                 max_results=500):
                   time.sleep(1)

                   #res = [{s: getattr(r, s) for s in r.__slots__ if hasattr(r, s)} for r in response.data]
                   res_data = [{s: getattr(r, s) for s in r.__slots__ if hasattr(r, s)} for r in response.data]
                   res_includes = [{s: getattr(r, s) for s in r.__slots__ if hasattr(r, s)} for r in
                                   response.includes['users']]
                   res_includes_fix = []
                   for r in res_includes:
                       # print(r)
                       r['author_data'] = r['data']
                       r['author_created_at'] = r['created_at']
                       r['author_public_metrics'] = r['public_metrics']
                       r['author_entities'] = r['entities']
                       r['author_withheld'] = r['withheld']
                       del r['data']
                       del r['created_at']
                       del r['public_metrics']
                       del r['id']  # idはres_dataの要素にもあるため
                       del r['entities']
                       del r['withheld']
                       # print(r)
                       res_includes_fix.append(r)

                   res = []
                   for data, includes in zip(res_data, res_includes_fix):
                       dic_res = dict(**data, **includes)
                       res.append(dic_res)

                   collection.insert_many(res)
                   next_token = response.meta.get("next_token", None)

                   time.sleep(1)

                   get_times += 1
                   elapsed_time = time.time() - start

                   log = str(get_times) + 'times：' + str(response.data[0].created_at) + '　　　time' + str(
                       elapsed_time) + '[sec]\n'
                   print(log)

                   if get_times == 1:
                       with open(f'./log/hot_log_since_2022_08_31/log_{log_name}.txt', 'w') as f:
                           df_now = datetime.datetime.now()
                           now = df_now.strftime('%Y年%m月%d日 %H:%M:%S')
                           now = now + '\n'
                           f.write(now)

                   with open(f'./log/hot_log_since_2022_08_31/log_{log_name}.txt', 'a') as f:
                        f.write(log)

if __name__ == "__main__":
    main()