# Socket.IO 事件处理器
# 负责 WebSocket 连接管理、房间加入、消息广播、断开清理

import socketio
import time
import json
from redis_client import redis_client
from config import Config
import jwt
from auth import get_token_from_environ

# 创建 Redis 适配器，使多个 Gunicorn Worker 之间可以共享房间和连接状态
mgr = socketio.RedisManager(
    url=Config.REDIS_URL,
    channel='socketio',  # 内部通信频道名，用于 Worker 间消息传递
    write_only=False  # 需要双向通信（读写都需要）
)

# 初始化 Socket.IO 服务器
sio = socketio.Server(
    async_mode="eventlet",  # 配合 gunicorn 的 eventlet worker，性能更好
    client_manager=mgr,  # 挂载 Redis 适配器，使多 Worker 共享状态
    cors_allowed_origins="*",  # 允许跨域（生产环境建议限制为前端域名）
    ping_interval=25,  # 每 25 秒发送一次 ping 包，保持连接活跃
    ping_timeout=60  # 若 60 秒未收到 pong 响应，则断开连接
)


# -------------------------------------------------------------------
# 工具函数：将消息存入用户的离线队列
# -------------------------------------------------------------------
def save_offline_message(user_id, message):
    """
    将消息对象序列化为 JSON 字符串，存入 Redis List 右侧。
    离线消息在用户下次连接时会被拉取。
    """
    key = f"offline_msg:{user_id}"  # 键名格式：offline_msg:123
    redis_client.rpush(key, json.dumps(message, ensure_ascii=False))  # 中文不转义
    # 设置过期时间为 7 天 (604800 秒)
    redis_client.expire(key, 604800)


# -------------------------------------------------------------------
# 事件：客户端连接
# -------------------------------------------------------------------
@sio.event
def connect(sid, environ):
    """
    客户端发起 WebSocket 连接时触发。
    :param sid: Socket.IO 为本次连接生成的唯一会话 ID。
    :param environ: WSGI 环境字典，包含 URL 参数等。
    """
    # 1. 从 URL 查询字符串中提取 token
    token = get_token_from_environ(environ)
    if not token:
        # 没有 token 直接拒绝连接，客户端会收到 "Missing token" 错误
        raise ConnectionRefusedError("Missing token")

    # 2. 验证 JWT 并提取 user_id
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]  # 从 payload 中取出用户 ID
    except Exception:
        # token 无效或过期，拒绝连接
        raise ConnectionRefusedError("Invalid token")

    # 3. 处理多地登录互踢逻辑（必须在设置新映射之前执行）
    old_sid = redis_client.get(f"user_sid:{user_id}")  # 查询该用户是否已有在线连接
    if old_sid and old_sid != sid:
        # 通过 Redis 判断旧 sid 是否仍有效（适用于多 Worker 环境）
        if redis_client.exists(f"sid_user:{old_sid}"):
            # 通知旧设备被踢下线
            sio.emit("server_kick", {"reason": "Login elsewhere"}, room=old_sid)
            # 主动断开旧连接，触发其 disconnect 事件进行清理
            sio.disconnect(old_sid)

    # 4. 建立双向映射（userId <-> sid）
    redis_client.set(f"user_sid:{user_id}", sid)  # 根据 user_id 找 sid
    redis_client.set(f"sid_user:{sid}", user_id)  # 根据 sid 找 user_id（反向映射）
    redis_client.sadd("online_users", user_id)  # 将用户 ID 加入在线集合

    # 5. 重连后自动恢复房间（若用户之前已加入过活动）
    activity_ids = redis_client.smembers(f"user_activities:{user_id}")
    for aid in activity_ids:
        # 将当前连接重新加入对应的 Socket.IO 房间
        sio.enter_room(sid, f"activity:{aid}")

    # 6. 推送离线期间收到的消息
    offline_key = f"offline_msg:{user_id}"
    while True:
        msg = redis_client.lpop(offline_key)  # 从左侧弹出最早的一条离线消息
        if not msg:
            break
        # msg 是 JSON 字符串，反序列化后发送给客户端
        sio.emit("server_offline_message", json.loads(msg), room=sid)

    # 7. 加载历史消息（从数据库）
    try:
        from models import ChatMessage, ChatRoom, UserActivity

        # 获取用户参与的所有活动
        user_activities = UserActivity.query.filter_by(user_id=int(user_id), status=1).all()

        for ua in user_activities:
            chat_room = ChatRoom.query.filter_by(activity_id=ua.activity_id).first()
            if chat_room:
                # 取最近50条消息
                history = ChatMessage.query.filter_by(room_id=chat_room.id) \
                    .order_by(ChatMessage.created_at.desc()) \
                    .limit(50).all()

                # 反转顺序（最旧的在前面）
                for msg in reversed(history):
                    sio.emit("server_new_message", {
                        "user_id": msg.user_id,
                        "activity_id": str(ua.activity_id),
                        "content": msg.content,
                        "timestamp": int(msg.created_at.timestamp())
                    }, room=sid)
    except Exception as e:
        print(f"加载历史消息失败: {e}")

    print(f"✅ User {user_id} connected ({sid})")


