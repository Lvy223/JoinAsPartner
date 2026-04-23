# 开发用，一键启动
from app import app
from socketio_server import sio
from wsgi import application   # 导入组合后的 WSGI 应用
import eventlet

if __name__ == "__main__":
    # 监听 8000 端口，启动 eventlet 服务器
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 8000)), application)