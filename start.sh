#!/bin/bash
set -e

# اگر Railway پورت رو با env داد، از همون استفاده کن، وگرنه 8000
export PORT="${PORT:-8000}"

echo "Using port: $PORT"

# تولید کانفیگ اولیه Xray
python -c "from app.xray_manager import generate_config; generate_config()"

# اجرای Supervisor با متغیرهای محیطی
exec /usr/local/bin/supervisord -c /app/supervisord.conf
