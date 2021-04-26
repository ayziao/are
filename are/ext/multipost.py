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


def toot(access_token,body):
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url='https://mstdn.jp'
    )
    r = mastodon.toot(body)
    # print(type(r))
    # print(r)
    return r
