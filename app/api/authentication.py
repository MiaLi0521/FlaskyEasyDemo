"""
Flask-httpauth为了像flask-login一样使用login_required装饰器，需要分别注册verify_password回调和auth_error回调
"""
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """即支持密码验证，也支持token验证"""
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if g.current_user.is_authenticated and not g.current_user.confirmed:
        return forbidden('Unconfirmed account.')


@api.route('/token', methods=['POST'])
def get_token():
    """客户端申请令牌时，必须使用邮箱验证"""
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})