# -------------------------------------------------------------------
# 事件：客户端请求加入某个活动的房间
# -------------------------------------------------------------------
@sio.event
def client_join_activity(sid, data):
    """
    客户端发送 { activity_id: "xxx" } 请求加入对应房间。
    """
    # 1. 根据 sid 获取当前用户 ID
    user_id = redis_client.get(f"sid_user:{sid}")
    if not user_id:
        return  # 无效连接，忽略请求

    # 2. 从请求数据中取出 activity_id
    activity_id = data.get("activity_id")
    if not activity_id:
        return

    # 3. 将当前连接加入到对应的 Socket.IO 房间
    room_name = f"activity:{activity_id}"
    sio.enter_room(sid, room_name)

    # 4. 维护活动成员集合（用于离线消息分发）
    redis_client.sadd(f"activity_members:{activity_id}", user_id)  # 记录该活动的成员
    redis_client.sadd(f"user_activities:{user_id}", activity_id)  # 记录用户加入了哪些活动（反向索引）

    # 5. 告知客户端加入成功（只发送一次）
    sio.emit(
        "server_joined",
        {"activity_id": activity_id, "room": room_name},
        room=sid
    )


# -------------------------------------------------------------------
# 事件：客户端请求退出活动房间
# -------------------------------------------------------------------
@sio.event
def client_leave_activity(sid, data):
    """
    客户端发送 { activity_id: "xxx" } 请求退出房间。
    """
    user_id = redis_client.get(f"sid_user:{sid}")
    if not user_id:
        return
    activity_id = data.get("activity_id")
    if not activity_id:
        return

    room_name = f"activity:{activity_id}"
    sio.leave_room(sid, room_name)  # 离开 Socket.IO 房间

    # 清理成员关系
    redis_client.srem(f"activity_members:{activity_id}", user_id)
    redis_client.srem(f"user_activities:{user_id}", activity_id)

    # 通知客户端已退出
    sio.emit("server_left", {"activity_id": activity_id}, room=sid)


# -------------------------------------------------------------------
# 事件：客户端发送聊天消息
# -------------------------------------------------------------------
@sio.event
def client_send_message(sid, data):
    """
    客户端发送 { activity_id: "xxx", content: "hello" }，服务器广播给房间内所有人。
    """
    # 1. 获取发送者 user_id
    user_id = redis_client.get(f"sid_user:{sid}")
    if not user_id:
        return

    # 2. 提取消息内容
    activity_id = data.get("activity_id")
    content = data.get("content")
    if not activity_id or not content:
        return

    # 3. 权限校验：用户是否是该活动成员？
    if not redis_client.sismember(f"activity_members:{activity_id}", user_id):
        # 非成员不能发送消息，返回错误提示（仅发送给自己）
        sio.emit("server_error", {"reason": "Not a member of this activity"}, room=sid)
        return

    # 4. 构造要广播的消息体
    message_payload = {
        "user_id": int(user_id),  # 转成数字，前端才能正确判断"自己的消息"
        "activity_id": activity_id,
        "content": content,
        "timestamp": int(time.time())  # Unix 时间戳（秒）
    }

    # 5. 向房间内所有人广播消息（包括发送者自己）
    room_name = f"activity:{activity_id}"
    sio.emit("server_new_message", message_payload, room=room_name)

    # 6. 保存消息到数据库（永久存储）
    try:
        from models import ChatMessage, ChatRoom, db

        # 查找或创建聊天室
        chat_room = ChatRoom.query.filter_by(activity_id=int(activity_id)).first()
        if not chat_room:
            chat_room = ChatRoom(activity_id=int(activity_id))
            db.session.add(chat_room)
            db.session.flush()  # 先刷新获取 chat_room.id

        # 保存消息
        msg = ChatMessage(
            room_id=chat_room.id,
            user_id=int(user_id),
            content=content,
            msg_type=1  # 1=文本消息
        )
        db.session.add(msg)
        db.session.commit()
        print(f"💾 消息已保存到数据库: user={user_id}, activity={activity_id}")
    except Exception as e:
        print(f"保存消息失败: {e}")
        # 保存失败不影响消息发送

    # 7. 离线消息存储：遍历该活动的所有成员，若成员不在线，则存入离线队列
    members = redis_client.smembers(f"activity_members:{activity_id}")
    for uid in members:
        # 检查用户是否在线（通过 user_sid 键是否存在判断）
        if not redis_client.exists(f"user_sid:{uid}"):
            save_offline_message(uid, message_payload)


# -------------------------------------------------------------------
# 事件：客户端断开连接（主动关闭或网络异常）
# -------------------------------------------------------------------
@sio.event
def disconnect(sid):
    """
    连接断开时清理 Redis 中的映射和在线状态。
    """
    # 1. 根据 sid 获取 user_id（使用反向映射键）
    user_id = redis_client.get(f"sid_user:{sid}")
    if not user_id:
        print(f"⚠️ Orphaned connection disconnected: {sid}")
        return  # 可能是未授权连接被拒绝，无需清理

    # 2. 清理用户加入的所有活动成员关系（防止内存泄漏）
    activity_ids = redis_client.smembers(f"user_activities:{user_id}")
    for aid in activity_ids:
        redis_client.srem(f"activity_members:{aid}", user_id)
    # 删除反向索引集合本身（只需一次）
    redis_client.delete(f"user_activities:{user_id}")

    # 3. 删除双向映射
    redis_client.delete(f"user_sid:{user_id}")  # 删除 userId -> sid 映射
    redis_client.delete(f"sid_user:{sid}")  # 删除 sid -> userId 映射

    # 4. 从在线集合中移除
    redis_client.srem("online_users", user_id)

    print(f"❌ User {user_id} disconnected ({sid})")