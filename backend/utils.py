# 工具函数
import random  # 随机数生成，用于匿名昵称
import hashlib  # 哈希算法，用于密码加密
import jwt  # JWT令牌，用于用户认证
from datetime import datetime, timedelta  # 时间处理
from flask import current_app  # 获取当前应用配置
from math import radians, sin, cos, sqrt, asin  # 数学函数，用于距离计算
from models import Activity, UserActivity, ActivityFeed, User

def generate_anonymous_nickname():
    """
    生成匿名昵称
    规则：形容词 + 名词 + 4位随机数字
    例如：快乐的熊猫1234
    """
    # 形容词词库
    adjectives = ['快乐的', '安静的', '奔跑的', '仰望的', '跳跃的',
                  '思考的', '可爱的', '帅气的', '酷酷的', '温柔的']

    # 名词词库
    nouns = ['熊猫', '考拉', '袋鼠', '企鹅', '松鼠', '猫咪',
             '狗狗', '兔子', '狐狸', '小鹿', '海豚', '鲸鱼']

    # 随机选择一个形容词和一个名词
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    # 生成4位随机数字
    number = random.randint(1000, 9999)

    # 组合成昵称
    return f"{adj}{noun}{number}"


def hash_password(password):
    """
    密码哈希
    使用SHA-256算法对密码进行加密
    参数：原始密码
    返回：哈希后的密码字符串
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """
    验证密码
    参数：原始密码，存储的哈希值
    返回：True表示密码正确，False表示错误
    """
    return hash_password(password) == password_hash

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    计算两个经纬度点之间的距离（米）
    使用半正矢公式(Haversine)，考虑地球曲率
    参数：纬度1，经度1，纬度2，经度2
    返回：距离（米）
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # 半正矢公式
    dlon = lon2 - lon1  # 经度差
    dlat = lat2 - lat1  # 纬度差

    # 计算公式的中间值
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # 地球平均半径，单位为米
    r = 6371000

    # 返回距离（米）
    return c * r


def recommend_activities(user_id, user_interests=None, limit=10):
    """
    推荐算法核心实现
    基于用户兴趣标签 + 历史活动参与情况
    参数：用户ID，用户兴趣标签，推荐数量
    返回：推荐的活动列表
    """
    from models import Activity, UserActivity, db

    # 1. 获取用户兴趣标签（如果没有传入，从数据库查）
    if not user_interests:
        user = User.query.get(user_id)
        user_interests = user.interests if user and user.interests else []

    # 2. 获取用户历史参与的活动ID（排除这些，不重复推荐）
    participated_ids = db.session.query(UserActivity.activity_id).filter_by(
        user_id=user_id, status=1
    ).all()
    participated_ids = [p[0] for p in participated_ids]

    # 3. 构建查询：推荐进行中/报名中的活动
    query = Activity.query.filter(
        Activity.status.in_([0, 1]),  # 筹备中或报名中
        Activity.id.notin_(participated_ids) if participated_ids else True
    )

    # 4. 如果有兴趣标签，优先匹配标签
    if user_interests:
        # 获取一批活动用于评分
        activities = query.order_by(Activity.created_at.desc()).limit(limit * 2).all()

        # 计算每个活动的匹配度分数
        scored_activities = []
        for activity in activities:
            score = 0

            # 标签匹配加分：每匹配一个标签加10分
            if activity.tags and user_interests:
                common_tags = set(activity.tags) & set(user_interests)
                score += len(common_tags) * 10

            # 近期创建的活动加分：7天内创建的活动加5分
            days_old = (datetime.now() - activity.created_at).days
            if days_old < 7:
                score += 5

            # 热门活动加分：参与人数超过10人加3分
            if activity.current_participants > 10:
                score += 3

            scored_activities.append((activity, score))

        # 按分数排序，取前limit个
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        return [a[0] for a in scored_activities[:limit]]
    else:
        # 没有兴趣标签，返回最新创建的活动
        return query.order_by(Activity.created_at.desc()).limit(limit).all()

