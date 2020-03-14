import re
import unittest
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        # 应用上下文激活以后，才可以使用db
        db.create_all()
        Role.insert_rows()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code, 200)
        self.assertIn(b'Stranger', response.data)

    def test_register_and_login(self):
        # register a new account
        response = self.client.post('/auth/register', data={
            'email': 'Bob@example.com',
            'username': 'Bob',
            'password': '123',
            'password2': '123',
        })
        self.assertEqual(response.status_code, 302)

        # login with the new account
        response = self.client.post('/auth/login', data={
            'email': 'Bob@example.com',
            'password': '123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(b'Hello,\s+Bob!', response.data))
        self.assertTrue(b'You have not confirmed your account yet.' in response.data)

        # send a confirmation token
        user = User.query.filter_by(email='Bob@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/{}'.format(token), follow_redirects=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(b'You have confirmed your account. Thanks!' in response.data)

        # logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You have been logged out.' in response.data)

