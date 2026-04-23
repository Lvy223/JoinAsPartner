# Redis 封装
# 提供全局唯一的 Redis 连接实例，使用连接池提高性能

import redis
from config import Config

# 创建连接池，复用连接以提升性能
pool = redis.ConnectionPool.from_url(Config.REDIS_URL, decode_responses=True, max_connections=50)
# 全局 Redis 客户端实例，所有模块共用
redis_client = redis.Redis(connection_pool=pool)

# 使用说明：
# - 存储 userId <-> sid 映射
# - 存储离线消息队列 (List)
# - 维护在线用户集合 (Set)
# - 维护活动成员集合 (Set)
