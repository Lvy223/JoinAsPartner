# JWT 校验 + 生成 + login_required 装饰器
# 提供 HTTP 请求验证 和 WebSocket 连接验证两种方式

import jwt
from flask import request, g, jsonify
from functools import wraps
from datetime import datetime
from config import Config
from models import User
from urllib.parse import parse_qs


def verify_token():
    """
        用于普通 Flask HTTP 路由的 JWT 验证。
        从 request.args 中获取 token 参数。
        返回 user_id 或 None。
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = request.args.get("token")
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except Exception:
        return None

def get_token_from_environ(environ):
    """
       专门用于 Socket.IO 连接时的 token 提取。
       environ 是 WSGI 环境字典，包含 'QUERY_STRING'。
       客户端通过 URL 参数 ?token=xxx 连接。
    """
    query_string = environ.get('QUERY_STRING', '')     # 获取查询字符串部分
    params = parse_qs(query_string)                    # 解析为字典，如 {'token': ['abc']}
    token = params.get('token', [None])[0] # 取列表的第一个元素
    return token

def create_token(user_id):
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def login_required(f):
    """登录验证装饰器，从 Authorization 头获取 token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'code': 401, 'message': '未提供认证令牌'}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({'code': 401, 'message': '认证令牌格式错误'}), 401
        token = parts[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.query.get(user_id)
            if not user:
                return jsonify({'code': 401, 'message': '用户不存在'}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效令牌'}), 401
        return f(*args, **kwargs)
    return decorated_function