FROM ubuntu:16.04

MAINTAINER Selman ALPDUNDAR <selman.alp@hotmail.com.tr>

RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-setuptools python3-pip git

ADD . /code
WORKDIR code

RUN python3 -m pip install -r requirements.txt

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV FLASK_APP auth_service/app.py

EXPOSE 5002

# bind to 0.0.0.0 will make Docker works
CMD ["flask","run","--host", "0.0.0.0"]