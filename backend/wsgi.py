# Gunicorn 生产环境启动入口
# 使用命令：gunicorn --worker-class eventlet -w 1 wsgi:application

from app import app                # Flask 应用实例
import socketio                    # Socket.IO 库
from socketio_server import sio    # Socket.IO 服务器实例

# 将 Socket.IO 服务器挂载到 Flask WSGI 应用上
socketio_app = socketio.WSGIApp(sio, app)
# Gunicorn 默认寻找名为 application 的可调用对象
application = socketio_app