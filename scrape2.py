#Libraries
#Newspaper3k
#https://newspaper.readthedocs.io/en/latest/
from newspaper import Article

#https://www.nltk.org
from nltk import word_tokenize
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer

from bs4 import BeautifulSoup
import urllib

#regex
import re

#https://selenium-python.readthedocs.io
from selenium import webdriver

import string
import time


#function to tokenize and clean articles
def tokenize_articles(article_list):
    
    #pass list of raw article/text to be tokenized
    #returns list of cleaned tokens
    
    #regex expression to remove non-alphabet only strings
    regex = re.compile('[^a-zA-Z]')

    #lemmatizing
    wordnet_lemmatizer = WordNetLemmatizer()

    article_tokens = []
    cleaned_tokens = []

    #uses nltk to tokenize article
    for article in article_list:
        tokens =  word_tokenize(article)
        article_tokens.append(tokens)
        
    #removes punctuation, empty tokens, non-alpha only tokens, converts to lowercase, lemmatizes 
    for tokens in article_tokens:
        
        #removes punctuation
        tokens_processing = [''.join(word for word in tok if word not in string.punctuation) for tok in tokens]
        
        #converts to lower case
        tokens_processing = [word.lower() for word in tokens_processing if word]
        
        #removes numbers and alphanumeric strings
        tokens_processing = [regex.sub('', word) for word in tokens_processing]
        
        #removes empty tokens
        tokens_processing= list(filter(None, tokens_processing)) # fastest


        #lemmatizing
        tokens_processing = [wordnet_lemmatizer.lemmatize(word) for word in tokens_processing]

        cleaned_tokens.append(tokens_processing)
        
    return cleaned_tokens




#scrape all pages from cryptocurrency news from cointelegraph bitcoin
url = "https://cointelegraph.com/tags/bitcoin"

#change location to your webdriver
driver =webdriver.Chrome('/Users/rashanarshad/Downloads/chromedriver')
driver.get(url)
html = driver.page_source.encode('utf-8')
page_num = 0

while (page_num < 200):
#while driver.find_elements_by_css_selector('.load'):

    driver.find_element_by_css_selector('.load').click()
    page_num += 1
    print("getting page number "+str(page_num))
    time.sleep(3)

html = driver.page_source.encode('utf-8')



#get htmls and parse for article links
soup = BeautifulSoup(html, 'lxml')



links = []
for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
    links.append(link.get('href'))



links_new = soup.find_all('h2', attrs={"class":'header'})
articles = [a.find('a')['href'] for a in links_new if a != '']


#download article and store text and timestamp 
from newspaper.article import ArticleException, ArticleDownloadState
from time import sleep

bitcoin_texts = []
    #parses each url and appends raw text to list, returns list of raw text
count = 0
slept = 0
for url in articles:
    article = Article(url.strip())
    article.download()
    while article.download_state == ArticleDownloadState.NOT_STARTED:
        # Raise exception if article download state does not change after 100 seconds
        #should solve download not started bug
        if slept > 100:
            raise ArticleException('Download never started')
        sleep(1)
        slept += 1
    article.parse()
    bitcoin_texts.append(article)
    print(count)
    count+=1
    
    

article_date_dict = {}
for x in bitcoin_texts:
    article_date_dict[x.text] = x.publish_date



#get article text and store in list
bitcoin_texts = [x.text for x in bitcoin_texts]



#clean articles
bitcoin_tokens = tokenize_articles(bitcoin_texts)
