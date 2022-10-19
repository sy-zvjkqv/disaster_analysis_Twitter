import json
import os
import requests
import time
import datetime
import pickle
import urllib3


BearerToken  = "hoge"


header = {"Authorization":"Bearer {}".format(BearerToken)}

ProcessID = datetime.datetime.now()

def check_rate_limit(header):
    try:
        remain = int(header['x-rate-limit-remaining'])
        reset = int(header['x-rate-limit-reset'])
        return remain, reset
    except:
        remain = 0
        reset = datetime.datetime.now().timestamp() + 60 * 15
        return remain, reset

class full_search_tweet():

    SearchURL = 'https://api.twitter.com/2/tweets/search/all'
    def __init__(self, keyword,dirname = '/data1/shuntaro-o/hurricane',start_day = '', end_day = 7):
        next_token = ''
        start_day = start_day
        if dirname == '':
            dirname = keyword
        for day in range(end_day):
            start_time = (start_day.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=day) - datetime.timedelta(hours=9)).isoformat() + 'Z'
            end_time = (start_day.replace(hour=23, minute=59, second=59, microsecond=99) + datetime.timedelta(days=day) - datetime.timedelta(hours=9)).isoformat() + 'Z'
            dir_name = dirname + '/'+(start_day+ datetime.timedelta(days=day)).date().isoformat()+'/'
            while True:
                next_token = self.API_request(keyword, dir_name, next_token=next_token, start_time=start_time, end_time = end_time)
                time.sleep(1.1)
                if next_token == '' or next_token == 'invalid_query':
                    break
            if next_token == 'invalid_query':
                break

    def API_request(self,keyword,dir_name,next_token,start_time= '', end_time = ''):
        params = {'query': keyword,
                  'expansions': 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id',
                  'max_results': 500,
                  'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics',
                  'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
                  'poll.fields': 'duration_minutes,end_datetime,id,options,voting_status',
                  'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                  'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                  }
        if next_token != '':
            params['next_token'] = next_token
        if start_time != '':
            params['start_time'] = start_time
        if end_time != '':
            params['end_time'] = end_time
        response = requests.get(full_search_tweet.SearchURL,
                                 params=params,
                                 headers=header)
        if response.status_code == 400:
            print('status_code:',response.status_code)
            print(keyword)
            return 'invalid_query'
        elif response.status_code != 200:
            print('status_code:',response.status_code)
            while response.status_code !=200:
                time.sleep(60)
                response = requests.get(full_search_tweet.SearchURL,
                                        params=params,
                                        headers=header)
        elif response.status_code == 200:
            tweets = response.json()
            remain, reset = check_rate_limit(response.headers)
            now = datetime.datetime.now().timestamp()
            wait_time = reset - now
            if remain < 2:
                print('sleep:',wait_time)
                time.sleep(wait_time)
            print(start_time,'tweet_count:',tweets['meta']['result_count'])
            if tweets['meta']['result_count'] == 0:
                return ''
            data = tweets['data']
            users = tweets['includes']['users']
            media = ''
            if 'media' in tweets['includes']:
                media = tweets['includes']['media']
            if 'tweets' in tweets['includes']:
                twts = tweets['includes']['tweets']
            else:
                twts = ''

            os.makedirs(dir_name,exist_ok=True)
            with open(dir_name+'/tweetdata.json','a') as td:
                for d in data:
                    td.write(json.dumps(d,ensure_ascii=False)+'\n')
            with open(dir_name+'/userdata.json','a') as tu:
                for u in users:
                    tu.write(json.dumps(u,ensure_ascii=False)+'\n')
            if len(twts) > 0:
                with open(dir_name+'/conversationdata.json','a') as tc:
                    for c in tweets['includes']['tweets']:
                        tc.write(json.dumps(c,ensure_ascii=False)+'\n')
            if len(media) > 0:
                with open(dir_name + '/mediadata.json','a') as tm:
                    for m in tweets['includes']['media']:
                        tm.write(json.dumps(m,ensure_ascii=False)+'\n')
            meta_data = tweets['meta']
            if 'next_token' in meta_data:
                return  meta_data['next_token']
            else:
                return ''
        else:
            print(400)
            print(response.text)
            return ''

