from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('id', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1)
    first = url_for('api.get_user_posts', id=id, page=1)
    last = url_for('api.get_user_posts', id=id, page=pagination.pages)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'first': first,
        'next': next,
        'prev': prev,
        'last': last,
        'count': pagination.total,
        'pages': pagination.pages
    })


@api.route('/users/<int:id>/followed/posts/')
def get_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_followed_posts', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_followed_posts', id=id, page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'pages': pagination.pages,
        'first': url_for('api.get_followed_posts', id=id, page=1),
        'last': url_for('api.get_followed_posts', id=id, page=pagination.pages)
    })
