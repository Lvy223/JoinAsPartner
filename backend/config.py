# 统一配置（增加 REDIS_URL）
import os  # 操作系统接口，用于读取环境变量
from datetime import timedelta  # 时间处理，用于设置token有效期


class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # ↑ 用于session加密，生产环境必须修改

    # 数据库配置（XAMPP默认无密码）
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://join_user:dagehuo12345@localhost/join_as_partner'
    # ↑ 数据库连接字符串格式：数据库+驱动://用户名:密码@主机/数据库名

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭对象修改追踪，节省内存
    SQLALCHEMY_ECHO = True  # 开发环境打印SQL语句，方便调试

    # Redis 配置 (用于缓存活动列表)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # JWT配置（用于API认证）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    # ↑ JWT加密密钥，和生产环境必须修改

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # token有效期7天
