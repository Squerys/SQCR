import sys
import os
import socket
import struct
import time
import threading
import json
import uuid
import traceback

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, 'generated_protos')
sys.path.append(proto_dir)

try:
    import generated_protos.PlatformCommands_pb2 as PC
    import generated_protos.ClientServerProtocol_pb2 as CSP
    import generated_protos.Gameplay_pb2 as GP
    import generated_protos.BackendMessage_pb2 as BM
    import generated_protos.Scene_pb2 
    import generated_protos.LogicScene_pb2
    import generated_protos.Weather_pb2
    print("[INIT] Modules Protobuf chargés.")
except ImportError as e:
    print(f"[FATAL] Erreur Import: {e}")
    sys.exit(1)

# ================= CONFIGURATION =================
BIND_IP = "0.0.0.0"
PORT = 9000
QUERY_PORT = 9001

SERVER_CONFIG = {
    "server_name": "[SQCR] TEST",
    "track_id": "spa",           
    "track_name": "Circuit de Spa-Francorchamps", 
    "track_layout": "gp",        
    "cars": ["ks_porsche_992_gt3_cup"],
    "max_players": 24,
    "session_type": "Practice",
    "uuid": str(uuid.uuid4())
}
# =================================================

def make_kunos_packet(msg_name, proto_object):
    payload = proto_object.SerializeToString()
    name_bytes = msg_name.encode('utf-8')
    total_len = 2 + 1 + len(name_bytes) + len(payload)
    header = struct.pack('<H', total_len)
    msg_id = struct.pack('<H', 0)
    return header + msg_id + bytes([len(name_bytes)]) + name_bytes + payload

def get_map_entry(container, key_val):
    if hasattr(container, "get_or_create"):
        return container.get_or_create(key_val)
    try:
        return container[key_val]
    except:
        for item in container:
            if getattr(item, 'key', None) == key_val:
                return item.value
        new_item = container.add()
        new_item.key = key_val
        return getattr(new_item, 'value', new_item)

# --- GÉNÉRATEUR HANDSHAKE COMPLET ---

def build_handshake():
    print(f"[GEN] Construction Handshake...")
    resp = PC.ConnectToServerHandshakeResponse()
    
    # 1. RACINE
    resp.handshake_result = 1
    resp.connection_id = 1001
    resp.server_version = 2
    resp.protocol_version = 4

    # 2. REQUEST DATA (Le miroir)
    # Le serveur confirme les infos de connexion du client
    req_data = resp.request_data
    req_data.password_type = 1 # Driver
    req_data.protocol_version = 4
    req_data.server_version = 2
    # On peut laisser 'local_physics_cars' vide pour l'instant

    # 3. SAISON
    season = resp.gamemode_changed_event.season
    if hasattr(season, "name"): season.name = SERVER_CONFIG["server_name"]
    
    # Métadonnées Saison (Manquantes dans v15)
    season.season_type = 1 # MultiPlayer
    season.gamemode_type = 1 # Race Weekend
    season.no_leaderboard = True
    season.season_guid.a = 123456789
    season.season_guid.b = 987654321

    # 4. EVENTS & SESSION
    event_entry = get_map_entry(season.event_map, 0)
    event_entry.name = "Race Weekend"
    
    session_entry = get_map_entry(event_entry.session_map, 0)
    session_entry.name = SERVER_CONFIG["session_type"]
    session_entry.description = "SQCR Lobby"
    
    # 5. SCÈNE (CIRCUIT)
    scene_config = session_entry.scene
    tcd = scene_config.track_content_data
    
    t_id = SERVER_CONFIG["track_id"]
    layout = SERVER_CONFIG["track_layout"]
    base_path = f"content\\tracks\\{t_id}"
    
    tcd.name = SERVER_CONFIG["track_name"]
    tcd.folder_path = base_path
    # Attention : Nom de fichier spécifique pour Spa
    scene_file = "spa_francorchamps" if t_id == "spa" else t_id
    tcd.file_path = f"{base_path}\\{scene_file}.scene"
    tcd.track_data_path = f"{base_path}\\dynamic_track\\{t_id}.track"
    
    tcd.nation = "BE"
    tcd.continent = "Europe"
    tcd.timezone = 1
    tcd.is_release = True
    tcd.coordinates.longitude = 5.971
    tcd.coordinates.latitude = 50.345

    # Conteneurs (Vitals)
    containers = [
        "camera_sequence_practice.scene",
        "layout_gp.scene",
        "marshalls_dlp.scene",
        "pitlane_race.scene",
        "pitlane_zones_gp.scene",
        "spawnpoints_pitlane.scene",
        "timelines.scene",
        "tv1_cameras.scene",
        "tv2_cameras.scene",
        "vr_cameras.scene"
    ]
    container_paths = [f"{base_path}\\containers\\{c}" for c in containers]
    
    if hasattr(scene_config, "containers"):
        del scene_config.containers[:]
        scene_config.containers.extend(container_paths)
    elif hasattr(scene_config, "container_scenes"):
        del scene_config.container_scenes[:]
        scene_config.container_scenes.extend(container_paths)

    # 6. LISTE DES VOITURES (CRITIQUE)
    # 'event_mutable_data' est une Map<int, EventMutableData>
    # ID 101 dans SeasonDefinition
    mutable_entry = get_map_entry(season.event_mutable_data, 0)
    
    # Ajout de voitures fictives pour que le client voie des slots
    try:
        # On ajoute 10 slots
        for i in range(1, 11):
            # 'cars' est un champ repeated de type Car (ID 1 dans EventMutableData)
            # Mais attention : c'est peut-être une Map selon ton proto généré.
            # On utilise une logique hybride :
            
            if hasattr(mutable_entry.cars, "add"): # Liste Repeated
                car = mutable_entry.cars.add()
            elif hasattr(mutable_entry.cars, "get_or_create"): # Map
                car = mutable_entry.cars.get_or_create(i)
            else:
                # Si c'est un champ simple (peu probable), on skip
                continue

            car.preferred_car_number = i
            car.pit_box_number = i
            # car.registration_key = "7656..." (Optionnel, pour réserver un slot)
            
    except Exception as e:
        print(f"[WARN] Erreur remplissage voitures : {e}")

    # 7. INITIAL SESSION DATA
    # ID 7 dans GamemodeChangedEvent
    # Doit être présent même vide pour valider la structure
    init_data = resp.gamemode_changed_event.initial_session_data
    # init_data.gamemode_session_data (Any, optionnel)

    # 8. MÉTÉO
    try:
        weather = session_entry.scene.weather
        weather.initial_date_time.hour = 12
        weather.static_data.static_weather.ambient_temperature_c = 24.0
    except: pass

    # 9. PHYSIQUE (Au bon endroit)
    resp.gamemode_changed_event.is_physics_pausable = False
    resp.gamemode_changed_event.physics_loaded = True 

    return make_kunos_packet("ConnectToServerHandshakeResponse", resp)

