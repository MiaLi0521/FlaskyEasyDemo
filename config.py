import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask-WTF扩展必须的秘钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    # 电子邮件默认配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # 发送电子邮件时应用层面需要的配置
    APP_MAIL_SUBJECT_PREFIX = '[FROM FLASK APP]'
    APP_MAIL_SENDER = 'Flask Admin <{}>'.format(MAIL_USERNAME)
    APP_ADMIN = os.environ.get('APP_ADMIN')

    # 在不需要跟踪对象变化时降低消耗
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 分页时每页的记录数
    FLASKY_POSTS_PER_PAGE = int(os.environ.get('FLASKY_POSTS_PER_PAGE') or '10')
    FLASKY_FOLLOWERS_PER_PAGE = 2
    FLASKY_COMMENTS_PER_PAGE = 2

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    # 未指定环境变量时，测试换将将使用内存数据库sqlite
    SQLALCHEMy_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
