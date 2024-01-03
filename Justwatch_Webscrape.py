#Importing necessary libraries/packages
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
import numpy as np
from datetime import datetime


# Global variable for the webdriver
global driver


# URLs for movies and TV shows on JustWatch
Movie_url = 'https://www.justwatch.com/in/movies'
TVShows_url = 'https://www.justwatch.com/in/tv-shows'


# Creating empty lists to store data
Title = []
Year = []
Genres = []
Rating = []
Steaming_services = []
Url = []
url_list = []


# Chrome options for WebDriver
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches",['enable-automation'])
options.add_experimental_option("detach", True)
options.add_experimental_option("useAutomationExtension", False)
options.binary_location = './/chrome-win64/chrome.exe'


# Web scraping for Movies URLs
try:
    driver = webdriver.Chrome(options=options)
    driver.get(Movie_url)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("scrollTo(0, document.body.scrollHeight);")
        time.sleep(7)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height >= 1000:
            break
        last_height = new_height
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    movies_data = soup.findAll('div', attrs = {'class': 'title-list-grid__item'})
    for index, link in enumerate(movies_data):
        url = link.a['href']
        url_list.append(url)
        if index == 49:
            break
    driver.close()
    print(np.count_nonzero(url_list))

except Exception as e:
    print(f"Error: {e}")


# Web scraping for TV show URLs
try:
    driver = webdriver.Chrome(options=options)
    driver.get(TVShows_url)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("scrollTo(0, document.body.scrollHeight);")
        time.sleep(7)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height >= 1000:
            break
        last_height = new_height
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    tv_data = soup.findAll('div', attrs = {'class': 'title-list-grid__item'})
    for index, link in enumerate(tv_data):
        url = link.a['href']
        url_list.append(url)
        if index == 49:
            break
    driver.close()
    print(np.count_nonzero(url_list))

except Exception as e:
    print(f"Error: {e}")


# Extracting information of each movie and TV show.
try:
    for data in url_list:
        url = "https://www.justwatch.com" + data
        driver = webdriver.Chrome(options=options)
        driver.get(url) 
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        name = soup.find('div', attrs = {'class': 'title-block'}).h1.text
        year = soup.find('div', attrs = {'class': 'title-block'}).span.text.replace('(','').replace(')','')
        genres_list = soup.findAll('div', attrs={'class': 'detail-infos'})

        for genre in genres_list:
            if(genre.h3.text == 'Genres'):
                genres = genre.div.text
        if (soup.findAll('div', attrs={'class': 'jw-scoring-listing__rating'})):
            rating_details = soup.findAll('div', attrs={'class': 'jw-scoring-listing__rating'})[1].span.span.text
            rating = rating_details.strip().split(' ')[0]
        else:
            rating = '0.0'

        stservices = soup.find('div', attrs={'class': 'buybox-row__offers'})
        print(len(stservices))
        if stservices:
            if stservices.a.picture.img['alt'] == 'Bookmyshow':
                stservice = "Not Available for Streaming"
            else:
                stservicelist = stservices.a.picture.findAll('img', attrs={'class': 'offer__icon'})
                stservice = ""
                for list in stservicelist:
                    stservice = stservice.join(list['alt'])
        else:
            stservice = "Not Available for Streaming"

        Title.append(name)
        Year.append(year)
        Genres.append(genres)
        Rating.append(rating)
        Steaming_services.append(stservice)
        Url.append(url)
        driver.close()

except Exception as e:
    print(f"Error: {e}")


# Converting the scraped data into DataFrames
justwatch_Movie_list = pd.DataFrame({"Movie Titles": Title, "Year of Release": Year, "Genres": Genres, "Imdb Rating": Rating, "Streaming Services": Steaming_services, "URLs": Url})
print(justwatch_Movie_list)


# Filtering the DataFrame to include only recent releases (i.e., last 2 years) with IMDb ratings of 7 or higher.
current_year = datetime.now().year
justwatch_Movie_list['Imdb Rating'] = justwatch_Movie_list['Imdb Rating'].apply(lambda x: float(x) if x else None)
justwatch_Movie_list['Year of Release'] = pd.to_numeric(justwatch_Movie_list['Year of Release'], errors='coerce')
filtered_df = justwatch_Movie_list[(justwatch_Movie_list['Year of Release'] >= current_year - 2) & (justwatch_Movie_list['Imdb Rating'] >= 7)]
print(filtered_df)


# Identifying and displaying the average rating of movies and TVShows
average_rating = filtered_df['Imdb Rating'].mean()
print(average_rating)

# Identifying and displaying the top genres
# top_genres = filtered_df['Genres'].value_counts().idxmax()
# print(top_genres)
df_genres = pd.DataFrame({'Genres': justwatch_Movie_list['Genres'].apply(lambda x: x.split(', '))})
all_genres = [genre for sublist in df_genres['Genres'] for genre in sublist]
genre_counts = pd.Series(all_genres).value_counts()
print(genre_counts.head(5))

# Identifying and displaying the predominant streaming service
# predominant_service = filtered_df['Streaming Services'].value_counts().idxmax()
# print(predominant_service)
df_service = pd.DataFrame({'Streaming Services': justwatch_Movie_list['Streaming Services'].apply(lambda x: x.split(', '))})
df_service = df_service[~df_service['Streaming Services'].apply(lambda x: 'Not Available for Streaming' in x)]
all_services = [service for sublist in df_service['Streaming Services'] for service in sublist]
service_counts = pd.Series(all_services).value_counts().idxmax()
print(service_counts)


# Save the filtered DataFrame to a CSV file
justwatch_Movie_list.to_csv("Unfiltered Data.csv")
filtered_df.to_csv("JustWatch Movies and TVShows Data.csv", index=False)