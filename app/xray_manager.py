import json, os, subprocess
from app.database import SessionLocal
from app.models import Inbound

XRAY_CONFIG_PATH = "/etc/xray/config.json"

def generate_config():
    db = SessionLocal()
    inbounds = db.query(Inbound).filter(Inbound.is_active == True).all()
    inbound_list = []
    for ib in inbounds:
        active_users = [u for u in ib.users if u.is_active]
        clients = []
        for u in active_users:
            client = {"id": u.uuid, "email": u.email}
            if ib.protocol == "vmess":
                client["alterId"] = 0
            clients.append(client)

        settings = {"clients": clients}
        if ib.protocol == "vmess":
            settings["decryption"] = "none"

        stream = {
            "network": ib.network,
            "security": ib.security
        }
        if ib.network == "ws":
            stream["wsSettings"] = {"path": ib.path}

        inbound_list.append({
            "tag": ib.tag,
            "port": ib.port,
            "listen": ib.listen,
            "protocol": ib.protocol,
            "settings": settings,
            "streamSettings": stream,
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}
        })

    config = {
        "log": {"loglevel": "warning"},
        "inbounds": inbound_list,
        "outbounds": [{"protocol": "freedom", "tag": "direct"}],
        "routing": {
            "domainStrategy": "AsIs",
            "rules": []
        }
    }
    if not inbound_list:
        config["inbounds"] = [{
            "tag": "noop",
            "port": 65535,
            "listen": "127.0.0.1",
            "protocol": "dokodemo-door",
            "settings": {"address": "127.0.0.1", "port": 1, "network": "tcp,udp"}
        }]

    db.close()
    os.makedirs(os.path.dirname(XRAY_CONFIG_PATH), exist_ok=True)
    with open(XRAY_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def reload_xray():
    generate_config()
    # restart xray via supervisor
    subprocess.run(["/usr/local/bin/supervisorctl", "restart", "xray"], check=False)
