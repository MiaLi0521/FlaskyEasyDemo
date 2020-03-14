"""应用实例尚未初始化，此处创建扩展类时没有向构造函数传入参数，扩展并未真正初始化"""
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
page_down = PageDown()
debug_toolbar = DebugToolbarExtension()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # 设置登录页面的路由端点


@login_manager.user_loader
def load_user(user_id):
    """在Flask-Login需要获取已登录用户的信息时调用"""
    from app import User
    return User.query.get(int(user_id))
