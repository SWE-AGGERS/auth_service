
# SocialDice Auth Service
[![Build Status](https://travis-ci.org/SWE-AGGERS/SocialDice.svg?branch=reactions)](https://travis-ci.org/SWE-AGGERS/SocialDice)
[![Coverage Status](https://coveralls.io/repos/github/SWE-AGGERS/SocialDice/badge.svg?branch=develop)](https://coveralls.io/github/SWE-AGGERS/SocialDice?branch=develop)
## Starting docker
* docker build .
* docker tag <image_id> auth_service
* docker run -p 5000:5000 --name auth auth_service

## Prepare Flask App Environment
* python3 -m venv venv
* . ./venv/bin/activate
* pip3 install -r requirements.txt


## Run Flask App
* export FLASK_APP=auth_service/app.py
* flask run

## Testing
* tox TOX_ENV=py36
