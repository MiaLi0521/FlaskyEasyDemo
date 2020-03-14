import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Post, Comment


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_rows()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @staticmethod
    def get_api_headers(username, password):
        return {
            'Authorization': 'Basic ' + b64encode((username + ":" + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get('/wrong/url', headers=self.get_api_headers('email', 'password'))
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get('/api/v1/posts/', content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='Bob@example.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # authenticated with the bad password
        response = self.client.get('/api/v1/posts/', headers=self.get_api_headers(u.email, 'dog'))
        self.assertEqual(response.status_code, 401)

    def test_token_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='Bob@example.com', password='cat', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        response = self.client.get('/api/v1/posts/', headers=self.get_api_headers('bad-token', ''))
        self.assertEqual(response.status_code, 401)

        # get a token
        response = self.client.post('/api/v1/token', headers=self.get_api_headers(u.email, 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # request with token
        response = self.client.get('/api/v1/posts/', headers=self.get_api_headers(token, ''))
        self.assertEqual(response.status_code, 200)

        # get a token with a token
        response = self.client.post('/api/v1/token', headers=self.get_api_headers(token, ''))
        self.assertEqual(response.status_code, 401)

    def test_anonymous(self):
        response = self.client.get('/api/v1/posts/', headers=self.get_api_headers('', ''))
        self.assertEqual(response.status_code, 401)

    def test_unconfirmed_account(self):
        # add an unconfirmed user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='Bob@example.com', password='123', confirmed=False, role=r)
        db.session.add(u)
        db.session.commit()

        # get list of posts with unconfirmed account
        response = self.client.get('/api/v1/posts/', headers=self.get_api_headers(u.email, '123'))
        self.assertTrue(response.status_code, 403)

    def test_posts(self):
        # add user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='Bob@example.com', password='123', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # write an empty post
        response = self.client.post('/api/v1/posts/', headers=self.get_api_headers(u.email, '123'),
                                    data=json.dumps({'body': ''}))
        self.assertEqual(response.status_code, 400)

        # write valid post
        response = self.client.post('/api/v1/posts/', headers=self.get_api_headers(u.email, '123'),
                                    data=json.dumps({'body': 'a post from Bob.'}))
        self.assertEqual(response.status_code, 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # get the new post
        response = self.client.get(url, headers=self.get_api_headers(u.email, '123'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response)
        self.assertEqual('http://localhost' + json_response['self_url'], url)
        self.assertEqual(json_response['body'], 'a post from Bob.')
        self.assertEqual(json_response['body_html'], '<p>a post from Bob.</p>')
        json_post = json_response

        # get the post from the user
        response = self.client.get('/api/v1/users/{}/posts/'.format(u.id),
                                   headers=self.get_api_headers(u.email, '123'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertEqual(json_response.get('count', 0), 1)
        self.assertEqual(json_response['posts'][0], json_post)

        # get the post from the user as a follower
        response = self.client.get('/api/v1/users/{}/followed/posts/'.format(u.id),
                                   headers=self.get_api_headers(u.email, '123'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertEqual(json_response.get('count', 0), 1)
        self.assertEqual(json_response['posts'][0], json_post)

        # edit post
        response = self.client.put(url, headers=self.get_api_headers(u.email, '123'),
                                   data=json.dumps({'body': 'updated body'}))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual('http://localhost' + json_response['self_url'], url)
        self.assertEqual(json_response['body'], 'updated body')
        self.assertEqual(json_response['body_html'], '<p>updated body</p>')

    def test_user(self):
        # add two users
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='Alice@example.com', username='alice', password='alice', confirmed=True, role=r)
        u2 = User(email='Bob@example.com', username='bob', password='bob', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # get users
        response = self.client.get('/api/v1/users/{}'.format(u1.id), headers=self.get_api_headers(u1.email, 'alice'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['username'], 'alice')

        response = self.client.get('/api/v1/users/{}'.format(u2.id), headers=self.get_api_headers(u2.email, 'bob'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['username'], 'bob')

    def test_comments(self):
        # add two users
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='Alice@example.com', username='alice', password='alice', confirmed=True, role=r)
        u2 = User(email='Bob@example.com', username='bob', password='bob', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # add a post
        post = Post(body='body of the post', author=u1)
        db.session.add(post)
        db.session.commit()

        # write a comment
        response = self.client.post('/api/v1/posts/{}/comments/'.format(u1.id),
                                    headers=self.get_api_headers(u2.email, 'bob'),
                                    json={'body': 'Good [post](http://example.com)!'})
        self.assertEqual(response.status_code, 201)
        # json_response = json.loads(response.get_data(as_text=True))
        json_response = response.get_json()
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        self.assertEqual(json_response['body'], 'Good [post](http://example.com)!')
        self.assertEqual(re.sub('<.*?>', '', json_response['body_html']), 'Good post!')

        # get the new comment
        response = self.client.get(url, headers=self.get_api_headers(u2.email, 'bob'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual('http://localhost' + json_response['self_url'], url)
        self.assertEqual(json_response['body'], 'Good [post](http://example.com)!')

        # add another comment
        comment = Comment(body='Thanks!', author=u1, post=post)
        db.session.add(comment)
        db.session.commit()

        # get the two comments form the post
        response = self.client.get('/api/v1/posts/{}/comments/'.format(post.id),
                                   headers=self.get_api_headers(u1.email, 'alice'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertEqual(json_response.get('total', 0), 2)