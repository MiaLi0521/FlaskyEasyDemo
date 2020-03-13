import os
import sys

COV = None
if os.getenv('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()

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
@click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')
def test(coverage):
    """run the unit test
    不推荐使用命令行的形式运行测试，一方面比较复杂，另一方面也可能存在潜在的BUG
    注：使用此方式运行测试，Selenium测试总是不通过
    """
    if coverage and not os.getenv('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        # ['flask', 'test', '--coverage'] 命令行参数列表
        # 3.5之前没有subprocess.run()，故使用subprocess.call(),缺点是该方法返回的是命令的退出码，无法捕获命令输出内容
        sys.exit(subprocess.call(sys.argv))

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://{}/index.html'.format(covdir))
        COV.erase()


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
