
# Projet The Movie Predictor

## Prerequisite
- Docker
- python 3.7

## Database : Create MySQL Tables

### `Movies` table

#### Fill movies table

- Retreive elements of `Movies` table from the imdb dataset. The used files are:  
    - title.basics.tsv.gz
    - title.ratings.tsv.gz  
- Dezipped files and rename the file whithout the .gz extension  
- Put both files in the ```/files/``` folder

Movies will be retreived year by year changing the 'year' in the command below :  
```  $ python app.py movies import --datasetTitleFile_year '2019' ```

#### List `Movies` table

- The command to list the table movies.  
```  $ python app.py movies list ```  
Note that this list the first 50 elements in he table

#### Retreive the movie with ID number  
- the command is :  
```  $ python app.py movies find '2000' ```

### `People` table
- Retreive elements of `People` table from the imdb dataset. The  used file is:  
    - name.basics.tsv.gz  
- no need to Dezip files  
- Put both file in the ```/files/``` folder  
- the command is 
```  $ python app.py people import --dataSetPeople 'name.basics.tsv.gz' ```  

#### List `people` table

- The command to list the table movies.  
```  $ python app.py people list ```  
Note that this list the first 50 elements in he table

#### Retreive a people with ID number  
- the command is :  
```  $ python app.py people find '2000' ```


## Movie Score Prediction



