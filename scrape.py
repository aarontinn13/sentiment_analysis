# coding: utf-8

#Googlesearch by MarioVilla
#https://github.com/MarioVilas
from googlesearch import search_news

#Newspaper3k
#https://newspaper.readthedocs.io/en/latest/
from newspaper import Article

from nltk import word_tokenize
import string

import pandas as pd


def parse_url(url_list):
    #pass a list of urls to be parsed
    
    bitcoin_texts = []
    #parses each url and appends raw text to list, returns list of raw text
    for url in (url_list):
        article = Article(url)
        article.download()
        article.parse()
        bitcoin_texts.append(article.text)
    return bitcoin_texts

def tokenize_articles(article_list):
    
    #pass list of raw article/text to be tokenized
    #returns list of cleaned tokens


    article_tokens = []
    cleaned_tokens = []
    
    #uses nltk to tokenize article
    for article in article_list:
        tokens =  word_tokenize(article)
        article_tokens.append(tokens)
    #removes punctuation and empty tokens
    for tokens in article_tokens:
        tokens_noPunc = [''.join(word for word in tok if word not in string.punctuation) for tok in tokens]
        tokens_noPunc = [word for word in tokens_noPunc if word]
        cleaned_tokens.append(tokens_noPunc)
    return cleaned_tokens



#use search news to get news urls from search query "bitcoin" from the last hour
bitcoin_article_url = []
for url in search_news('bitcoin', tbs="qdr:h",stop=50):
    bitcoin_article_url.append(url)




bitcoin_parsed = parse_url(bitcoin_article_url)


bitcoin_tokens = tokenize_articles(bitcoin_parsed)


bitcoin_clean_text = [' '.join(x) for x in bitcoin_tokens]
