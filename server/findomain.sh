#!/usr/bin/env bash

NAME="findomain_sh"

process_id() {
    pgrep -f "server.py -n $NAME"
}

# 启动服务
start() {
    PORT="${1:-8000}"     # 默认端口 8000

    # 检查是否已经在运行
    if pgrep -f "python3 server.py -n $NAME -p $PORT" > /dev/null; then
        PID=$(process_id)
        HOST=$(ss -lptn | grep "$PID" | awk '{print $4}')
        echo "⚠️ Server (PID: $PID) is already running on $HOST."
        return 0
    fi

    echo "Starting server ..."

    # 是否后台运行（可切换注释）
    # 后台运行 + 重定向日志
    nohup python3 server.py -n "$NAME" -p "$PORT" > /dev/null 2>&1 &

    sleep 3s
    
    PID=$(process_id)
    HOST=$(ss -lptn | grep "$PID" | awk '{print $4}')
    echo "Server (PID: $PID) is running on $HOST."
    # 前台运行（调试时用）
    # python3 server.py -p "$PORT" -n "$NAME"
}

# 停止服务
stop() {
    # 使用 pkill 精确匹配名称，避免误杀
    echo "Stopping processes named '$NAME'..."
    pkill -f "findomain_sh"

    # 可选：确认是否成功停止
    if pgrep -f "$NAME" > /dev/null; then
        echo "⚠️ Failed to stop all processes."
    else
        echo "✅ All '$NAME' processes stopped."
    fi
}

# 重启服务
restart() {
    stop
    start "$@"
}

# 状态检查
status() {
    echo "Checking running processes for '$NAME'..."
    PID=$(process_id)

    if [[ -z "$PID" ]]; then
        echo "❌ No process found."
        return 0
    fi

    HOST=$(ss -lptn | grep "$PID" | awk '{print $4}')
    echo "Server (PID: $PID) is running on $HOST."    
}

# 主逻辑分发
case "$1" in
    start) shift; start "$@" ;;
    stop) stop ;;
    restart) shift; restart "$@" ;;
    status) status ;;
    *)
        echo "Usage: $0 {start|stop|restart|status} [port]"
        exit 1
        ;;
esac
