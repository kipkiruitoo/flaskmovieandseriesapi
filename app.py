from flask import Flask
import requests
from flask import request
from bs4 import BeautifulSoup
import sys

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/api/search/movie', methods=['POST'])
def searchMovie():
    query = request.form['query'].rstrip(" ")
    html_page = requests.get("https://mycima.tube/search/"+query)
    soup = BeautifulSoup(html_page.content, "lxml")

    recommended_movies = soup.find_all("div", {"class": "Thumb--GridItem"})
    links_of_recommended_movies= []


    for i in recommended_movies:
        link1 = i.find("a")

        html_page = requests.get(link1.get("href"))
        soup = BeautifulSoup(html_page.content, "lxml")

        link = soup.find("iframe", {"name": "watch"})
        watching_link = link.get("data-lazy-src")
        links_of_recommended_movies.append({
            "link": watching_link,
            "title": link1.get("title"),
            })
        
        

    
    return {
        "results": links_of_recommended_movies,
        "status": "Ok",
    }

@app.route('/api/search/series', methods=['POST'])
def searchSeries():
    query = request.form['query'].rstrip(" ")


    # Preparing our html page and soup
    html_page = requests.get("https://mycima.tube/search/"+query+"/list/series")
    soup = BeautifulSoup(html_page.content, "lxml")

    # Scraping links and titles of series resulted from the query
    recommended_series = soup.find_all("div", {"class": "Thumb--GridItem"})
    links_of_recommended_series = []

    results = [

    ]

    for i in recommended_series:
        result = {}
        link = i.find("a")
        links_of_recommended_series.append(link.get("href"))
        result["title"] = link.get("title")
        


        # Preparing html page and soup for desired series
        html_page = requests.get(link.get("href"))
        soup = BeautifulSoup(html_page.content, "lxml")


        # Scraping links and titles of seasons of the desired series
        temp_list = soup.find("div", {"class": "List--Seasons--Episodes"})
        result["seasons"] = []
        if temp_list is None:
            temp_list = soup.find("div", {"class": "Seasons--Episodes"})
            episodes_links = temp_list.findAll("a")
        else:
            seasons_links = temp_list.findAll("a")  # i.get("href")

            for i in range(len(seasons_links)):

                season = {}

                # Preparing html page and soup to be used to scrape episodes links
                html_page = requests.get(seasons_links[i].get("href"))
                soup = BeautifulSoup(html_page.content, "lxml")

                season["season"] = i +1
                season["episodes"] = [

                ]

                # Scraping episodes links and titles
                temp_list = soup.find("div", {"class": "Episodes--Seasons--Episodes"})
                episodes_links = temp_list.findAll("a")
                episodes_links.reverse()


                # Iterating through desired episodes
                for i in range(len(episodes_links)):
                    html_page = requests.get(episodes_links[i].get("href"))
                    soup = BeautifulSoup(html_page.content, "lxml")
                    link = soup.find("iframe",{"name":"watch"})
                    watching_link = link.get("data-lazy-src")
                    
                    season["episodes"].append({
                        "episode": i + 1,
                        "link" : watching_link
                    })
                
                result["seasons"].append(season) 

    results.append(result)
    return {
        "results" : results,
        "status" : "success",
    }