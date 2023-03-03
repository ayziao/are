import requests
from requests_oauthlib import OAuth1Session
from mastodon import Mastodon


def tweet(seting, body):
    twitter = OAuth1Session(seting['consumerKey'],
                            seting['consumerSecret'],
                            seting['accessToken'],
                            seting['accessTokenSecret'])
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    params = {"status": body}
    r = twitter.post(url, params).json()
    # print(r)
    # print(type(r))
    return r


def toot(access_token, body):
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url='https://mstdn.jp'
    )
    r = mastodon.toot(body)
    # print(type(r))
    # print(r)
    return r


def note(access_token, body):
    POST_URL = "https://calckey.jp/api/notes/create"

    visibility = homepub(body)

    request_body = dict(i=access_token, visibility=visibility, text=body)

    response = requests.post(POST_URL, json=request_body, headers={'Content-Type': 'application/json'})

    return response


def homepub(body):
    if '殺' in body:
        return 'home'
    if '死' in body:
        return 'home'
    if '糞' in body:
        return 'home'
    if 'クソ' in body:
        return 'home'
    if 'うんこ' in body:
        return 'home'
    if 'ファック' in body:
        return 'home'
    if 'ファッキ' in body:
        return 'home'
    if 'ネガティブ' in body:
        return 'home'

    if 'な' in body:
        return 'public'
    if 'ナ' in body:
        return 'public'
    if 'カルクキー' in body:
        return 'public'
    if 'calckey' in body:
        return 'public'

    return 'home'
