"""Faker生成虚拟用户和文章"""
import os
from random import randint, random

from sqlalchemy.exc import IntegrityError
from faker import Faker

from . import db
from .models import User, Post, Comment


def admin():
    admin = User(email=os.getenv('APP_ADMIN'),
                 username='admin',
                 password='admin123',
                 confirmed=True,
                 name='flasky admin',
                 location='zhangjiakou',
                 about_me="website admin",

                 )
    db.session.add(admin)
    db.session.commit()


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()


def follows(count=100):
    for i in range(count):
        user = User.query.get(randint(1, User.query.count()))
        user.follow(User.query.get(randint(1, User.query.count())))


def comments(count=300):
    fake = Faker()
    for i in range(count):
        user = User.query.get(randint(1, User.query.count()))
        post = Post.query.get(randint(1, Post.query.count()))
        comment = Comment(body=fake.text(),
                          timestamp=fake.past_date(),
                          author=user,
                          post=post)
        db.session.add(comment)
    db.session.commit()
