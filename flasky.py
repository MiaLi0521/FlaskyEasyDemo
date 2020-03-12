import os

import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission, Post, Follow

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post, Follow=Follow)


# 启动单元测试的命令
@app.cli.command()
def test():
    """run the unit test"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# 产生虚拟数据
@app.cli.command()
@click.option('--user', default=50, help="Quantity of users, default is 50")
@click.option('--post', default=100, help="Quantity of posts, default is 100")
@click.option('--follow', default=300, help="Quantity of follows, default is 100")
@click.option('--comment', default=300, help="Quantity of follows, default is 100")
def forge(user, post, follow, comment):
    """create the fake data"""
    from app.fake import admin, users, posts, follows, comments
    click.echo('init db...')
    db.drop_all()
    db.create_all()
    click.echo('init role...')
    Role.insert_rows()
    click.echo('create admin...')
    admin()
    click.echo('create users...')
    users(user)
    click.echo('create posts...')
    posts(post)
    click.echo('create follows...')
    follows(follow)
    click.echo('create comment...')
    comments(comment)

