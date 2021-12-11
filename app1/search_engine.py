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
alltopics={}
alltopics['hi']={
    0.0: 'bjp   president   nahi    national',
    1.0: 'nashik soul mind food big',
    2.0: 'come child certificate great people',
    3.0: 'hai rashtrapatibhvn life change increase',
    4.0: 'vaccine corona dos vaccination jai',
    5.0: 'time country make india',
    6.0: 'country india day people crore',
    7.0: 'new vaccination world today center',
    8.0: 'covishield available like covaxin congratulation',
    9.0: 'modi sir vaccine record guidance',
    10.0: 'congress nagar britain india vaccine',
    11.0: 'minister government shri prime pradesh',
    12.0: 'administer wish good yogi karnataka family',
    13.0: 'dose vaccine vaccinate vaccination campaign',
    14.0: 'crore lakh development youth birthday',
}
alltopics['en']={
    0.0: 'american great job live johnson',
    1.0: 'good time love protect community',
    2.0: 'million biden don support month',
    3.0: 'vaccinate new start world safe',
    4.0: 'amp case high nation dos',
    5.0: 'health state plan clinical public',
    6.0: 'people covid need stop death',
    7.0: 'work like know today look',
    8.0: 'vaccine say day come report',
    9.0: 'just help vaccination care',
    10.0: 'make family test virus congress',
    11.0: 'dose want week die ivermectin',
    12.0: 'life india way texas fight',
    13.0: 'shot country thank president let',
    14.0: 'year booster pfizer think right',
}
alltopics['es']={
    0.0: 'today make use morning case',
    1.0: 'covid continue new report just',
    2.0: 'mexico health campaign care immunization',
    3.0: 'vaccine year pfizer child antibody',
    4.0: 'effect government vaccine people life',
    5.0: 'vaccine death coronavirus center',
    6.0: 'day work apply dos arrive',
    7.0: 'people vaccinate come start data',
    8.0: 'dose second receive old leave',
    9.0: 'vaccination state united public change',
    10.0: 'know vaccinate want time dont',
    11.0: 'good need thank best world',
    12.0: 'vaccinate say country vaccine vaccinated',
    13.0: 'vaccine age like right long',
    14.0: 'population vaccinate measure tell think',
}


