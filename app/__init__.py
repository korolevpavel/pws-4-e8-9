from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

db.create_all()

from app import controllers, models
