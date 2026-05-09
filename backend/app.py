# Flask 主入口（健康检查 + 初始化 + CLI命令）
# 负责提供 HTTP 接口（如健康检查），并通过 wsgi.py 与 Socket.IO 结合

import eventlet
eventlet.monkey_patch()

import socketio
from socketio_server import sio

import logging
import click
from datetime import datetime  # 时间处理

from flask_migrate import Migrate
from flask import Flask, jsonify  # Flask核心组件
from flask_cors import CORS  # 跨域支持
from sqlalchemy import text

from config import Config
from models import db
from redis_client import redis_client   # 导入 Redis 客户端
from routes.activity import activity_bp # 导入活动相关的蓝图
from routes.auth import auth_bp
from utils import hash_password, generate_anonymous_nickname

# 添加日志配置
logging.basicConfig(level=logging.INFO)

# 创建 Flask 应用实例
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
CORS(app)                     # 允许跨域
db.init_app(app)              # 初始化 SQLAlchemy
migrate = Migrate(app, db)

# 注册蓝图，使蓝图中的路由生效
app.register_blueprint(activity_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 健康检查端点（用于负载均衡、K8s 等）
@app.route("/health")
def health():
    # 可增加数据库和 Redis 的连通性检查（可选）
    try:
        redis_client.ping()
        # 使用 text() 或直接执行简单查询
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "services": {"db": "ok", "redis": "ok"}})
    except Exception as e:
        return jsonify({"status": "degraded", "error": str(e)}), 500

# CLI 命令：初始化数据库表
@app.cli.command("init-db")
def init_db():
    """创建所有数据库表（基于 models.py 中的定义）"""
    click.echo("正在创建数据库表...")
    db.create_all()
    click.echo("✅ 数据库表创建成功")

# ============================================================
# CLI 命令：添加测试数据（方便开发调试）
# ============================================================
@app.cli.command("seed-data")
def seed_data():
    """填充测试数据：普通用户、匿名用户、示例活动、参与记录等"""
    from models import User, Activity, UserActivity

    click.echo("开始添加测试数据...")

    # 1. 创建测试普通用户
    test_user = User.query.filter_by(username="test_user").first()
    if not test_user:
        test_user = User(
            username="test_user",
            nickname="测试用户",
            phone="13800138000",
            password_hash=hash_password("123456"),
            interests=["跑步", "摄影", "读书"],
            credit_score=100,
            is_anonymous=0
        )
        db.session.add(test_user)
        click.echo("  - 创建测试用户: test_user / 123456")

    # 2. 创建匿名用户
    anon_user = User.query.filter_by(username="anon_demo").first()
    if not anon_user:
        anon_user = User(
            username="anon_demo",
            nickname=generate_anonymous_nickname(),
            password_hash=hash_password("anonymous"),
            is_anonymous=1
        )
        db.session.add(anon_user)
        click.echo("  - 创建匿名用户演示账号")

    db.session.commit()

    # 3. 创建示例活动（如果不存在）
    demo_activity = Activity.query.filter_by(title="周末校园跑步活动").first()
    if not demo_activity:
        demo_activity = Activity(
            creator_id=test_user.id,
            title="周末校园跑步活动",
            description="一起在操场跑步，5公里慢跑",
            category="运动",
            tags=["跑步", "健康"],
            start_time=datetime(2025, 5, 10, 8, 0, 0),
            end_time=datetime(2025, 5, 10, 10, 0, 0),
            location_name="学校操场",
            max_participants=10,
            current_participants=1,
            status=1  # 报名中
        )
        db.session.add(demo_activity)
        click.echo("  - 创建示例活动: 周末校园跑步活动")

        # 创建者自动加入
        creator_join = UserActivity(
            user_id=test_user.id,
            activity_id=demo_activity.id,
            role=3,
            status=1
        )
        db.session.add(creator_join)

    db.session.commit()
    click.echo("✅ 测试数据添加成功")

if __name__ == "__main__":
    socketio_app = socketio.WSGIApp(sio, app)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8000)), socketio_app)