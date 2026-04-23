from app import app
from models import db, User, Activity, UserActivity
from utils import hash_password
from datetime import datetime

with app.app_context():
    # 1. 创建测试用户（如果不存在）
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
        db.session.commit()
        print("✅ 测试用户创建成功")
    else:
        print("ℹ️ 测试用户已存在，ID:", test_user.id)

    # 2. 创建一个示例活动（如果不存在）
    demo_activity = Activity.query.filter_by(title="周末校园跑步活动").first()
    if not demo_activity:
        demo_activity = Activity(
            creator_id=test_user.id,
            title="周末校园跑步活动",
            description="一起在操场跑步，5公里慢跑",
            category="sports",
            tags=["跑步", "健康"],
            start_time=datetime(2026, 5, 10, 8, 0, 0),
            end_time=datetime(2026, 5, 10, 10, 0, 0),
            location_name="学校操场",
            max_participants=10,
            current_participants=1,
            status=1
        )
        db.session.add(demo_activity)
        db.session.commit()
        print("✅ 示例活动创建成功，ID:", demo_activity.id)

        # 创建者自动加入活动
        creator_join = UserActivity(
            user_id=test_user.id,
            activity_id=demo_activity.id,
            role=3,
            status=1
        )
        db.session.add(creator_join)
        db.session.commit()
        print("✅ 创建者已加入活动")
    else:
        print("ℹ️ 示例活动已存在，ID:", demo_activity.id)

print("\n🎉 测试数据准备完成！")
print("用户名：test_user")
print("密码：123456")