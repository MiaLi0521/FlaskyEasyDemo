import unittest
from flask import current_app
from app import create_app
from app import db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        # 创建上下文对象
        self.app_context = self.app.app_context()
        # 推送应用上下文
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # 当显式地推送上下文后，不需要再手动调用db.session.remove()清除数据库会话
        # db.session.remove()会在程序上下文销毁时自动触发
        # db.session.remove()
        db.drop_all()
        # 销毁应用上下文
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(self.app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
