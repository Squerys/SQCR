import asyncio
import websockets
import ssl
import socket
import json
import uuid

# ================= CONFIGURATION =================
PORT = 6990
CERT_FILE = "mitmproxy-ca.pem"
KEY_FILE = "mitmproxy-ca.pem"

# Target Game Server for UDP Query
GAME_SERVER_IP = "127.0.0.1"
GAME_QUERY_PORT = 9001

# Dummy Player Profile
PLAYER = {
    "steam_id": "76561198000000000",
    "uuid": "10000000-0000-0000-0000-000000000001",
    "name": "SQCR",
    "surname": "User"
}
# =================================================

# --- PROTOBUF UTILS ---
def varint(value):
    out = []
    while value > 127:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)

def make_field(field_id, value, wire_type=None):
    if wire_type is None:
        if isinstance(value, (str, bytes)): wire_type = 2
        elif isinstance(value, int): wire_type = 0
    
    if wire_type == 0 and value == 0: return b""
    if wire_type == 2 and len(value) == 0: return b""

    encoded_val = b""
    if wire_type == 2:
        if isinstance(value, str): value = value.encode('utf-8')
        encoded_val = varint(len(value)) + value
    elif wire_type == 0:
        encoded_val = varint(int(value))
    
    tag = (field_id << 3) | wire_type
    return varint(tag) + encoded_val

def wrap_packet(type_url, payload):
    any_obj = make_field(1, type_url) + make_field(2, payload)
    return make_field(1, any_obj)

# --- LOGIC ---

def fetch_server_info():
    """Queries the local Game Server via UDP to get live config."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.2) # Fast timeout
        sock.sendto(b"SQCR_QUERY", (GAME_SERVER_IP, GAME_QUERY_PORT))
        data, _ = sock.recvfrom(4096)
        return json.loads(data.decode('utf-8'))
    except:
        return None

def get_register_response():
    payload = make_field(2, 1) + make_field(3, 1)
    return wrap_packet("type.googleapis.com/RegisterResponse", payload)

def get_account_response():
    pdata = make_field(1, PLAYER["name"]) + make_field(2, PLAYER["surname"])
    payload = make_field(1, b"") + make_field(2, "Steam_" + PLAYER["steam_id"]) + \
              make_field(4, pdata) + make_field(100, PLAYER["uuid"])
    return wrap_packet("type.googleapis.com/GameEconomyClientResponseAccount", payload)

def get_server_list_response():
    # 1. Get info from Game Server
    info = fetch_server_info()
    
    if not info:
        print("[WARN] Game Server not responding. Sending empty list.")
        return wrap_packet("type.googleapis.com/MultiplayerServerListResponseServerList", make_field(1, b""))

    # 2. Build Entry based on live info
    srv = b""
    srv += make_field(1, info["name"])
    
    # Critical: IP:PORT string
    srv += make_field(2, f"{GAME_SERVER_IP}:{info['port']}")
    
    srv += make_field(3, info['port'])
    srv += make_field(4, info['port'])
    srv += make_field(5, info["uuid"])
    
    srv += make_field(8, 24)
    srv += make_field(10, 1)
    srv += make_field(11, "SQCR Session")
    srv += make_field(12, "Qualifying")
    srv += make_field(13, info["track"]) # Dynamic Track Name
    srv += make_field(14, "GP Race")
    srv += make_field(15, "12:00:00")
    
    srv += make_field(31, 1)
    for car in info["cars"]:
        srv += make_field(34, car)
        
    srv += make_field(35, 15)
    srv += make_field(40, 1)
    srv += make_field(51, 1)
    srv += make_field(52, 4)
    srv += make_field(53, 2)

    payload = make_field(1, b"") + make_field(2, srv)
    return wrap_packet("type.googleapis.com/MultiplayerServerListResponseServerList", payload)

# --- HANDLER ---

async def handler(websocket, path):
    print(f"[INFO] Client connected")
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                if b"RegisterRequest" in message:
                    await websocket.send(get_register_response())
                elif b"GameEconomy" in message:
                    await websocket.send(get_account_response())
                elif b"ServerList" in message:
                    print(">> Fetching Game Server Info...")
                    await websocket.send(get_server_list_response())
                    print("<< Sent Dynamic List")
                elif b"SelectServer" in message:
                    await websocket.send(wrap_packet("type.googleapis.com/MultiplayerServerListResponseSelectServer", b""))
                elif b"ConnectToServer" in message:
                    await websocket.send(wrap_packet("type.googleapis.com/MultiplayerServerListResponseConnectToServer", b""))
    except Exception: pass

async def main():
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        ssl_ctx.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    except:
        print("[FATAL] SSL Cert missing.")
        return

    print(f"SQCR Master Directory - Port {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT, ssl=ssl_ctx):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
