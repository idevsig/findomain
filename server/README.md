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

可通过脚本 `findomain.sh` 快速执行。
```bash
./findomain.sh start
# 指定端口
./findomain.sh start 8000

./findomain.sh stop
./findomain.sh restart
./findomain.sh status
```

## 数据格式
```json
{
  "last_query_domain": "",
  "updated_time": ""
}
```

将上述 URL `http://0.0.0.0:8000` 填入配置文件中的 ``domain.resume_url`` 即可。

## 自动触发 GitHub Action

环境变量，`GITHUB_TOKEN` 为必填项。
```bash
GITHUB_TOKEN="" # 必填
FD_REPOSITORY="idev-sig/findomain" # 选填，仓库地址。
FD_REF="main" # 选填，默认分支。
FD_WORKFLOW="find-domain.yml" # 选填，工作流程文件名。
```
