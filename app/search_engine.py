#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify
import mysql.connector
import tweepy
import smtplib
from flask_mail import Mail, Message
import re

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cse586DS@gmail.com'
app.config['MAIL_PASSWORD'] = 'cse586Distributed'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

auth = tweepy.OAuthHandler('AC7WkBbTptQM1F9vPvaWMnPu0',
                           '6Kv4MuuLHX3FvB0PxNLZaa1ajyIIrnGqVQriBvmYzGD8u2fD3O'
                           )
auth.set_access_token('1433835629763338242-SMviK8BJ5FcBnrrYBj9CMWIoDRX8Uu'
                      , '8hcho5OJ03WadpgMjfEgvUhzX3sOJ3DNWoIvOAyqc0sdc')
api = tweepy.API(auth, wait_on_rate_limit=True)


import json
import urllib.request 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

@app.route('/tweet_ret',  methods=['GET', 'POST'])
def tweet_ret():
    if request.method == 'POST':
        search = request.form.get('search')
        # encoded_query = urllib.parse.quote(search)
        # print(type(encoded_query),encoded_query)
        query=search
        query = re.sub(' +', '%0Atweet_text:', query)

        inurl = 'http://3.139.237.57:8983/solr/TESTCORE_1/select?q.op=OR&q=tweet_text%3A'+query+'&wt=json&indent=true&rows=1000'
        print(inurl)
        f = open("reply_tweets.json")
        doo = json.load(f)

        twids=[]
        
        for tt in doo:
            twid = tt['replied_to_tweet_id']
            twids.append(twid)

        
        count=1
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        tweet_data = []
        for tweet in docs:
            tw = {}
            tw_id = tweet['id']
            ttt = int(tw_id)
            if ttt not in twids:
                continue

            print(count)
            print(ttt)

            count+=1
            if count>10:
                break


            replies= list(filter(lambda person: person['replied_to_tweet_id'] == ttt, doo))
            #print(replies)
            print("no. of replies: ",len(replies))
            polarity_scores={}

            for rep in replies:
                t_t = rep['tweet_text']
                polarity = TextBlob(t_t).sentiment.polarity
                polarity_scores[t_t]=polarity

            max_p=max(polarity_scores, key=polarity_scores.get)
            min_p=min(polarity_scores, key=polarity_scores.get)
            print(max_p, polarity_scores[max_p])
            print(min_p, polarity_scores[min_p])

            tweet_text = tweet['tweet_text']
            tweet_senti_val = 0
            tweet_senti = ''
            polarity = TextBlob(tweet['tweet_text']).sentiment.polarity
            tweet_senti_val=polarity

            
            if polarity > 0:
                tweet_senti = 'Positive Tweet'
            elif polarity < 0:
                tweet_senti = 'Negative Tweet'        
            elif polarity==0:
                tweet_senti = 'Neutral Tweet'



            tw['tw_id']= tw_id
            tw['tweet_text']= tweet_text
            tw['tweet_senti_val']= tweet_senti_val
            tw['tweet_senti']= tweet_senti
            tw['replies'] = replies
            tw['pos_reply'] = max_p
            tw['neg_reply'] = min_p
            tweet_data.append(tw)

        rem =0
        if count < 10:
            rem = 10-count
            inurl = 'http://3.139.237.57:8983/solr/TESTCORE_1/select?q.op=OR&q=tweet_text%3A'+query+'&wt=json&indent=true&rows='+str(rem)
            data = urllib.request.urlopen(inurl)
            docs = json.load(data)['response']['docs']
            for tw in  docs:
                print(count)
                count+=1


        

        return render_template('search.html',data=tweet_data)
"""
Index.html - Main Page
"""
@app.route('/')
def index():

    # config = {'user': 'root','password': 'root','host': 'db','port': '3306','database': 'htest'}
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
