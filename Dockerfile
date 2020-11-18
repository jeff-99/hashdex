FROM python:3.8-alpine

ADD . /app

WORKDIR /app

VOLUME /media
VOLUME /db

RUN python setup.py install

ENTRYPOINT [ "hashdex" ]