def build_udp_auth():
    resp = CSP.AssociateUDPSocketResponse()
    resp.success = True
    resp.connectionId = 1001
    return make_kunos_packet("AssociateUDPSocketResponse", resp)

def build_car_spawn():
    resp = CSP.ChangePlayerCarResponseEvent()
    resp.car_id.a = 123
    resp.car_id.b = 456
    
    if hasattr(resp, "car_model"):
        resp.car_model = SERVER_CONFIG["cars"][0]
    
    resp.car_number = 1
    resp.spawn_transform.position.y = 2.0 
    resp.spawn_transform.rotation.w = 1.0
    
    print(f"[GEN] Spawn Car OK")
    return make_kunos_packet("ChangePlayerCarResponseEvent", resp)

# --- SERVEURS ---

def query_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BIND_IP, QUERY_PORT))
    print(f"🟡 [QUERY] Ready on {QUERY_PORT}")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data == b"SQCR_QUERY":
                info = {
                    "name": SERVER_CONFIG["server_name"],
                    "track": SERVER_CONFIG["track_id"],
                    "cars": SERVER_CONFIG["cars"],
                    "port": PORT,
                    "uuid": SERVER_CONFIG["uuid"],
                    "max_players": SERVER_CONFIG["max_players"],
                    "session_type": SERVER_CONFIG["session_type"]
                }
                sock.sendto(json.dumps(info).encode('utf-8'), addr)
        except: pass

def udp_game_logic():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BIND_IP, PORT))
    print(f"🟢 [UDP] Ping Ready on {PORT}")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if len(data) > 0 and data[0] == 0x05:
                sock.sendto(b'\x06' + data[1:], addr)
        except: pass

def tcp_client_handler(client, addr):
    print(f"🔥🔥 [TCP] Connexion : {addr}")
    try:
        while True:
            header = client.recv(2)
            if not header: break
            size = struct.unpack('<H', header)[0]
            body = client.recv(size)
            
            name_len = body[2]
            msg_name = body[3 : 3+name_len].decode('utf-8', errors='ignore')
            print(f">> RECV: {msg_name}")
            
            if msg_name == "ClientConnectionRequest":
                client.sendall(build_handshake())
                print("<< SEND: Handshake")
                time.sleep(0.1) 
                client.sendall(build_udp_auth())
                print("<< SEND: UDP Auth")

            elif msg_name == "RequestPlayerCar":
                client.sendall(build_car_spawn())
                print("<< SEND: Car Spawn")

    except Exception as e:
        print(f"   Session terminée : {e}")
        traceback.print_exc()
    finally:
        client.close()

def start_server():
    threading.Thread(target=query_server, daemon=True).start()
    threading.Thread(target=udp_game_logic, daemon=True).start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BIND_IP, PORT))
    sock.listen(5)
    print(f"🔵 [TCP] Game Host Ready on {PORT}")
    while True:
        client, addr = sock.accept()
        threading.Thread(target=tcp_client_handler, args=(client, addr)).start()

if __name__ == "__main__":
    print("--- SQCR GAME SERVER v16 (COMPLETE) ---")
    start_server()
