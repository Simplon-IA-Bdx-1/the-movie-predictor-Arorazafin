FROM python:3.7-buster

RUN pip install argparse mysql-connector-python beautifulsoup4 requests

COPY . /usr/srv/themoviepredictor

WORKDIR /usr/src/themoviepredictor

#CMD python /usr/src/themoviepredictor/app.py movies import --api omdb --imdbId tt3896387 --for_nb 20
#CMD python /usr/src/themoviepredictor/app.py movies import --api omdb --imdbId +100