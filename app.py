#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TheMoviePredictor script
Author: Arnaud de Mouhy <arnaud@admds.net>
modified by Aro
"""

import mysql.connector
import sys
import argparse
import csv
import os
import socket
import time
from datetime import datetime
from datetime import date
import gzip

import pandas as pd

from omdb import OMDBApi
from movie import Movie
from person import Person


def connectToDatabase():
    return mysql.connector.connect(user='predictor', password='predictor',
                              host='localhost',
                              database='predictor')   #host='database' host='127.0.0.1'



#def isOpen(ip,port):
#   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#   try:
#      s.connect((ip, int(port)))
#      s.shutdown(2)
#      return True
#   except:
#      return False

#def connectToDatabase():
#    host = 'databse' #os.environ['host_db']
#    while isOpen(host, 3306) == False:
#        print("En attente de la BDD...")
#        #time.sleep(5)
#    return mysql.connector.connect(user='predictor', password='predictor',
#                              host='database',
#                              database='predictor')   #host='database' host='127.0.0.1'

def disconnectDatabase(cnx):
    cnx.close()

def createCursor(cnx):
    return cnx.cursor(dictionary=True)

def closeCursor(cursor):    
    cursor.close()

def findQuery(table, id):
    return ("SELECT * FROM {} WHERE id = {} LIMIT 1".format(table, id))

def find_last_imdbId_Query (table,field, id):
    #return (f"SELECT `imdbID` FROM `movies` where `id` = 125;)
    return ("SELECT {} FROM {} where `id` = {}".format(field,table,id))

def find_last_imdbId(table,field):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute("SELECT `id` FROM {} ORDER BY `id` DESC LIMIT 1;".format(table))
    last_id = cursor.fetchone()
    last_id = last_id['id'] 
    cursor.execute(find_last_imdbId_Query (table,field, last_id))
    imdbId_last = cursor.fetchone()
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return imdbId_last
    

def findAllQuery(table):
    return ("SELECT * FROM {} LIMIT 50".format(table))

#def insert_people_query(People):
#    return (f"INSERT INTO `people` (`firstname`, `lastname`) VALUES ('{People.firstname}', '{People.lastname}');")

def insert_people_query(People):
    return (f"INSERT INTO `people` (`imdbId`, `fullname`) VALUES ('{People.imdbId}', '{People.fullname}') ON DUPLICATE KEY UPDATE id=id;")

def insert_movie_query(movie):
    insert_stmt = (
        "INSERT INTO `movies` (`imdbId`,`original_title`,`title`, `genres`,`duration`, `release_date`,`rating`, `synopsis`, `boxOffice`,`imdbScore`) "
        "VALUES (%s, %s, %s, %s, %s,%s, %s,%s,%s,%s)"
    )
    data = (movie.imdbId, movie.original_title, movie.title,movie.genres,movie.duration, movie.release_date, movie.rating,movie.synopsis,movie.boxOffice,movie.imdbScore)
    return (insert_stmt, data)





def find(table, id):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    query = findQuery(table, id)
    cursor.execute(query)
    results = cursor.fetchall()

    entity = None
    if (cursor.rowcount == 1):
        row = results[0]
        if (table == "movies"):
            entity = Movie(title=row['title'], original_title=row['original_title'], duration=row['duration'], release_date=row['release_date'], rating=row['rating'],imdbScore=row['imdbScore'],genres=row['genres'],imdbId=row['imdbId'])
        if (table == "people"):
            entity = People(row['firstname'], row['lastname'])
        entity.id = row['id']

    closeCursor(cursor)
    disconnectDatabase(cnx)

    return entity

def findAll(table):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(findAllQuery(table))
    results = cursor.fetchall() # liste de dictionnaires contenant des valeurs scalaires
    closeCursor(cursor)
    disconnectDatabase(cnx)
    if (table == "movies"):
        movies = []
        for result in results: # result: dictionnaire avec id, title, ...
            movie = Movie(
                title=result['title'],
                original_title=result['original_title'],
                duration=result['duration'],
                release_date=result['release_date'],
                rating=result['rating'],
                imdbId=result['imdbId'],
                genres=result['genres'],
                imdbScore=result['imdbScore']
            )
            movie.id = result['id']
            movies.append(movie)
        return movies
    if (table == "people"):
        people = []
        for result in results: # result: dictionnaire avec id, title, ...
            p = Person(
                firstname = result['firstname'],
                lastname = result['lastname'],
            )
            p.id = result['id']
            people.append(p)
        return people

def insert_people(People):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(insert_people_query(People))
    cnx.commit()
    last_id = cursor.lastrowid
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return last_id

def insert_movie(movie):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    #cursor.execute(insert_movie_query(movie))
    (insert_stmt, data) = insert_movie_query(movie)
    cursor.execute(insert_stmt, params=data)
    cnx.commit()
    last_id = cursor.lastrowid
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return last_id

def printPerson(person):
    print("#{}: {} {}".format(person.id, person.firstname, person.lastname))

def printMovie(movie):
    print("#{}: {} - released on {} - with an average score of {}".format(movie.id, movie.title, movie.release_date.year,movie.imdbScore))

parser = argparse.ArgumentParser(description='Process MoviePredictor data')

parser.add_argument('context', choices=('people', 'movies'), help='Le contexte dans lequel nous allons travailler')

action_subparser = parser.add_subparsers(title='action', dest='action')

list_parser = action_subparser.add_parser('list', help='Liste les entitées du contexte')
list_parser.add_argument('--export' , help='Chemin du fichier exporté')

find_parser = action_subparser.add_parser('find', help='Trouve une entité selon un paramètre')
find_parser.add_argument('id' , help='Identifant à rechercher')

import_parser = action_subparser.add_parser('import', help='Importer un fichier CSV')
import_parser.add_argument('--file', help='Chemin vers le fichier à importer', required=False)
import_parser.add_argument ('--api', help='choix de l\'api à utiliser', required = False)
import_parser.add_argument ('--imdbId', help='ID imdb à importer depuis une API', required = False)
import_parser.add_argument ('--for_nb', help='Nombre de film à importer à partir du imdbId', required = False)
import_parser.add_argument('--datasetTitleFile_year', help='year into dataset file to import', required=False)
import_parser.add_argument('--datasetPeopleZip', help='name dataset file to import', required=False)


insert_parser = action_subparser.add_parser('insert', help='Insert une nouvelle entité')
known_args = parser.parse_known_args()[0]

if known_args.context == "people":
    insert_parser.add_argument('--firstname' , help='Prénom de la nouvelle personne', required=True)
    insert_parser.add_argument('--lastname' , help='Nom de la nouvelle personne', required=True)

if known_args.context == "movies":
    insert_parser.add_argument('--title' , help='Titre en France', required=True)
    insert_parser.add_argument('--duration' , help='Durée du film', type=int, required=True)
    insert_parser.add_argument('--original-title' , help='Titre original', required=True)
    insert_parser.add_argument('--release-date' , help='Date de sortie en France', required=True)
    insert_parser.add_argument('--rating' , help='Classification du film', choices=('TP', '-12', '-16'), required=True)

args = parser.parse_args()

if args.context == "people":
    if args.action == "list":
        people = findAll("people")
        for person in people:
            if args.export:
                with open(args.export, 'w', encoding='utf-8', newline='\n') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(people[0].__dict__.keys())
                    for person in people:
                        writer.writerow(person.__dict__.values())
            else:
                printPerson(person)
    if args.action == "find":
        peopleId = args.id
        people = find("people", peopleId)
        if (people == None):
            print(f"Personne avec l'id {peopleId} n'a été trouvé ! Try Again!")
        else:
            printPerson(people)
    if args.action == "insert":
        print(f"Insertion d'une nouvelle personne: {args.firstname} {args.lastname}")
        people = Person (firstname=args.firstname, lastname=args.lastname)
        people_id = insert_people(people)
        print(f"Nouvelle personne insérée avec l'id '{people_id}'")

    if args.action == "import":
        if args.datasetPeopleZip:
            filePeople ='./files/' + args.datasetPeopleZip
            with gzip.open(filePeople, 'rt', encoding = 'utf-8') as tsvfile:
                rows = csv.DictReader(tsvfile, delimiter="\t", quoting = csv.QUOTE_NONE) 
#                for i, row in enumerate(rows):
#                    if i > 100:
#                       break     
                for row in rows:
                    people = Person (
                                    imdbId = row['nconst'],
                                    fullname = row['primaryName'].replace("'", "\\'")
                                    )
                    people_id = insert_people (people)
                    print(f"Nouvelle personne insérée avec l'id '{people_id}'")

if args.context == "movies":
    if args.action == "list":  
        movies = findAll("movies")
        for movie in movies:
            printMovie(movie)

    if args.action == "find":  
        movieId = args.id
        movie = find("movies", movieId)
        if (movie == None):
            print(f"Aucun film avec l'id {movieId} n'a été trouvé ! Try Again!")
        else:
            printMovie(movie)
    if args.action == "insert":
        print(f"Insertion d'un nouveau film: {args.title}")
        movie = Movie(args.title, args.original_title, args.duration, args.release_date, args.rating)
        movie_id = insert_movie(movie)
        print(f"Nouveau film inséré avec l'id '{movie_id}'")
    if args.action == "import":
        if args.file:
            with open(args.file, 'r', encoding='utf-8', newline='\n') as csvfile:
                reader = csv.DictReader(csvfile)    
                for row in reader:
                    movie = Movie(
                            title = row['title'],
                            original_title = row['original_title'],
                            duration = row['duration'],
                            rating = row['rating'],
                            release_date = row['release_date']
                    )
                    movie_id = insert_movie(movie)
                    print(f"Nouveau film inséré avec l'id '{movie_id}'")
        
        
        if args.datasetTitleFile_year:
            fileTsv_basics = 'files/title.basics.tsv'
            fileTsv_ratings = 'files/title.ratings.tsv'
            with open(fileTsv_basics, 'r', encoding='utf-8') as csvfile:
                reader_movies = csv.DictReader(csvfile, dialect='excel-tab') # Reader dans un dictionnaire
                pd_reader_movies = pd.DataFrame.from_dict(reader_movies,dtype=str)
            with open(fileTsv_ratings, 'r', encoding='utf-8') as csvfile:
                reader_ratings = csv.DictReader(csvfile,dialect='excel-tab')    
                pd_reader_ratings = pd.DataFrame.from_dict(reader_ratings, dtype=str)
            pd_movies_ratings = pd_reader_movies.join(pd_reader_ratings.set_index('tconst'), on='tconst')
            #pd_movies_ratings.info()
            pd_movies_ratings = pd_movies_ratings[pd_movies_ratings['startYear'] == args.datasetTitleFile_year]
            #print()
            pd_movies_ratings = pd_movies_ratings.reset_index()
            #pd_movies_ratings.info()
            #print(pd_movies_ratings.loc[1,'genres'])
            #exit()
            for r in range(0,pd_movies_ratings.shape[0]):
                #if pd_movies_ratings.loc[r,'startYear'].isnumeric() == False:
                #     release_year_date = 0
                #else:
                release_year_date = int(pd_movies_ratings.loc[r,'startYear'])

                if pd_movies_ratings.loc[r,'runtimeMinutes'].isnumeric() == False:
                    duration = 0
                else:
                    duration = int(pd_movies_ratings.loc[r,'runtimeMinutes'])
               
                if pd.isna(float(pd_movies_ratings.loc[r,'averageRating'])) == False:   
                    if pd_movies_ratings.loc[r,'isAdult']!=1 and pd_movies_ratings.loc[r,'titleType'] == 'movie':
                    #print(next(reader))
                        movie = Movie(
                                title = pd_movies_ratings.loc[r,'primaryTitle'],
                                original_title = pd_movies_ratings.loc[r,'originalTitle'],
                                duration = duration,
                                rating = "",
                                release_date = datetime(release_year_date, 1, 1),
                                genres = pd_movies_ratings.loc[r,'genres'],
                                imdbId = pd_movies_ratings.loc[r,'tconst'],
                                imdbScore = pd_movies_ratings.loc[r,'averageRating']
                                )
                        movie_id = insert_movie(movie)
                        print(f"Nouveau film inséré avec l'id '{movie_id}'")
        
        if args.api != None :
            if args.api == "omdb":
                if args.imdbId == "+100":
                     last_imdbId = find_last_imdbId("movies","imdbId")
                     last_imdbId = last_imdbId['imdbId'] 
                     for i in range (1,100):
                        id_number = last_imdbId.strip().split("tt")[1]
                        omdb = OMDBApi()
                        id_number = int(id_number) + i
                        omdbID = 'tt'+ str(id_number)
                        movie = omdb.get_movie (omdbID)
                        if movie == "NoMovie":
                            print (omdbID, "No movie for this imdbId")
                            print()
                        else :
                            movie_id = insert_movie(movie)
                            print(f"New movie is integrated at id number '{movie_id}'")
                            print()
                else: 
                    id_number = args.imdbId
                    omdb = OMDBApi()
                    id_number = int(id_number) + i
                    omdbID = 'tt'+ str(id_number)
                    movie = omdb.get_movie (omdbID)
                    if movie == "NoMovie":
                        print (omdbID, "No movie for this imdbId")
                        print()
                    else :
                        movie_id = insert_movie(movie)
                        print(f"Nouveau film inséré avec l'id '{movie_id}'")
                        #print (movie.__dict__)
                        #print()
                        #print ('ImdbId : ', movie.imdbId)
                        #print ('Original title : ', movie.original_title)
                        #print ('Title : ', movie.title)
                        #print ('Release date : ', movie.release_date)
                        #print ('Rating : ', movie.rating)
                        #print ('Duration : ', movie.duration)
                        #print ('Synopsis : ', movie.synopsis)
                        #print ('Box Office : ', movie.boxOffice)
                        #print ('Score : ', movie.imdbScore)
                        #movie_id = insert_movie(movie)
                        #print(f"Nouveau film inséré avec l'id '{movie_id}'")
                        print()