import json, base64, urllib.parse
from app.models import Inbound, User
import qrcode
from io import BytesIO
import yaml

def generate_config_link(inbound: Inbound, user: User) -> str:
    protocol = inbound.protocol
    domain = inbound.domain
    port = inbound.external_port
    path = inbound.path
    net = inbound.network
    sec = "tls"      # Railway handles TLS

    if protocol == "vless":
        query = urllib.parse.urlencode({
            "path": path,
            "security": sec,
            "encryption": "none",
            "type": net,
            "host": domain
        })
        return f"vless://{user.uuid}@{domain}:{port}?{query}#{urllib.parse.quote(user.email)}"

    elif protocol == "vmess":
        vmess_dict = {
            "v": "2",
            "ps": user.email,
            "add": domain,
            "port": str(port),
            "id": user.uuid,
            "aid": "0",
            "net": net,
            "type": "none",
            "host": "",
            "path": path,
            "tls": "tls"
        }
        return "vmess://" + base64.b64encode(json.dumps(vmess_dict, sort_keys=True).encode()).decode()

    elif protocol == "trojan":
        query = urllib.parse.urlencode({
            "security": sec,
            "type": net,
            "path": path,
            "host": domain
        })
        return f"trojan://{user.uuid}@{domain}:{port}?{query}#{urllib.parse.quote(user.email)}"
    return ""

def generate_qr_code_base64(data: str) -> str:
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# For Clash subscription
def generate_clash_config(user: User, inbound: Inbound) -> dict:
    proxy_name = f"{user.email}-{inbound.tag}"
    proxy = {
        "name": proxy_name,
        "type": inbound.protocol,
        "server": inbound.domain,
        "port": inbound.external_port,
        "uuid": user.uuid,
        "network": inbound.network,
        "tls": True,
        "servername": inbound.domain,
    }
    if inbound.network == "ws":
        proxy["ws-opts"] = {"path": inbound.path}
    if inbound.protocol == "vmess":
        proxy["alterId"] = 0
        proxy["cipher"] = "auto"
    return {"proxies": [proxy]}
