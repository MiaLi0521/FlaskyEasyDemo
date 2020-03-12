"""main模块的蓝本：在蓝本中定义路由和错误处理程序"""
from flask import Blueprint

# 参数：蓝本的名称和蓝本所在的包或模块
main = Blueprint('main', __name__)

# 把路由和错误处理程序与蓝本关联起来
from . import views, error
from ..models import Permission


# 把Permission类加入模板上下文，以便访问类中定义的常量
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
