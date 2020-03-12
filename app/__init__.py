"""定义应用工厂函数"""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_login import LoginManager
from flask_pagedown import PageDown

# 引入自定义的包
from config import config

# 应用实例尚未初始化，此处创建扩展类时没有向构造函数传入参数，扩展并未真正初始化
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
page_down = PageDown()
# 设置登录页面的路由端点
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    # 使用对象始化app.config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app=app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    page_down.init_app(app)

    # 注册蓝本:使蓝本中关联的路由和自定义错误界面生效
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册身份验证蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册API蓝本
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app

