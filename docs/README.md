# How I met Corona
https://howimetcorona.herokuapp.com/

![Header](header.png)

## Introduction

### Problem
All over the world people are encouraged to practice SocialDistancing. However, contact with fellow human beings cannot always be avoided and thus, for example, an infection can occur while shopping. In the case of symptoms you are asked to go into quarantine at home. It is estimated that one third of those infected have a mild course and therefore do not always attribute their symptoms to the virus. In addition, up to 24 hours before the first symptoms appear, infected persons are at risk of infection. 

### Opportunity

A large part of the population uses smartphones and the Google Maps application. In many cases, this application stores the movement profile of the user, which can then be downloaded. 

### Solution

Infected people can donate their movement profile of the last few weeks. Other users can now also upload their movement profile. This is then compared with the data in the database, and in the event of overlaps, the user is informed where and when he or she may have come into contact with infected persons. This enables the user to act responsibly and to adapt his behaviour accordingly.


## Requirements

- Python 3
- Postgres


## Setup

### Clone repo

With https:
```bash
git clone https://github.com/nicoknoll/howimetcorona.git
```

Or with ssh:
```bash
git clone git@github.com:nicoknoll/howimetcorona.git
```

### Setup venv

In the same directory you entered `git clone` (not inside the "howimetcorona" directory) enter:
```bash
python3 -m venv howimetcorona-env
source howimetcorona-env/bin/activate 
```

Enter the prodject directory:
```bash
cd howimetcorona
```

Install the requirements:
```bash
pip install -r requirements.txt
```

### Create .env file

The `.env` file should contain your database connection string and the `DEBUG` setting:

```bash
DATABASE_URL=postgres://USERNAME:PASSWORD@HOST:PORT/DATABASE
DEBUG=1
```

### Run initial migrations

```bash
python manage.py migrate
```

### Run server

```bash
python manage.py runserver
```

Now you can access the application on `http://localhost:8000`
