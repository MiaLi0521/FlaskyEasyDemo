"""
404,405,500,503(表示服务器不可用)这些错误由Flask直接处理，发生错误时会触发全局的错误处理函数，
如果没有定义对应的错误处理函数，则返回默认的HTTP响应；

利用HTTP的内容协商机制，在以下错误处理函数中根据客户端请求的格式，改写响应；
"""
from flask import render_template, request, jsonify

from . import main


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500


# 405通常只发生在API中，我们直接返回json响应
@main.app_errorhandler(405)
def method_not_allowed(e):
    response = jsonify(error="The method is not allowed for the requested URL.")
    response.status_code = 405
    return response
