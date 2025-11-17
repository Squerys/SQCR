import asyncio
import websockets
import ssl
import uuid
import os

# ================= CONFIGURATION =================
PORT = 6990
CERT_FILE = "mitmproxy-ca.pem"
KEY_FILE = "mitmproxy-ca.pem"

# --- SERVER CONFIGURATION ---
MY_SERVER = {
    "name": "[SQCR] Open Source Server | Listing Test",
    "ip": "31.44.44.11", #Set to lfm for the test, but when server executable will be available, you can change that to the ip of the server you're connecting to
    "tcp": 9738, #same there
    "udp": 9738, #same there
    "track": "Imola",
    "cars": ["ks_mazda_mx5_nd_cup", "ks_ferrari_296_gtb"],
    "uuid": str(uuid.uuid4())
}

# --- PLAYER PROFILE CONFIGURATION ---
PLAYER = {
    "steam_id": "76561198000000000",
    "uuid": "10000000-0000-0000-0000-000000000001",
    "name": "SQCR",
    "surname": "User"
}
# =================================================

# --- PROTOBUF UTILS ---

def varint(value):
    """Encodes an integer as a Protobuf Varint."""
    out = []
    while value > 127:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)

def make_field(field_id, value, wire_type=None):
    """Creates a Protobuf field (Tag + Length + Value)."""
    if wire_type is None:
        if isinstance(value, (str, bytes)):
            wire_type = 2
        elif isinstance(value, int):
            wire_type = 0 
    
    # Proto3: Default values are not serialized
    if wire_type == 0 and value == 0:
        return b""
    if wire_type == 2 and len(value) == 0:
        return b""

    encoded_val = b""
    if wire_type == 2:
        if isinstance(value, str):
            value = value.encode('utf-8')
        encoded_val = varint(len(value)) + value
    elif wire_type == 0:
        encoded_val = varint(int(value))
    
    tag = (field_id << 3) | wire_type
    return varint(tag) + encoded_val

def wrap_packet(type_url, payload):
    """Wraps the message in a google.protobuf.Any container (ID 1=URL, ID 2=Data)."""
    any_obj = make_field(1, type_url) + make_field(2, payload)
    # The game expects the Any object to be wrapped in Field 1 of the outer message
    return make_field(1, any_obj)

# --- RESPONSE GENERATORS ---

def get_register_response():
    """Generates 'type.googleapis.com/RegisterResponse'."""
    # ID 2: is_registered = True
    # ID 3: platform_type = STEAM (1)
    payload = make_field(2, 1) + make_field(3, 1)
    return wrap_packet("type.googleapis.com/RegisterResponse", payload)

def get_account_response():
    """Generates 'type.googleapis.com/GameEconomyClientResponseAccount'."""
    # ID 4: PersonalData (1=Name, 2=Surname)
    pdata = make_field(1, PLAYER["name"]) + make_field(2, PLAYER["surname"])
    
    payload = b""
    payload += make_field(1, b"") # Response OK
    payload += make_field(2, "Steam_" + PLAYER["steam_id"])
    payload += make_field(4, pdata)
    payload += make_field(100, PLAYER["uuid"])
    
    return wrap_packet("type.googleapis.com/GameEconomyClientResponseAccount", payload)

def get_server_list_response():
    """Generates 'type.googleapis.com/MultiplayerServerListResponseServerList'."""
    srv = b""
    
    # --- Identity ---
    srv += make_field(1, MY_SERVER["name"])
    
    # ID 2: Must be formatted as "IP:PORT" (Critical fix)
    ip_combo = f"{MY_SERVER['ip']}:{MY_SERVER['tcp']}"
    srv += make_field(2, ip_combo)
    
    srv += make_field(3, MY_SERVER["tcp"])
    srv += make_field(4, MY_SERVER["udp"])
    srv += make_field(5, MY_SERVER["uuid"])
    
    # --- Configuration ---
    srv += make_field(8, 24)              # Max Players
    srv += make_field(10, 1)              # Mode
    srv += make_field(11, "SQCR Event")   # Event Name
    srv += make_field(12, "Qualifying")   # Session Name
    srv += make_field(13, MY_SERVER["track"])
    srv += make_field(14, "GP Race")      # Layout
    srv += make_field(15, "12:00:00")     # Time of Day
    
    # --- Filters ---
    srv += make_field(31, 1)              # Session Type
    for car in MY_SERVER["cars"]:
        srv += make_field(34, car)
        
    srv += make_field(35, 15)             # Ping
    
    # --- Advanced Params (from dump) ---
    srv += make_field(40, 1) # Weather
    srv += make_field(42, 2) # Grip
    srv += make_field(43, 1) # Duration Type
    srv += make_field(44, 900000) # Duration (ms)
    
    # --- Compatibility ---
    srv += make_field(51, 1) # Is Car Eligible = True
    
    # Protocol Versions (Static values known to work)
    srv += make_field(52, 4) 
    srv += make_field(53, 2)

    # Global Response Wrapper
    payload = make_field(1, b"") + make_field(2, srv)
    
    return wrap_packet("type.googleapis.com/MultiplayerServerListResponseServerList", payload)

# --- WEBSOCKET HANDLER ---

async def handler(websocket, path):
    print(f"[INFO] New client connected: {websocket.remote_address[0]}")
    
    try:
        async for message in websocket:
            # Ignore text handshake
            if isinstance(message, str): 
                continue

            if isinstance(message, bytes):
                if b"RegisterRequest" in message:
                    print("[RECV] RegisterRequest")
                    await websocket.send(get_register_response())
                    print("[SEND] RegisterResponse")
                
                elif b"GameEconomy" in message:
                    print("[RECV] AccountRequest")
                    await websocket.send(get_account_response())
                    print("[SEND] AccountResponse")

                elif b"ServerList" in message:
                    print("[RECV] ServerListRequest")
                    await websocket.send(get_server_list_response())
                    print(f"[SEND] ServerListResponse (Injected: {MY_SERVER['name']})")
                    
    except Exception as e:
        print(f"[ERROR] {e}")

async def main():
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        ssl_ctx.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    except Exception as e:
        print(f"[FATAL] SSL Error: {e}")
        print(f"Ensure '{CERT_FILE}' is present.")
        return

    print(f"SQCR Master Server Emulator")
    print(f"Listening on wss://0.0.0.0:{PORT}")
    print("-" * 30)
    
    async with websockets.serve(handler, "0.0.0.0", PORT, ssl=ssl_ctx):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
