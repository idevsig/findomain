# Findomain Server

接收查询进度的服务器，用于断点续查

## 运行
```bash
python server.py

# 指定端口
python server.py -p 8000

# 后台运行
nohup python server.py -p 8000 &

# 结束后台
ps aux | grep server.py
kill -9 <PID>
```

```
Findomain Server for Resume Query
Listening on http://0.0.0.0:8000
Press Ctrl+C to stop
```

## 数据格式
```json
{
  "last_query_domain": "",
  "updated_time": ""
}
```

将上述 URL `http://0.0.0.0:8000` 填入配置文件中的 ``domain.resume_url`` 即可。
