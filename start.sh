#!/bin/bash
# تولید کانفیگ اولیه Xray قبل از شروع سرویس‌ها
python -c "from app.xray_manager import generate_config; generate_config()"
# شروع Supervisor
exec /usr/local/bin/supervisord -c /app/supervisord.conf
