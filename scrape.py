"""
1.1 Collect weather vocabularies

To determine the classes weathers going to be used for training, need to scrape weather vocabulary 
website: Weather Vocabulary (US),
link: https://www.teachstarter.com/au/teaching-resource/weather-word-wall-vocabulary-us/

The function used to scrape vocabularies.
"""

from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import requests
import time
from tqdm import tqdm
from flickrapi import FlickrAPI

key = ''
secret = ''

# set up url link and use requests and BeautifulSoup to get the vocabularies
URL = "https://www.teachstarter.com/us/teaching-resource/weather-word-wall-vocabulary-us/"
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
r = requests.get(URL, headers=headers)
soup = BeautifulSoup(r.content, 'html5lib')

# find the vocabularies sections and save to list
data=[]
words = soup.find('div', attrs={"class":"links"}) 

for row in words.findAll('li', attrs={"data-v-09efc660":""}):
    text = row.text.replace('\n', '')
    if len(text)<15 and not(" " in text) and not(any(ch.isupper() for ch in text)) and (text not in data):
        data.append(text)

# save the scraped vocabularies in csv file for image collection.
fields = ['words'] 
filename = 'weather_vocabulary.csv'
with open(filename, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for voc in data:
        writer.writerow([voc])

# the final classes are rain, cloud, sun, fog, rainbow, snow
# each class has subclasses used for image collected, eg, use the words in each class to collect images from Flickr

data = {
    'rain': ['lightning', 'thunder', 
             'thunderstorm', 'downpour', 
             'storm', 'flood', ], 
    'cloud': ['cloud', 'cloudy',],
    'sun': ['sun', 'sunny',],
    'fog': ['fog', 'mist', 'smog', 
            'sleet', 'dew'],
    'rainbow': ['rainbow',],
    'snow': ['snow', 'icicle', 'snowfall', 
             'hail', 'frost', 'blizzard',],
}

"""
1.3 Scrape images from Flickr
Full dataset collected amount to 24,000 images. Here I have presented the 
functions for collection and images saved in the dataset for amount of 10 for 
each class as demo. To collect more images, please adjust the amount of urls 
scraped for image collection.

The total dataset I have collect is amount 24,000, so that each class has 4,000 
images. To make sure each has same total amount, each subclass amount is equal to 
4000 / len(class_list). In this way, within each class, the subclasses have equal 
amount of images.

Images collected for each class is saved in their own folder. The path, imageID 
and label are also collected and saved in csv file for training.
"""

def fetch_image_link(query, amount):
    flickr = FlickrAPI(key, secret)         #initialize python flickr api
    photos = flickr.walk(text=query,
                        tag_mode='all',
                        extras='url_c',     #specify meta data to be fetched
                        sort='relevance')   #sort search result based on relevance (high to low by default)
    
    max_count = amount                      #let's just simply fetch 5 images for illustration
    urls = []
    count = 0

    for photo in photos:
        if count >= max_count:
            break
        count = count + 1
        try:
            url = photo.get('url_c')
            urls.append(url)
        except:
            print("Url for image number {} could not be fetched".format(count))
    return urls


# here is a demo to scrap 15 images and save to folder
# scraping 15 because some urls fails to download, need to scrap a more in case
amt_collect = 15
for label, QURIES in data.items():
    l = len(QURIES)
    amount_temp = int(amt_collect / l)
    amount_list = [amount_temp, ] * (l - 1)
    amount_list.append(amt_collect - sum(amount_list)) # for 10 images, the last sub class has more images than others, 
                                                        # but when we collect 4000 total amount for each class, the difference is immaterial
    for query, amount in zip(QURIES, amount_list):
        urls = fetch_image_link(query, amount)
        if len(urls) > amount - 1:
            urls = pd.Series(urls)
            save_path = './Flickr_scrape/'
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            category_path = f'{save_path}/{label}_urls.csv'
            urls.to_csv(category_path, mode='a', header=False, index=False)

