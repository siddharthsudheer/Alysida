FROM python:3

ENV GUNICORN_WORKERS=5

EXPOSE 4200 4201

WORKDIR /alysida

ADD . /alysida

RUN pip install -r requirements.txt

# ONLY FOR DEV
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev



