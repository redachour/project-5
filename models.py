from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *


DATABASE = SqliteDatabase('entries.db')


class User(UserMixin, Model):
    username = CharField(unique=True, max_length=80)
    password = CharField(max_length=80)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(Model):
    title = CharField(unique=True, max_length=80)
    date = CharField(max_length=80)
    time_spent = IntegerField()
    learned = TextField()
    resources = TextField()
    slug = CharField(max_length=80)
    tags = CharField(max_length=80)

    class Meta:
        database = DATABASE


def initialize():
    '''Open database, create tables, close database'''
    DATABASE.connect()
    DATABASE.create_tables([Entry, User], safe=True)
    DATABASE.close()
