"""定义应用工厂函数"""
import os

import click
from flask import Flask

# 引入自定义的包
from app.models import User, Role, Permission, Post, Follow
from config import config
from app.extensions import bootstrap, mail, moment, db, login_manager, page_down, debug_toolbar, migrate


def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app = Flask('app')
    app.config.from_object(config[config_name])  # 使用对象始化app.config
    config[config_name].init_app(app=app)

    register_extensions(app)
    register_blueprints(app)
    register_command(app)
    register_shell_context(app)

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    page_down.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    """注册蓝本:使蓝本中关联的路由和自定义错误界面生效"""
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')   # 注册身份验证蓝本
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')  # 注册API蓝本


def register_command(app):
    # 启动单元测试的命令
    @app.cli.command()
    def test():
        """run the unit test
        不推荐使用命令行的形式运行测试，一方面比较复杂，另一方面也可能存在潜在的BUG
        注：使用此方式运行测试，Selenium测试总是不通过
        """
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


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post, Follow=Follow)