class someones_tweet():
    def __init__(self, user_id,dir_name='', error_stop=False):
        next_token = ''
        while True:
            next_token = self.API_request(user_id, next_token=next_token, dir_name=dir_name, error_stop=error_stop)
            time.sleep(1)
            if next_token == '':
                break

    def API_request(self,keyword,next_token, dir_name,error_stop) :
        #keyword = '菅義偉首相が立憲民主党のコロナ政策を批判したことに対し、枝野幸男代表「党首討論に相応しくない'
        if dir_name == '':
            dir_name = keyword
        else:
            dir_name = dir_name+'/'+keyword
        params = {'expansions': 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
                  'max_results': 100,
                  #'start_time': start,
                  'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics',
                  'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
                  'poll.fields': 'duration_minutes,end_datetime,id,options,voting_status',
                  'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                  'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                  }

        if error_stop:
            with open('someone.pickle','rb') as f:
                error_dict = pickle.load(f)
            next_token = error_dict['next_token']

        if next_token != '':
            params['pagination_token'] = next_token

        while True:
            with open('someone.pickle','wb') as f:
                pickle.dump({'time': ProcessID, 'dir':dir_name, 'params':params,'next_token':next_token, 'user_id':keyword},f)
            response = requests.get('https://api.twitter.com/2/users/{}/tweets'.format(keyword),
                                     params=params,
                                     headers=header,
                                     timeout=3.5)
            if response.status_code == 200:
                tweets = response.json()
                remain, reset = check_rate_limit(response.headers)
                now = datetime.datetime.now().timestamp()
                wait_time = reset - now
                if remain < 2:
                    print('sleep:', wait_time)
                    time.sleep(wait_time)
                if tweets['meta']['result_count'] == 0:
                    return ''
                if not 'data' in tweets:
                    return ''
                data = tweets['data']
                users = tweets['includes']['users']
                os.makedirs(dir_name,exist_ok=True)
                with open(dir_name+'/tweetdata.json','a') as td:
                    for d in data:
                        td.write(json.dumps(d)+'\n')
                with open(dir_name+'/userdata.json','a') as tu:
                    for u in users:
                        tu.write(json.dumps(u)+'\n')
                if 'tweets' in tweets['includes']:
                    with open(dir_name+'/conversationdata.json','a') as tc:
                        for c in tweets['includes']['tweets']:
                            tc.write(json.dumps(c)+'\n')
                if 'media' in tweets['includes']:
                    with open(dir_name + '/mediadata.json','a') as tm:
                        for m in tweets['includes']['media']:
                            tm.write(json.dumps(m)+'\n')
                meta_data = tweets['meta']
                if 'next_token' in meta_data:
                    return meta_data['next_token']
                else:
                    return ''
            elif response.status_code == 400 or response.status_code == 401:
                print('status_code:',response.status_code)
                return ''
            elif response.status_code != 200:
                print('status_code:',response.status_code)
                time.sleep(60)


    def checkid(self,username):
        endpoint = 'https://api.twitter.com/2/users/by/username/'
        response = requests.get(endpoint+username,
                                 headers=header,
                                timeout=3.5
                                )
        id = response.json()['data']['id']
        return id

