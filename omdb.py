import requests
import os
import json
import key_file
from datetime import datetime
import person
from movie import Movie

dossier_courant = os.path.dirname(__file__)

class OMDBApi:

    ENDPOINT = 'www.omdbapi.com'
    
    def __init__(self):
        api_key = key_file.omdb_key
        self.query_params = {"apikey" : api_key}
        
    def get_movie(self, imdb_id):
        params = self.query_params
        params.update({
            "i": imdb_id
        })
        response = requests.get(f"https://{OMDBApi.ENDPOINT}/", params=params)
        print(response.url)
        #print(response.content)
        if (response.status_code != 200):
            print("Error in request")
            return None
        dict_response = response.json()
        return self.movie_from_json(dict_response)

    def movie_from_json(self, dict_movie):
        if dict_movie['Response'] == "False":
            movie ="NoMovie" 
        else :
            imdbId = dict_movie['imdbID']
        
            original_title = dict_movie['Title']

            title = None
        
            duration = dict_movie['Runtime']
            if duration == "N/A":
                duration = None
            else :
                duration = dict_movie['Runtime'].strip().split(" ")[0]
        
            
            release_date =dict_movie['Released']
            if release_date == "N/A":
                release_date_string = None
            else :
                release_date = datetime.strptime(dict_movie['Released'], '%d %b %Y')
                release_date_string = release_date.strftime('%Y-%m-%d')
        
            rating = dict_movie['Rated']
            if rating == 'PG-13':
                 rating = "-12"
            elif  rating == "TV-14":
                rating = "-16"
            elif rating == 'X':
                rating = "-18"
            else : 
                rating = None
        
        
            synopsis = dict_movie['Plot']

            if 'BoxOffice' in dict_movie:
                boxOffice = dict_movie['BoxOffice']
            else: 
                boxOffice = None

            score = dict_movie['imdbRating']
            if score == "N/A":
                score = None
            else :
                score = score
             


            movie = Movie(imdbId, original_title, title, duration, release_date_string, rating)
        
            movie.synopsis = synopsis
            movie.boxOffice = boxOffice
            movie.imdbScore = score
        
        
        #print(movie.__dict__)
        return movie

    

"""
imdb_id = "tt3896196"

url2 = f"http://www.omdbapi.com/?i={imdb_id}&apikey={token}&"

response= requests.get(url2)

response_json = response.json() #réponse sous format JSON

#### data liées à la table movies
vtitle = response_json['Title']

vrating = response_json['Rated']
if vrating == "N/A":
    rating = None
elif vrating == '13':
    rating = "-12"
else : 
    rating = vrating


vdate = response_json['Released']
release_date_object = datetime.strptime(vdate, '%d %b %Y')
release_date_sql_string = release_date_object.strftime('%Y-%m-%d')

vduration = response_json['Runtime']
duration = vduration.strip().split(" ")[0]

vsynopsis = response_json['Plot']

vactors = response_json['Actors']
actors_list = vactors.split(",")
actors = []
#print (actors_list)
for i in actors_list:
    i1 = i.strip()
    p = person.Person(firstname = i1.split(" ")[0], lastname = i1.split(" ")[1])
    #print (p.full_name())
    actors.append(p)

for i in actors:
    print('actors :', i.full_name())

#print('actors : ', actors[0].__dict__)
#print('actors : ', actors.__dict__)


print("Title : ", vtitle)
print("rating : ", rating)
print("release date : ", release_date_sql_string)
print("duration : ",duration)
print("synopsis : ", vsynopsis)
#print('actors : ', vactors)

"""