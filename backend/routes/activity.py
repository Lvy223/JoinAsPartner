# 活动相关的 HTTP 路由处理模块
# 提供活动加入、退出等 RESTful 接口，并与 WebSocket 状态联动

# routes/activity.py
# 活动相关的 HTTP 路由处理模块（完整版）

from flask import Blueprint, request, jsonify, g
from datetime import datetime
from models import db, Activity, UserActivity, ActivityFeed, UserReview, User
from utils import calculate_distance, recommend_activities
from auth import login_required
from redis_client import redis_client
from socketio_server import sio
from sqlalchemy import or_

activity_bp = Blueprint("activity", __name__)

# ============================================================
# 1. 发布活动
# ============================================================
@activity_bp.route("/activities", methods=["POST"])
@login_required
def create_activity():
    """
    创建新活动
    请求体 JSON:
    {
        "title": "活动标题",
        "description": "活动描述",
        "category": "运动",
        "tags": ["跑步", "户外"],
        "start_time": "2025-05-01 10:00:00",
        "end_time": "2025-05-01 18:00:00",
        "deadline": "2025-04-30 23:59:59",
        "location_name": "奥体中心",
        "address_detail": "北门集合",
        "longitude": 116.397128,
        "latitude": 39.916527,
        "max_participants": 20
    }
    """
    data = request.get_json()
    required_fields = ['title', 'start_time', 'end_time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'code': 400, 'message': f'{field}为必填项'}), 400

    # 时间字段转换
    try:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00')) if data.get('deadline') else None
    except Exception:
        return jsonify({'code': 400, 'message': '时间格式错误，请使用 ISO 格式'}), 400

    activity = Activity(
        creator_id=g.current_user.id,
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category'),
        tags=data.get('tags', []),
        start_time=start_time,
        end_time=end_time,
        deadline=deadline,
        location_name=data.get('location_name'),
        address_detail=data.get('address_detail'),
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        max_participants=data.get('max_participants', 0),
        current_participants=1,
        status=0  # 筹备中
    )
    db.session.add(activity)
    db.session.commit()

    # 创建者自动加入（角色为创建者）
    user_activity = UserActivity(
        user_id=g.current_user.id,
        activity_id=activity.id,
        role=3,  # 3=创建者
        status=1
    )
    db.session.add(user_activity)
    db.session.commit()

    # 清除相关缓存（支持通配符）
    for key in redis_client.scan_iter("activity_feed:*"):
        redis_client.delete(key)

    return jsonify({
        'code': 200,
        'message': '活动创建成功',
        'data': activity.to_dict()
    })

@activity_bp.route("/activities/<int:activity_id>", methods=["GET"])
def get_activity_detail(activity_id):
    """获取单个活动详情"""
    activity = Activity.query.get_or_404(activity_id)
    return jsonify({'code': 200, 'data': activity.to_dict()})

# ============================================================
# 2. 活动信息流（首页推荐列表）
# ============================================================
@activity_bp.route("/activities/feed", methods=["GET"])
def get_activity_feed():
    """
    获取活动信息流，支持分页、距离排序、分类筛选
    查询参数:
        page: 页码，默认1
        per_page: 每页数量，默认20
        lat: 用户纬度（用于距离计算）
        lng: 用户经度
        radius: 搜索半径（米），默认5000
        category: 活动分类筛选
        sort: 排序方式 time|distance|hot，默认 time
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 5000, type=int)
    category = request.args.get('category')
    sort = request.args.get('sort', 'time')

    # 基础查询：只显示筹备中(0)或报名中(1)的活动
    query = Activity.query.filter(Activity.status.in_([0, 1]))
    if category:
        query = query.filter_by(category=category)

    activities = query.order_by(Activity.created_at.desc()).all()

    # 使用列表存储 (activity对象, 字典) 的元组
    result_with_obj = []
    for act in activities:
        act_dict = act.to_dict()
        # 计算距离
        if lat and lng and act.latitude and act.longitude:
            distance = calculate_distance(lat, lng, float(act.latitude), float(act.longitude))
            act_dict['distance'] = round(distance, 2)
            act_dict['distance_km'] = round(distance / 1000, 2)
            if distance > radius:
                continue
        else:
            act_dict['distance'] = None

        creator = User.query.get(act.creator_id)
        act_dict['creator'] = creator.to_public_dict() if creator else None
        act_dict['participant_count'] = UserActivity.query.filter_by(activity_id=act.id, status=1).count()
        result_with_obj.append((act, act_dict))

    # 排序时使用原始 Activity 对象的 start_time
    if sort == 'distance' and lat and lng:
        result_with_obj.sort(key=lambda x: x[1]['distance'] if x[1]['distance'] is not None else float('inf'))
    elif sort == 'hot':
        result_with_obj.sort(key=lambda x: x[1]['participant_count'], reverse=True)
    else:
        # 使用 Activity.start_time（datetime 对象）排序
        result_with_obj.sort(key=lambda x: x[0].start_time, reverse=True)

    # 提取最终的字典列表
    result = [item[1] for item in result_with_obj]

    # 分页
    total = len(result)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = result[start:end]

    # 缓存（可选，可后续优化）
    return jsonify({
        'code': 200,
        'data': {
            'activities': paginated,
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': end < total
        }
    })

@activity_bp.route("/activities/search", methods=["GET"])
def search_activities():
    """
    根据关键词搜索活动
    查询参数:
        keyword: 搜索关键词（必填）
        page: 页码，默认1
        per_page: 每页数量，默认20
    """
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({'code': 400, 'message': '请输入搜索关键词'}), 400

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # 在标题、描述、标签（JSON数组）中模糊匹配
    search_pattern = f"%{keyword}%"
    query = Activity.query.filter(
        or_(
            Activity.title.ilike(search_pattern),
            Activity.description.ilike(search_pattern),
            # 如果数据库支持 JSON 搜索（MySQL 5.7+），可使用 JSON_CONTAINS / JSON_SEARCH
            # 这里简化为标签字符串包含判断（取决于实际存储方式）
            Activity.tags.cast(db.String).ilike(search_pattern)
        ),
        Activity.status.in_([0, 1])  # 只搜索筹备中或报名中的活动
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    activities = [act.to_dict() for act in pagination.items]

    return jsonify({
        'code': 200,
        'data': {
            'activities': activities,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }
    })


# ============================================================
# 3. 附近活动（LBS 专用接口）
# ============================================================
@activity_bp.route("/activities/nearby", methods=["GET"])
def get_nearby_activities():
    """
    获取附近的活动（基于经纬度）
    查询参数:
        lat: 纬度
        lng: 经度
        radius: 半径（米），默认3000
    """
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 3000, type=int)

    if not lat or not lng:
        return jsonify({'code': 400, 'message': '需要提供位置信息'}), 400

    activities = Activity.query.filter(
        Activity.status.in_([0, 1]),
        Activity.latitude.isnot(None),
        Activity.longitude.isnot(None)
    ).all()

    nearby = []
    for act in activities:
        distance = calculate_distance(lat, lng, float(act.latitude), float(act.longitude))
        if distance <= radius:
            act_dict = act.to_dict()
            act_dict['distance'] = round(distance, 2)
            act_dict['distance_km'] = round(distance / 1000, 2)
            nearby.append(act_dict)

    nearby.sort(key=lambda x: x['distance'])
    return jsonify({
        'code': 200,
        'data': {
            'activities': nearby,
            'total': len(nearby),
            'center': {'lat': lat, 'lng': lng},
            'radius': radius
        }
    })


# ============================================================
# 4. 个性化活动推荐
# ============================================================
@activity_bp.route("/recommendations/activities", methods=["GET"])
@login_required
def get_recommendations():
    """
    基于用户兴趣标签和历史的个性化推荐
    查询参数: limit (默认10)
    """
    limit = request.args.get('limit', 10, type=int)
    user = g.current_user
    recommendations = recommend_activities(user.id, user.interests, limit)

    result = []
    for act in recommendations:
        act_dict = act.to_dict()
        # 匹配度评分（简单展示）
        if user.interests and act.tags:
            common = set(act.tags) & set(user.interests)
            act_dict['match_score'] = len(common) * 20  # 0-100
        else:
            act_dict['match_score'] = 50
        result.append(act_dict)

    return jsonify({
        'code': 200,
        'data': {
            'recommendations': result,
            'based_on': {
                'interests': user.interests,
                'history_count': UserActivity.query.filter_by(user_id=user.id, status=1).count()
            }
        }
    })


# ============================================================
# 5. 加入活动（原已存在，补全数据库操作）
# ============================================================
@activity_bp.route("/activities/<int:activity_id>/join", methods=["POST"])
@login_required
def join_activity(activity_id):
    """用户加入活动"""
    activity = Activity.query.get_or_404(activity_id)

    # 校验活动状态
    if activity.status not in [0, 1]:
        return jsonify({'code': 400, 'message': '该活动已不可加入'}), 400

    # 检查是否已加入
    existing = UserActivity.query.filter_by(
        user_id=g.current_user.id,
        activity_id=activity_id
    ).first()
    if existing:
        if existing.status == 1:
            return jsonify({'code': 400, 'message': '您已加入该活动'}), 400
        else:
            # 重新加入
            existing.status = 1
            existing.joined_at = datetime.now()
            existing.cancelled_at = None
    else:
        new_ua = UserActivity(
            user_id=g.current_user.id,
            activity_id=activity_id,
            role=1,   # 参与者
            status=1
        )
        db.session.add(new_ua)

    # 更新当前人数
    activity.current_participants += 1
    db.session.commit()

    # 通知 WebSocket 加入房间（通过 Redis 触发，或直接调用 sio）
    sid = redis_client.get(f"user_sid:{g.current_user.id}")
    if sid:
        sio.enter_room(sid, f"activity:{activity_id}")
        redis_client.sadd(f"activity_members:{activity_id}", g.current_user.id)
        redis_client.sadd(f"user_activities:{g.current_user.id}", activity_id)

    return jsonify({'code': 200, 'message': '成功加入活动'})


# ============================================================
# 6. 取消活动（仅创建者）
# ============================================================
@activity_bp.route("/activities/<int:activity_id>/cancel", methods=["POST"])
@login_required
def cancel_activity(activity_id):
    """取消整个活动（创建者权限）"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有创建者可取消活动'}), 403

    activity.status = 4  # 已取消
    db.session.commit()

    # 通过 WebSocket 广播活动取消
    sio.emit("server_activity_cancel", {"activity_id": activity_id, "message": "活动已取消"},
             room=f"activity:{activity_id}")
    # 关闭房间
    sio.close_room(f"activity:{activity_id}")
    # 清理 Redis 中的成员数据
    members = redis_client.smembers(f"activity_members:{activity_id}")
    for uid in members:
        redis_client.srem(f"user_activities:{uid}", activity_id)
    redis_client.delete(f"activity_members:{activity_id}")

    return jsonify({'code': 200, 'message': '活动已取消'})


# ============================================================
# 7. 关闭报名通道（开始活动）
# ============================================================
@activity_bp.route("/activities/<int:activity_id>/channel/close", methods=["POST"])
@login_required
def close_activity_channel(activity_id):
    """关闭报名通道，活动状态变为进行中（创建者权限）"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有创建者可关闭报名通道'}), 403

    activity.status = 2  # 进行中
    db.session.commit()
    return jsonify({'code': 200, 'message': '报名通道已关闭，活动开始'})


# ============================================================
# 8. 发布活动动态
# ============================================================
@activity_bp.route("/activities/<int:activity_id>/feeds", methods=["POST"])
@login_required
def create_feed(activity_id):
    """
    发布活动动态
    请求体 JSON:
    {
        "content": "今天天气真好",
        "images": ["url1", "url2"]
    }
    """
    activity = Activity.query.get_or_404(activity_id)
    # 检查用户是否参与了该活动（或是创建者）
    participation = UserActivity.query.filter_by(
        user_id=g.current_user.id,
        activity_id=activity_id,
        status=1
    ).first()
    if not participation and activity.creator_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有活动参与者可发布动态'}), 403

    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'code': 400, 'message': '动态内容不能为空'}), 400

    feed = ActivityFeed(
        activity_id=activity_id,
        user_id=g.current_user.id,
        content=data['content'],
        images=data.get('images', [])
    )
    db.session.add(feed)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '发布成功',
        'data': feed.to_dict()
    })


# ============================================================
# 9. 获取活动动态列表
# ============================================================
@activity_bp.route("/activities/<int:activity_id>/feeds", methods=["GET"])
def get_activity_feeds(activity_id):
    """获取活动的所有动态，支持分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    paginate = ActivityFeed.query.filter_by(activity_id=activity_id) \
        .order_by(ActivityFeed.is_pinned.desc(), ActivityFeed.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'feeds': [feed.to_dict() for feed in paginate.items],
            'total': paginate.total,
            'page': page,
            'per_page': per_page,
            'pages': paginate.pages
        }
    })