@app.route('/tweet_ret',  methods=['GET', 'POST'])
def tweet_ret():
    if request.method == 'POST':
        search = request.form.get('search')
        poii= request.form.get('poi')
        countryyy= request.form.get('country')
        langgg= request.form.get('lang')
        
        print(search, poii,countryyy,langgg)
        # encoded_query = urllib.parse.quote(search)
        # print(type(encoded_query),encoded_query)
        query=search
        query = re.sub(' +', '%0Atweet_text:', query)

        query = query +')'
        if poii != "n":
            query = query+ '%0AAND%20poi_name%3A'+poii

        if countryyy != "nn":
            query = query+ '%0AAND%20'+'country%3A'+countryyy

        if langgg != "nnn":
            query = query+ '%0AAND%20tweet_lang%3A'+langgg            

        inurl = 'http://3.139.237.57:8983/solr/FINAL/select?q.op=OR&q=(tweet_text%3A'+query+'&wt=json&indent=true&rows=1000'

        poi_url = 'http://3.139.237.57:8983/solr/FINAL/select?q.op=OR&q=(tweet_text%3A'+query+'%0AAND%20poi_id%3A*'+'&wt=json&indent=true&rows=10'
        print(inurl)
        print(poi_url)

        f = open("reply_tweets.json")
        doo = json.load(f)

        twids=[]
        
        for tt in doo:
            twid = tt['replied_to_tweet_id']
            twids.append(twid)
        
        count=0
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        tweet_data = []
        pos_tweets=0
        neg_tweets=0
        neu_tweets=0

        india=0
        usa=0
        mexico=0

        poi_data = urllib.request.urlopen(poi_url)
        poi_docs = json.load(poi_data)['response']['docs']

        if poii != "n":
            poi_docs=[]

        for tweet in poi_docs:
            tw = {}
            tw_id = tweet['id']
            ttt = int(tw_id)

            print(count)
            print(ttt)

            count+=1
            if count>10:
                break

            max_p='N/A'
            min_p='N/A'
            replies=[]
            if ttt in twids:
                replies= list(filter(lambda person: person['replied_to_tweet_id'] == ttt, doo))
                if len(replies)>1:
                    polarity_scores={}

                    for rep in replies:
                        t_t = rep['tweet_text']
                        polarity = TextBlob(t_t).sentiment.polarity
                        polarity_scores[t_t]=polarity

                    max_p=max(polarity_scores, key=polarity_scores.get)
                    min_p=min(polarity_scores, key=polarity_scores.get)



            tweet_text = tweet['tweet_text']
            tweet_senti_val = 0
            tweet_senti = ''
            

            tweet_senti_val=tweet['sentiment_score'][0]

            top = tweet['dominant_topic']

            topicc_disp=''

            if tweet['tweet_lang']== 'en':
                usa+=1
                topicc_disp = alltopics['en'][top]

            elif tweet['tweet_lang']== 'hi':
                india+=1
                topicc_disp = alltopics['hi'][top]

            elif tweet['tweet_lang']== 'es':
                mexico+=1
                topicc_disp = alltopics['es'][top]
            else:
                continue

            if tweet_senti_val > 0:
                tweet_senti = 'Positive Tweet'
                pos_tweets+=1
            elif tweet_senti_val < 0:
                tweet_senti = 'Negative Tweet' 
                neg_tweets+=1       
            elif tweet_senti_val==0:
                tweet_senti = 'Neutral Tweet'
                neu_tweets+=1

            


            tw['dom_top']    = topicc_disp    
            tw['tw_id']      = tw_id
            tw['tweet_text'] = '(POI) @'+str(tweet['poi_name'])+tweet_text
            tw['polarity']   = tweet_senti_val
            tw['tweet_sentiment']= tweet_senti
            tw['pos_reply']  = max_p
            tw['neg_reply']  = min_p

            tweet_data.append(tw)


        for tweet in docs:
            tw = {}
            tw_id = tweet['id']
            ttt = int(tw_id)
            if ttt not in twids:
                continue

            print(count)
            print(ttt)


            replies= list(filter(lambda person: person['replied_to_tweet_id'] == ttt, doo))


            count+=1
            if count>20:
                break

            print("no. of replies: ",len(replies))
            polarity_scores={}

            for rep in replies:
                t_t = rep['tweet_text']
                polarity = TextBlob(t_t).sentiment.polarity
                polarity_scores[t_t]=polarity

            max_p=max(polarity_scores, key=polarity_scores.get)
            min_p=min(polarity_scores, key=polarity_scores.get)
            #print(max_p, polarity_scores[max_p])
            #print(min_p, polarity_scores[min_p])

            tweet_text = tweet['tweet_text']
            tweet_senti_val = 0
            tweet_senti = ''

            if len(replies)==1:
                max_p='N/A'
                min_p='N/A'

            tweet_senti_val=tweet['sentiment_score'][0]
            top = tweet['dominant_topic']

            if tweet['tweet_lang']== 'en':
                usa+=1
                topicc_disp = alltopics['en'][top]

            elif tweet['tweet_lang']== 'hi':
                india+=1
                topicc_disp = alltopics['hi'][top]

            elif tweet['tweet_lang']== 'es':
                mexico+=1
                topicc_disp = alltopics['es'][top]
            else:
                continue

            if tweet_senti_val > 0:
                tweet_senti = 'Positive Tweet'
                pos_tweets+=1
            elif tweet_senti_val < 0:
                tweet_senti = 'Negative Tweet' 
                neg_tweets+=1       
            elif tweet_senti_val==0:
                tweet_senti = 'Neutral Tweet'
                neu_tweets+=1

            tw['dom_top']    = topicc_disp 
            tw['tw_id']      = tw_id
            tw['tweet_text'] = tweet_text
            tw['polarity']   = tweet_senti_val
            tw['tweet_sentiment']= tweet_senti
            tw['replies']    = replies
            tw['pos_reply']  = max_p
            tw['neg_reply']  = min_p
            tweet_data.append(tw)

        rem =0
        if count < 20:
            rem = 20-count
            inurl = 'http://3.139.237.57:8983/solr/FINAL/select?q.op=OR&q=(tweet_text%3A'+query+'&wt=json&indent=true&rows='+str(rem)
            print(inurl)
            data = urllib.request.urlopen(inurl)
            docs = json.load(data)['response']['docs']
            for tweet in  docs:
                tw = {}
                tw_id = tweet['id']


                tweet_text = tweet['tweet_text']
                tweet_senti_val = 0
                tweet_senti = ''
                

                tweet_senti_val=tweet['sentiment_score'][0]
                top = tweet['dominant_topic']
                
                if tweet['tweet_lang']== 'en':
                    usa+=1
                    topicc_disp = alltopics['en'][top]

                elif tweet['tweet_lang']== 'hi':
                    india+=1
                    topicc_disp = alltopics['hi'][top]

                elif tweet['tweet_lang']== 'es':
                    mexico+=1
                    topicc_disp = alltopics['es'][top]

                if tweet_senti_val > 0:
                    tweet_senti = 'Positive Tweet'
                    pos_tweets+=1
                elif tweet_senti_val < 0:
                    tweet_senti = 'Negative Tweet' 
                    neg_tweets+=1       
                elif tweet_senti_val==0:
                    tweet_senti = 'Neutral Tweet'
                    neu_tweets+=1
                else:
                    continue

                print(count)
                count+=1
                tw['dom_top']    = topicc_disp 
                tw['tw_id']= tw_id
                tw['tweet_text']= tweet_text
                tw['polarity']= tweet_senti_val
                tw['tweet_sentiment']= tweet_senti
                tw['reply'] = 'N/A'
                tw['neg_reply'] = 'N/A'
                tweet_data.append(tw)

        tw_data = {}
        tw_data['pos_tweets'] = pos_tweets
        tw_data['neg_tweets'] = neg_tweets
        tw_data['neu_tweets'] = neu_tweets
        tw_data['india'] = india
        tw_data['usa'] = usa
        tw_data['mexico'] = mexico


        return render_template('search.html',data=tweet_data, dt= tw_data)
"""
Index.html - Main Page
"""
@app.route('/')
def index():

    # config = {'user': 'root','password': 'root','host': 'db','port': '3306','database': 'htest'}
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
