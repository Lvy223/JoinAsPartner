import redis

# 1. 创建 Redis 连接
# host: Redis服务器的地址，因为是在本机运行，所以是 'localhost' 或 '127.0.0.1'
# port: Redis服务器的端口，默认是 6379，这和你截图里的一致
# db: 选择使用的数据库编号，默认是 0
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # 2. 测试连接
    # ping() 方法会向 Redis 服务器发送一个 PING 命令，如果连接成功，服务器会返回 PONG
    if r.ping():
        print("✅ 成功连接到 Redis 服务器！")

    # 3. 进行简单的读写操作
    # 设置一个键值对
    r.set('my_key', 'Hello from PyCharm!')
    print("已存入数据：my_key -> Hello from PyCharm!")

    # 获取这个键的值
    value = r.get('my_key')
    print(f"已获取数据：my_key -> {value}")

except redis.ConnectionError:
    print("❌ 无法连接到 Redis 服务器，请确保 redis-server.exe 正在运行。")