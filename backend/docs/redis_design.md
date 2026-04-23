# Redis 缓存结构设计文档（完整版）
## 一、设计目标
1. 支撑 Socket.IO 多进程共享状态
2. 实现 用户在线状态、连接映射、房间管理
3. 支持 离线消息缓存
4. 为 推荐算法、活动信息流 提供高速缓存
5. 保证 高并发、低延迟、可扩展

## 二、Key 命名规范（强制统一）
+ 小写
+ 使用：分隔
+ 不使用空格、中文

## 三、核心 Redis Key 设计总表
### Redis 缓存设计

| Key | Type | 说明            | TTL |
|----|----|---------------|----|
| user_sid:{uid} | String | user_id → sid | 24h |
| sid_user:{sid} | String | sid → user_id | 24h |
| online_users | Set | 在线用户集合        | 永久 |
| activity_members:{aid} | Set | 活动成员          | 活动结束 |
| offline_msg:{uid} | List | 离线消息队列        | 7天 |
| activity:info:{aid} | Hash | 活动详情          | 5min |
| recommend:{uid} | List | 推荐活动ID        | 5min |

## 四、 Key 详细说明
1. 用户 ↔ Socket 映射（核心）
```
python
user:sid:{user_id} -> sid
sid:user:{sid} -> user_id
```
用途：
+ Socket.IO 连接鉴权
+ 多地登录互踢
+ 单点推送

2. 在线用户集合
```
python
online:users -> Set(user_id)
```
用途：
+ 快速统计在线人数
+ 多地登录互踢
3. 活动房间成员
```
python
activity:members:{activity_id} -> Set(user_id)
```
用途：
+ 判断活动是否满员
+ 广播消息
+ 踢人 / 解散房间
4. 活动信息缓存
```
python
activity:info:{activity_id} -> Hash
```
字段示例：
title、
creator_id、
current_count、
max_count、
status、
longitude、
latitude
（减少MySQL查询）
5. 离线消息队列
```
python
offline:msg:{user_id} -> List(JSON)
```
```
# 消息结构
{
  "from": "user_1",
  "content": "你好",
  "timestamp": 1713177600
}
```
用户上线后逐条弹出
6. 推荐结果缓存（算法）
```
recommend:{user_id} -> List(activity_id)
```
降低推荐算法计算频率、 提升首页加载速度
## 五、典型业务流程
+ 用户上线
```
connect
→ 校验 JWT
→ 写入 user:sid
→ 写入 sid:user
→ 加入 online:users
→ 推送 offline:msg
```
+ 发送消息
```
判断 receiver 是否 online
→ 是 → emit
→ 否 → push offline:msg
```
+ 活动满员
```
current_count == max_count
→ 遍历 activity:members
→ emit activity_full
```
## 六、过期策略
| Key           | 策略   |
|---------------|------|
| user:sid      | 24h  |
| sid:user      | 24h  |
| activity.info | 5min |
| offline:msg:  | 7天   |
| recommend     | 5min |
