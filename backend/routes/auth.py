# 注册、登录、个人资料接口
# 注册、登录、个人资料接口

from flask import Blueprint, request, jsonify, g
from datetime import datetime
from models import db, User, Activity, UserActivity
from utils import generate_anonymous_nickname, hash_password, verify_password
from auth import login_required, create_token

# 创建蓝图，URL 前缀将在 app.py 中注册时添加（例如 /api/auth）
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    请求体 JSON:
    {
        "username": "用户名",
        "password": "密码",
        "phone": "手机号",      # 可选
        "nickname": "昵称",    # 可选，若不传则自动生成
        "interests": ["跑步", "摄影"]  # 可选
    }
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码为必填项'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    # 检查手机号是否已存在（如果提供了）
    if data.get('phone') and User.query.filter_by(phone=data['phone']).first():
        return jsonify({'code': 400, 'message': '手机号已注册'}), 400

    # 使用前端传入的昵称，若未提供则自动生成匿名昵称
    nickname = data.get('nickname')
    if not nickname:
        nickname = generate_anonymous_nickname()

    user = User(
        username=data['username'],
        nickname=nickname,
        phone=data.get('phone'),
        password_hash=hash_password(data['password']),
        interests=data.get('interests', []),
        is_anonymous=0,
        last_login_at=datetime.now()
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id)
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {
            'user': user.to_dict(),
            'token': token
        }
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录（支持用户名或手机号）
    请求体 JSON:
    {
        "username": "用户名或手机号",
        "password": "密码"
    }
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码为必填项'}), 400

    username = data['username']
    user = User.query.filter(
        (User.username == username) | (User.phone == username)
    ).first()

    if not user or not verify_password(data['password'], user.password_hash):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401

    user.last_login_at = datetime.now()
    db.session.commit()

    token = create_token(user.id)
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user.to_dict(),
            'token': token
        }
    })


@auth_bp.route('/anonymous-login', methods=['POST'])
def anonymous_login():
    """
    匿名登录（无需参数，自动生成匿名用户）
    """
    anonymous_username = f"anon_{datetime.now().timestamp()}"
    nickname = generate_anonymous_nickname()

    user = User(
        username=anonymous_username,
        nickname=nickname,
        password_hash=hash_password('anonymous'),
        is_anonymous=1,
        last_login_at=datetime.now()
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id)
    return jsonify({
        'code': 200,
        'message': '匿名登录成功',
        'data': {
            'user': user.to_public_dict(),
            'token': token
        }
    })


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    获取个人中心信息（需登录）
    返回用户信息和统计数据
    """
    user = g.current_user

    # 获取用户参与的活动数量（status=1 表示已加入）
    participated_count = UserActivity.query.filter_by(
        user_id=user.id, status=1
    ).count()

    # 获取用户创建的活动数量
    created_count = Activity.query.filter_by(creator_id=user.id).count()

    return jsonify({
        'code': 200,
        'data': {
            'user': user.to_dict(),
            'stats': {
                'participated_count': participated_count,
                'created_count': created_count,
                'credit_score': user.credit_score
            }
        }
    })


@auth_bp.route('/update-interests', methods=['PUT'])
@login_required
def update_interests():
    """
    更新用户兴趣标签
    请求体 JSON:
    {
        "interests": ["跑步", "摄影", "读书"]
    }
    """
    data = request.get_json()
    interests = data.get('interests', [])
    user = g.current_user
    user.interests = interests
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {'interests': user.interests}
    })


# ============= 用户活动列表接口 =============

@auth_bp.route('/user/activities', methods=['GET'])
@login_required
def get_user_activities():
    """
    获取当前用户参与的活动列表（我参与的）
    返回：活动列表，按加入时间倒序
    """
    user = g.current_user
    # 查询用户参与的活动记录（status=1 表示已加入）
    participations = UserActivity.query.filter_by(
        user_id=user.id,
        status=1
    ).order_by(UserActivity.joined_at.desc()).all()

    activities = []
    for p in participations:
        activity = p.activity
        if activity:
            act_dict = activity.to_dict()
            # 添加额外信息：角色、加入时间等
            act_dict['role'] = p.role  # 1-参与者 2-管理员 3-创建者
            act_dict['joined_at'] = p.joined_at.isoformat() if p.joined_at else None
            activities.append(act_dict)

    return jsonify({
        'code': 200,
        'data': activities
    })


@auth_bp.route('/user/created-activities', methods=['GET'])
@login_required
def get_user_created_activities():
    """
    获取当前用户创建的活动列表（我发布的）
    返回：活动列表，按创建时间倒序
    """
    user = g.current_user
    activities = Activity.query.filter_by(
        creator_id=user.id
    ).order_by(Activity.created_at.desc()).all()

    result = [act.to_dict() for act in activities]
    return jsonify({
        'code': 200,
        'data': result
    })