class get_retweet():

    def __init__(self, tweetid):
        next_token = ''
        while True:
            next_token = self.API_request(tweetid, next_token)
            time.sleep(1)
            if len(next_token) < 1:
                break

    def API_request(self,keyword, next_token):
        #keyword = '菅義偉首相が立憲民主党のコロナ政策を批判したことに対し、枝野幸男代表「党首討論に相応しくない'
        params = {
                #'expansions': 'pinned_tweet_id',
                'max_results': 100,
                'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                  }
        if len(next_token) > 0:
            params['pagination_token'] = next_token
        response = requests.get('https://api.twitter.com/2/tweets/{}/retweeted_by'.format(keyword),
                                 params=params,
                                 headers=header,
                                timeout=3.5)

        tweets = response.json()
        remain, reset = check_rate_limit(response.headers)
        now = datetime.datetime.now().timestamp()
        wait_time = reset - now
        if remain < 2:
            print('sleep:', wait_time)
            time.sleep(wait_time)
        if 'data' in tweets:
            data = tweets['data']
        else:
            return ''
        if 'meta' in tweets:
            if 'next_token' in tweets['meta']:
                next_token = tweets['meta']['next_token']
        else:
            next_token = ''
        #os.makedirs('retweets/'+keyword,exist_ok=True)
        with open('retweets/'+keyword+'.json','a') as td:
            for d in data:
                td.write(json.dumps(d, ensure_ascii=False)+'\n')
        return next_token

    def checkid(self,username):
        endpoint = 'https://api.twitter.com/2/users/by/username/'
        response = requests.get(endpoint+username,
                                 headers=header,
                                timeout=3.5)
        id = response.json()['data']['id']
        return id


class follow_follower():

    SearchURL_following = 'https://api.twitter.com/2/users/{}/following'
    SearchURL_followers = 'https://api.twitter.com/2/users/{}/followers'

    def __init__(self, User_id, dir_name=''):
        next_follow = 'initial'
        next_follower = 'initial'
        while True:
            if next_follow != '':
                next_follow = self.API_request(User_id, next_follow, type='follow', dir_name=dir_name)
            elif next_follower != '':
                next_follower = self.API_request(User_id, next_follower, type='follower', dir_name=dir_name)
            elif next_follow == '' and next_follower == '':
                break

    def API_request(self, User_Id, next_token='', type='follow', dir_name = ''):
        params = {
                  'max_results': 1000,
                  'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                  'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                  }
        if next_token != 'initial':
            params['pagination_token'] = next_token
        retry_count=0
        while True:
            if type == 'follow':
                if dir_name != '':
                    dir_name = dir_name+'/'+User_Id+'/follow'
                else:
                    dir_name = User_Id+'/follow'
                try:
                    response = requests.get(follow_follower.SearchURL_following.format(User_Id),
                                 params=params,
                                 headers=header,
                                 timeout=(3.0, 7.5))
                except:
                    time.sleep(120)
                    retry_count +=1
                    if retry_count >5:
                        return ''
                    continue
            elif type == 'follower':
                if dir_name != '':
                    dir_name = dir_name+'/'+User_Id+'/follower'
                else:
                    dir_name = User_Id + '/follower'
                try:
                    response = requests.get(follow_follower.SearchURL_followers.format(User_Id),
                                          params=params,
                                          headers=header,
                                          timeout=(3.0, 7.5))
                except:
                    time.sleep(120)
                    retry_count +=1
                    if retry_count >5:
                        return ''
                    continue
            if response.status_code == 200:
                tweets = response.json()
                remain, reset = check_rate_limit(response.headers)
                print(remain, reset)
                now = datetime.datetime.now().timestamp()
                wait_time = reset - now
                if remain < 2:
                    print('sleep:', wait_time)
                    time.sleep(wait_time)
                if tweets['meta']['result_count'] == 0:
                    return ''
                data = tweets['data']

                os.makedirs(dir_name, exist_ok=True)
                with open(dir_name + '/tweetdata.json', 'a') as td:
                    for d in data:
                        td.write(json.dumps(d, ensure_ascii=False) + '\n')
                meta_data = tweets['meta']
                time.sleep(1)
                if 'next_token' in meta_data:
                    return meta_data['next_token']
                else:
                    return ''
            elif response.status_code == 400 or response.status_code == 401:
                print('status_code:',response.status_code)
                return ''
            elif response.status_code != 200:
                print('status_code:',response.status_code)
                time.sleep(60)

def checkid(username):
    endpoint = 'https://api.twitter.com/2/users/by/username/'
    response = requests.get(endpoint+username,
                            headers=header,
                            timeout=3.5)
    if 'data' in response.json():
        id = response.json()['data']['id']
        return id
    else:
        return ''

if __name__ == '__main__':
    start_time = datetime.datetime(2019, 10, 5, hour=0, minute = 0,second = 0)
    #full_search_tweet('(自民 総裁選) OR 高市早苗 OR 岸田文雄 OR 河野太郎 OR 野田聖子','自民党総裁選',start_day=start_time,end_day=30)
    full_search_tweet("雨 OR 強風 OR 台風 OR防風 OR 暴風", start_day=start_time, end_day= 11)
    #someones_tweet('kiyoshi_ueada_')
    #get_retweet('1480290931043536896')
    #sampling_tweet()