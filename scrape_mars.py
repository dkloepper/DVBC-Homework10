#David Kloepper
#Data Visualization Bootcamp, Cohort 3
#May 18th, 2019

#Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint
import re
import time

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "c:\\Users\\dkloe\\OneDrive\\Documents\\Data Viz Bootcamp\\chromedrv\\chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    #Initialize the dictionary to send to MongoDB
    mars_data = {}

    browser = init_browser()

    ##### Scrape Mars News #####
    #Set URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(1)

    #Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    mars_news_soup = BeautifulSoup(html, 'html.parser')

    #Scrape the first article title. While loop to ensure page loaded content
    while mars_news_soup.find('div', class_='content_title') is None:
        browser.reload()
        time.sleep(1)
    first_title = mars_news_soup.find('div', class_='content_title').text

    #Scrape the first article paragraph text. While loop to ensure page loaded content
    while mars_news_soup.find('div', class_='article_teaser_body') is None:
        browser.reload()
        time.sleep(1)
    first_paragraph = mars_news_soup.find('div', class_='article_teaser_body').text

    #Append results to dictionary
    mars_data["news_title"] = first_title
    mars_data["news_paragraph"] = first_paragraph

    ##### Scrape JPL Featured Mars Image #####
    #Set URL of page to be scraped
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(1)
    
    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')

    #Scrape the featured image URL
    feat_img_url = image_soup.find('a', class_='button fancybox')['data-fancybox-href']
    feat_img_full_url = f'https://www.jpl.nasa.gov{feat_img_url}'

    #Append result to dictionary
    mars_data["featured_image"] = feat_img_full_url

    ##### Scrape Mars weather tweet #####
    #Set URL of page to be scraped
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(1)
    
    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    tweet_soup = BeautifulSoup(html, 'html.parser')

    #Scrape the first tweet that matches the weather data. Use regex to trim unwanted text
    all_tweets = tweet_soup.find_all('p', class_='TweetTextSize')
    for tweet in all_tweets:
        if tweet.find(text=re.compile("InSight")):
            weather_tweet = tweet.text
            break
    weather_tweet = re.sub("pic.*", "", weather_tweet)

    #Append result to dictionary
    mars_data["weather_tweet"] = weather_tweet

    ##### Scrape Mars facts table using Pandas #####
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['Description', 'Value']
    
    #Append entire table as HTML to dictionary
    mars_data["fact_table"] = df.to_html(index=False)

    ###### Scrape Mars hemisphere images #####
    #Set URL of page to be scraped
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    #Populate a list with links for the hemispheres pages
    hemi_links = []
    links = hemi_soup.find_all('a', {'class':'itemLink product-item','href':True})

    for hemi in links:
        if hemi.find(text=re.compile('.*Enhanced')):
            hemi_links.append(hemi['href'])

    # Initialize hemisphere_image_urls list and set base URL
    hemisphere_image_urls = []
    base_url = "https://astrogeology.usgs.gov"

    # Loop through the hemisphere links to obtain the images
    for hemi in hemi_links:
        # Initialize a dictionary for the hemisphere title and image
        hemi_dict = {}
        
        browser.visit(base_url + hemi)
        
        html = browser.html
        hemipic_soup = BeautifulSoup(html, 'html.parser')
        
        title = hemipic_soup.find('h2', class_='title').text
        img_url = base_url + hemipic_soup.find('img', class_='wide-image')['src']
        
        hemi_dict["title"] = title
        hemi_dict["img_url"] = img_url

        hemisphere_image_urls.append(hemi_dict)

    #Append list to the overall dictionary
    mars_data["hemi_imgs"] = hemisphere_image_urls

    # Close the browser after scraping
    browser.quit()

    # Return results as a dictionary
    return mars_data