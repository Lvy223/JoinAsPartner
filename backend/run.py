# 开发用，一键启动
import socketio
from app import app
from socketio_server import sio

# 创建 Socket.IO 组合应用
socketio_app = socketio.WSGIApp(sio, app)

# 使用 Python 内置的 WSGI 服务器（开发用）
# 必须 import simple_websocket 以激活 WebSocket 支持
import simple_websocket
from wsgiref.simple_server import make_server

with make_server('0.0.0.0', 8000, socketio_app) as httpd:
    print("服务运行在 http://0.0.0.0:8000")
    httpd.serve_forever()