@activity_bp.route("/activities/<int:activity_id>/quit", methods=["POST"])
@login_required
def quit_activity(activity_id):
    """用户退出活动（参与者）"""
    user_activity = UserActivity.query.filter_by(
        user_id=g.current_user.id,
        activity_id=activity_id,
        status=1
    ).first()
    if not user_activity:
        return jsonify({'code': 400, 'message': '您尚未加入该活动'}), 400
    if user_activity.role == 3:
        return jsonify({'code': 400, 'message': '创建者不能退出，请解散活动'}), 400

    user_activity.status = 0
    user_activity.cancelled_at = datetime.now()
    activity = Activity.query.get(activity_id)
    activity.current_participants -= 1
    db.session.commit()

    # WebSocket 通知房间成员（可选）
    sio.emit("server_user_left", {"user_id": g.current_user.id, "activity_id": activity_id}, room=f"activity:{activity_id}")
    return jsonify({'code': 200, 'message': '已退出活动'})

@activity_bp.route("/activities/<int:activity_id>/complete", methods=["POST"])
@login_required
def complete_activity(activity_id):
    """活动完成（创建者或参与者标记活动结束）"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.creator_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有创建者可标记活动完成'}), 403
    if activity.status == 3:
        return jsonify({'code': 400, 'message': '活动已经结束'}), 400
    activity.status = 3
    db.session.commit()
    # 可额外处理评分等逻辑
    return jsonify({'code': 200, 'message': '活动已标记为完成'})


# ============================================================
# 10. 评价参与者（互评）
# ============================================================
@activity_bp.route("/review", methods=["POST"])
@login_required
def add_review():
    """
    活动结束后，用户评价其他参与者
    请求体 JSON:
    {
        "activity_id": 123,
        "reviewed_user_id": 456,
        "rating": 5,          # 1-5 分
        "comment": "很靠谱"
    }
    """
    data = request.get_json()
    activity_id = data.get('activity_id')
    reviewed_user_id = data.get('reviewed_user_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([activity_id, reviewed_user_id, rating]):
        return jsonify({'code': 400, 'message': '参数不完整'}), 400
    if rating < 1 or rating > 5:
        return jsonify({'code': 400, 'message': '评分必须为1-5'}), 400
    if g.current_user.id == reviewed_user_id:
        return jsonify({'code': 400, 'message': '不能评价自己'}), 400

    # 检查活动是否存在且已结束（status=3）
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    if activity.status != 3:
        return jsonify({'code': 400, 'message': '活动尚未结束，暂不能评价'}), 400

    # 检查双方是否都是该活动的参与者
    reviewer_participant = UserActivity.query.filter_by(
        user_id=g.current_user.id, activity_id=activity_id, status=1
    ).first()
    reviewed_participant = UserActivity.query.filter_by(
        user_id=reviewed_user_id, activity_id=activity_id, status=1
    ).first()
    if not reviewer_participant or not reviewed_participant:
        return jsonify({'code': 403, 'message': '只有活动参与者才能评价'}), 403

    # 检查是否已经评价过
    existing = UserReview.query.filter_by(
        activity_id=activity_id,
        reviewer_id=g.current_user.id,
        reviewed_user_id=reviewed_user_id
    ).first()
    if existing:
        return jsonify({'code': 400, 'message': '您已经评价过该用户了'}), 400

    # 创建评价记录
    review = UserReview(
        activity_id=activity_id,
        reviewer_id=g.current_user.id,
        reviewed_user_id=reviewed_user_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)

    # 更新被评价人的信用分（>=4 加2分，否则减5分，最低60）
    reviewed_user = User.query.get(reviewed_user_id)
    if rating >= 4:
        reviewed_user.credit_score += 2
    else:
        reviewed_user.credit_score -= 5
    if reviewed_user.credit_score < 60:
        reviewed_user.credit_score = 60

    db.session.commit()
    return jsonify({'code': 200, 'message': '评价成功'})