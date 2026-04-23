# 数据库模型
from flask_sqlalchemy import SQLAlchemy  # 导入数据库ORM
from datetime import datetime  # 时间处理

db = SQLAlchemy()  # 创建数据库实例


class User(db.Model):
    """用户模型 - 对应数据库中的users表"""
    __tablename__ = 'users'  # 指定表名

    # 主键字段
    id = db.Column(db.Integer, primary_key=True)  # 用户ID，自增主键

    # 账号信息
    username = db.Column(db.String(50), unique=True, nullable=False)  # 用户名，唯一，不能为空
    nickname = db.Column(db.String(50), nullable=False)  # 昵称，不能为空
    phone = db.Column(db.String(20), unique=True)  # 手机号，唯一
    password_hash = db.Column(db.String(255), nullable=False)  # 密码哈希值，不能为空

    # 个人资料
    avatar_url = db.Column(db.String(500))  # 头像地址
    gender = db.Column(db.SmallInteger, default=0)  # 性别：0-未知 1-男 2-女
    birthday = db.Column(db.Date)  # 出生日期
    interests = db.Column(db.JSON)  # 兴趣标签，JSON格式存储

    # 系统字段
    credit_score = db.Column(db.Integer, default=100)  # 信用分，默认100
    is_anonymous = db.Column(db.SmallInteger, default=0)  # 是否匿名：0-否 1-是
    last_login_at = db.Column(db.DateTime)  # 最后登录时间
    created_at = db.Column(db.DateTime, default=datetime.now)  # 注册时间，默认当前时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # 关系（用于关联查询）
    created_activities = db.relationship('Activity', backref='creator', lazy='dynamic')
    # ↑ 用户创建的活动，backref='creator'表示在Activity中可以用.creator访问用户

    activity_participations = db.relationship('UserActivity', backref='user', lazy='dynamic')

    # ↑ 用户参与的活动记录

    def to_dict(self):
        """转换为字典（用于API返回完整信息）"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'gender': self.gender,
            'interests': self.interests,
            'credit_score': self.credit_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_public_dict(self):
        """转换为字典（用于公开信息，如匿名展示）"""
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'credit_score': self.credit_score
        }


class Activity(db.Model):
    """活动模型 - 对应数据库中的activities表"""
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)  # 活动ID，自增主键

    # 基本信息
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # ↑ 创建者ID，外键关联users表

    title = db.Column(db.String(200), nullable=False)  # 活动标题，不能为空
    description = db.Column(db.Text)  # 活动描述
    category = db.Column(db.String(50))  # 活动分类
    tags = db.Column(db.JSON)  # 活动标签，JSON格式

    # 时间和地点
    start_time = db.Column(db.DateTime, nullable=False)  # 开始时间，不能为空
    end_time = db.Column(db.DateTime, nullable=False)  # 结束时间，不能为空
    deadline = db.Column(db.DateTime)  # 报名截止时间

    location_name = db.Column(db.String(255))  # 地点名称
    longitude = db.Column(db.DECIMAL(10, 7))  # 经度
    latitude = db.Column(db.DECIMAL(10, 7))  # 纬度
    address_detail = db.Column(db.String(500))  # 详细地址

    # 参与设置
    max_participants = db.Column(db.Integer, default=0)  # 最大参与人数，0表示不限
    current_participants = db.Column(db.Integer, default=0)  # 当前参与人数
    status = db.Column(db.SmallInteger, default=0)  # 状态：0-筹备中 1-报名中 2-进行中 3-已结束 4-已取消
    is_private = db.Column(db.SmallInteger, default=0)  # 是否私密：0-公开 1-私密

    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # 关系
    participants = db.relationship('UserActivity', backref='activity', lazy='dynamic')
    # ↑ 活动的参与者记录

    feeds = db.relationship('ActivityFeed', backref='activity', lazy='dynamic')

    # ↑ 活动的动态

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'tags': self.tags,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location_name': self.location_name,
            'address_detail': self.address_detail,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'status': self.status,
            'creator_id': self.creator_id,
            'creator_nickname': self.creator.nickname if self.creator else None
        }


class UserActivity(db.Model):
    """用户-活动关联模型 - 对应数据库中的user_activities表"""
    __tablename__ = 'user_activities'

    id = db.Column(db.Integer, primary_key=True)  # 记录ID，自增主键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户ID
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)  # 活动ID
    description = db.Column(db.Text)  # 描述
    category = db.Column(db.String(20))  # 分类：运动、学习等
    location = db.Column(db.String(100))  # 地点
    role = db.Column(db.SmallInteger, default=1)  # 角色：1-参与者 2-管理员 3-创建者
    status = db.Column(db.SmallInteger, default=1)  # 状态：0-已退出 1-已加入 2-待审核
    max_people = db.Column(db.Integer, default=2)  # 最大人数
    current_people = db.Column(db.Integer, default=1)  # 当前人数
    joined_at = db.Column(db.DateTime, default=datetime.now)  # 加入时间
    cancelled_at = db.Column(db.DateTime)  # 退出时间

    __table_args__ = (db.UniqueConstraint('user_id', 'activity_id'),)  # 联合唯一约束，防止重复加入


class ActivityFeed(db.Model):
    """活动动态模型 - 对应数据库中的activity_feeds表"""
    __tablename__ = 'activity_feeds'

    id = db.Column(db.Integer, primary_key=True)  # 动态ID
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)  # 活动ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 发布者ID
    content = db.Column(db.Text, nullable=False)  # 动态内容，不能为空
    images = db.Column(db.JSON)  # 图片地址数组，JSON格式
    like_count = db.Column(db.Integer, default=0)  # 点赞数
    comment_count = db.Column(db.Integer, default=0)  # 评论数
    is_pinned = db.Column(db.SmallInteger, default=0)  # 是否置顶：0-否 1-是
    created_at = db.Column(db.DateTime, default=datetime.now)  # 发布时间

    # 发布者信息（关系）
    author = db.relationship('User', foreign_keys=[user_id])

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'content': self.content,
            'images': self.images,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'created_at': self.created_at.isoformat(),
            'author': {
                'id': self.author.id,
                'nickname': self.author.nickname,
                'avatar_url': self.author.avatar_url
            }
        }

class ChatRoom(db.Model):
    """聊天室模型 - 对应 chat_room 表"""
    __tablename__ = 'chat_room'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    is_active = db.Column(db.SmallInteger, default=1, comment='1-活跃 0-已关闭')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    activity = db.relationship('Activity', backref='chat_room')
    messages = db.relationship('ChatMessage', backref='room', lazy='dynamic')

class ChatMessage(db.Model):
    """聊天消息模型 - 对应 chat_message 表"""
    __tablename__ = 'chat_message'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.SmallInteger, default=1, comment='1-文本 2-图片 3-系统通知')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    user = db.relationship('User', foreign_keys=[user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else None,
            'user_avatar': self.user.avatar_url if self.user else None,
            'content': self.content,
            'msg_type': self.msg_type,
            'created_at': self.created_at.isoformat()
        }

class UserReview(db.Model):
    """用户互评模型 - 对应 user_review 表"""
    __tablename__ = 'user_review'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, comment='1-5分')
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    activity = db.relationship('Activity', foreign_keys=[activity_id])
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewed_user = db.relationship('User', foreign_keys=[reviewed_user_id])

    __table_args__ = (db.UniqueConstraint('activity_id', 'reviewer_id', 'reviewed_user_id'),)

    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_nickname': self.reviewer.nickname if self.reviewer else None,
            'reviewed_user_id': self.reviewed_user_id,
            'reviewed_user_nickname': self.reviewed_user.nickname if self.reviewed_user else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

