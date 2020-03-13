import re
import threading
import time
import unittest

from selenium import webdriver

from app import create_app, db, fake
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # 启动Chrome
        # 不加载图片和CSS，加快测试速度
        prefs = {'profile.managed_default_content_settings.images':2, 'permissions.default.stylesheet':2}
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        options.add_experimental_option('prefs', prefs)
        try:
            cls.client = webdriver.Chrome(options=options)
        except:
            pass

        # 如果无法启动浏览器，跳过这些测试
        if cls.client:
            # 创建应用
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # 禁止日志，保持输出简洁
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # 创建数据库，并使用一些虚拟数据填充
            db.create_all()
            Role.insert_rows()
            fake.users(10)
            fake.posts(10)

            # 添加管理员
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(email='admin@example.com', username='admin', password='admin', role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # 在一个线程中启动Flask服务器
            cls.server_thread = threading.Thread(target=cls.app.run, kwargs={'debug': False})
            cls.server_thread.start()
            # 确保服务器已完成启动
            time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 关闭Flask服务器和浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            # 销毁数据库
            db.drop_all()
            db.session.remove()

            # 删除应用上下文
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # 进入首页
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s*Stranger!', self.client.page_source))

        # 进入登录页面
        self.client.find_element_by_link_text('Log In').click()
        self.assertIn('<h1>Login</h1>', self.client.page_source)
        time.sleep(2)

        # 登录
        self.client.find_element_by_name('email').send_keys('admin@example.com')
        self.client.find_element_by_name('password').send_keys('admin')
        self.client.find_element_by_name('submit').click()
        time.sleep(2)
        self.assertTrue(re.search('Hello,\s*admin', self.client.page_source))

        # 进入用户资料页面
        self.client.find_element_by_link_text('Profile').click()
        self.assertIn('<h1>admin</h1>', self.client.page_source)


