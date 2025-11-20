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
    import generated_protos.PlatformGameState_pb2 as PGS
    import generated_protos.gamemodes.TimeAttackData_pb2 as TA 
    import generated_protos.gamemodes.InstantRaceData_pb2 as IR 
    print("[INIT] Protobuf modules loaded.")
except ImportError as e:
    print(f"[FATAL] Import Error: {e}")
    sys.exit(1)

# ================= CONFIGURATION =================
BIND_IP = "0.0.0.0"
PORT = 9000
QUERY_PORT = 9001
SERVER_CONFIG = {
    "server_name": "[SQCR] Test listing",
    "track_id": "spa", "track_name": "Circuit de Spa-Francorchamps",
    "cars": ["ks_porsche_992_gt3_cup"],
    "uuid": str(uuid.uuid4()), "max_players": 24, "session_type": "Practice"
}

# --- RESEAU ---
def make_kunos_packet(msg_name, proto_object_or_bytes):
    if isinstance(proto_object_or_bytes, bytes): payload = proto_object_or_bytes
    else: payload = proto_object_or_bytes.SerializeToString()
    name_bytes = msg_name.encode('utf-8')
    total_len = 2 + 1 + len(name_bytes) + len(payload)
    header = struct.pack('<H', total_len); msg_id = struct.pack('<H', 2) 
    return header + msg_id + bytes([len(name_bytes)]) + name_bytes + payload

def send_packet(client, lock, packet):
    with lock:
        try: client.sendall(packet)
        except OSError: pass 

# --- DEFINITIONS ---
def create_session_definition(name, duration_ms, is_race=False):
    session = GP.SeasonDefinition.SessionDefinition(); session.name = name
    scene = session.scene; scene.physics_type = 1
    scene.spawn.scale.x = 1.0; scene.spawn.scale.y = 1.0; scene.spawn.scale.z = 1.0
    tcd = scene.track_content_data; tcd.name = SERVER_CONFIG["track_name"]
    tcd.folder_path = f"content\\tracks\\{SERVER_CONFIG['track_id']}"
    tcd.file_path = f"content\\tracks\\{SERVER_CONFIG['track_id']}\\{SERVER_CONFIG['track_id']}_francorchamps.scene"
    tcd.track_data_path = f"content\\tracks\\{SERVER_CONFIG['track_id']}\\dynamic_track\\{SERVER_CONFIG['track_id']}.track"
    tcd.nation = "BE"; tcd.continent = "Europe"; tcd.timezone = 1; tcd.is_release = True
    tcd.coordinates.latitude = 50.345; tcd.coordinates.longitude = 5.971
    scene.layout_image.margin = 10; scene.layout_image.min_x = -1465.85; scene.layout_image.min_y = -2224.94; scene.layout_image.k_multiplier = 2224.94
    base_cont = f"content\\tracks\\{SERVER_CONFIG['track_id']}\\containers"
    containers = [f"{base_cont}\\camera_sequence_practice.scene", f"{base_cont}\\layout_gp.scene", f"{base_cont}\\marshalls_dlp.scene", f"{base_cont}\\pitlane_race.scene", f"{base_cont}\\pitlane_zones_gp.scene", f"{base_cont}\\spawnpoints_pitlane.scene", f"{base_cont}\\timelines.scene", f"{base_cont}\\tv1_cameras.scene", f"{base_cont}\\tv2_cameras.scene", f"{base_cont}\\vr_cameras.scene"]
    if is_race: containers.append(f"{base_cont}\\spawnpoints_grid.scene")
    del scene.containers[:]; scene.containers.extend(containers); scene.event_name = "GP " + name
    if is_race:
        spec = IR.InstantRace.Specialization(); spec.base.session_duration_ms = duration_ms; spec.base.start_mode = 0
        session.specialization.type_url = "type.googleapis.com/InstantRace.Specialization"; session.specialization.value = spec.SerializeToString()
    else:
        hex_spec = "2205080910904E28013A00B2015A0A0AA201020803A206020A000A23F2010F0D0000004015CDCCCC3D1D00000040A206040A00101EA206070A0308FA0110640A2712077069746C616E65B20204083C1001A206070A0310904E103EA2060A0A0608840210904E1046BA0103454131C20103454131C20C101880DDDB012801309875380150B0EA01C202440A0908E80F1008180F200C150000803F1D00002041221D0D0000803F1517B7D1391D5C8F823F20112A0A0D0AD73340153D0A8F4092030D0A0B0A0012001A0025560DBB41E2020F0D8FC2753F15CDCC4C3E1D8FC2F53DFD02"
        session.specialization.type_url = "type.googleapis.com/TimeAttack.Specialization"
        session.specialization.value = bytes.fromhex(hex_spec)
    session.weather.initial_date_time.year = 2024; session.weather.initial_date_time.month = 8; session.weather.initial_date_time.day = 15; session.weather.initial_date_time.hour = 12
    session.weather.static_data.static_weather.ambient_temperature_c = 23.0; session.crowd_density = 0.8
    return session

def build_handshake():
    print(f"[GEN] Handshake V41...")
    resp = PC.ConnectToServerHandshakeResponse(); resp.handshake_result = 1; resp.connection_id = 1001
    resp.request_data.password_type = 1; resp.request_data.protocol_version = 4; resp.request_data.server_version = 2
    season = resp.gamemode_changed_event.season; season.name = SERVER_CONFIG["server_name"]; season.season_type = 2; season.gamemode_type = 1; season.no_leaderboard = True
    comp = season.entrylist.competitors.add(); comp.name = "SQCR Team"
    event_entry = season.event_map[0]; event_entry.name = "Race Weekend"
    event_entry.session_map[0].CopyFrom(create_session_definition("Practice", 3600000, is_race=False))
    event_entry.session_map[3].CopyFrom(create_session_definition("Race", 1800000, is_race=True))
    event_data = season.event_mutable_data[0]; car_mut = event_data.cars.add(); car_mut.registration_key = "12345"; car_mut.preferred_car_number = 1
    _ = resp.gamemode_changed_event.initial_session_data.gamemode_session_data
    return make_kunos_packet("ConnectToServerHandshakeResponse", resp)

# --- REPONSES ---
def build_pre_spawn_state_cloned():
    hex_payload = "080812540A38747970652E676F6F676C65617069732E636F6D2F54696D6541747461636B2E53746174652E47616D652E5265616479546F4E6578744D617012180A160A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6061A1554696D6541747461636B2E53746174652E47616D65"
    return make_kunos_packet("BroadcastStateMessage", bytes.fromhex(hex_payload))
def build_state_broadcast_cloned():
    hex_payload = "080212530A2B747970652E676F6F676C65617069732E636F6D2F506C6174666F726D526163654C6561646572626F617264122412220A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6063A0632003A0048014001483B1A1554696D6541747461636B2E53746174652E47616D65"
    return make_kunos_packet("BroadcastStateMessage", bytes.fromhex(hex_payload))
def build_session_initialization_cloned():
    hex_payload = "0A0808031201021A010212B5010AAB010A240A0F0D1D678DC415CAB6F5421D0B8D09C512001A0F0D0000803F150000803F1D0000803F0A240A0F0D562690C415B345F2421D76DD06C512001A0F0D0000803F150000803F1D0000803F0A240A0F0DACDF8FC415C219F2421DF8CE06C512001A0F0D0000803F150000803F1D0000803F0A240A0F0D39318DC415D16FF5421DA28109C512001A0F0D0000803F150000803F1D0000803FAA010A15F195483F1D0000803FB501CDCC4C3F1205920702080212B2040ABF010A290A0F0DBE106DC315427B23431D4C3334C4120515336A51C11A0F0DECFF7F3F150000803F1DECFF7F3F0A290A0F0DA7C253C315C21A24431D573C36C41205158D4C51C11A0F0DEDFF7F3F150000803F1DEDFF7F3F0A290A0F0D010F54C31520FD23431DB89036C4120515C81E51C11A0F0DECFF7F3F150000803F1DECFF7F3F0A290A0F0D926D6DC315828E23431DCC8034C4120515A6C751C11A0F0DECFF7F3F150000803F1DECFF7F3FAA010A0D0000803F159752663FB501CDCC4C3F0ABF010A290A0F0D55C4ADC4157EA592421D25638FC31205155C5ABC411A0F0DF9FF7F3F150000803F1DF9FF7F3F0A290A0F0D74E1AAC41516BC90421D020AA0C312051562B9BB411A0F0DF9FF7F3F150000803F1DFAFF7F3F0A290A0F0D2A11ABC415F6BF90421DC0F99FC312051518F8BB411A0F0DF8FF7F3F150000803F1DF8FF7F3F0A290A0F0D30E1ADC415868692421D52AF8FC3120515028ABC411A0F0DFAFF7F3F150000803F1DFAFF7F3FAA010A150000803F1D2D0FC03CB501CDCC4C3F0AA6010A240A0F0D57A885C415916CED421DDCEAE8C412001A0F0D0000803F150000803F1D0000803F0A240A0F0D62EF7EC415609EF0421DD4C9ECC412001A0F0D0000803F150000803F1D0000803F0A240A0F0DBA017FC415C1A6F0421DECDCECC412001A0F0D0000803F150000803F1D0000803F0A240A0F0D10BB85C4158D88ED421DEC07E9C412001A0F0D0000803F150000803F1D0000803FAA01050D0000803FB501CDCC4C3F1203A20600D40002001E54696D6541747461636B2E436F6D6D616E642E4164645A6F6E65446174610AB0010AA8010A220A0F0D4D9093C415C75DF4421D086903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3F0A220A0F0D4DD093C415C75DF4421D086903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3F0A220A0F0D4DD093C415C75DF4421D088903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3F0A220A0F0D4D9093C415C75DF4421D088903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3FAA010F0D0000803F1567D5573F250000803FB501000000401203B206003C0002002354696D6541747461636B2E436F6D6D616E642E436F6E6E656374696F6E4C6F616465640A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6068A0002001554696D6541747461636B2E53746174652E47616D650A230A000A02080A0A0208140A0208150A0208160A02081E0A02085A1900901804DEACDD40122412220A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6063A0632003A0048014001483B1A0042180A160A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E606C23E085072616374696365310002002554696D6541747461636B2E436F6D6D616E642E55706461746547616D656D6F646554696D650900901804DEACDD4032000200174173736F63696174654361724E756D6265724576656E740A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E606103B860002001542726F61646361737453746174654D657373616765080212530A2B747970652E676F6F676C65617069732E636F6D2F506C6174666F726D526163654C6561646572626F617264122412220A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6063A0632003A0048014001483B1A1554696D6541747461636B2E53746174652E47616D65"
    return make_kunos_packet("TimeAttack.Command.SessionInitialization", bytes.fromhex(hex_payload))

def build_ui_gamemode_event_cloned():
    hex_payload = "0A04676F746F12086875642E68746D6C12096D61696E2F6D61696E"
    return make_kunos_packet("UIGameModeEvent", bytes.fromhex(hex_payload))

def build_car_spawn_mirror(incoming_payload):
    print("[GEN] Spawn Car (Miroir)...")
    client_req = CSP.RequestPlayerCar()
    try: client_req.ParseFromString(incoming_payload)
    except: return b""
    resp = CSP.ChangePlayerCarResponseEvent()
    resp.car_spawn_data.CopyFrom(client_req.car_spawn_data)
    resp.driver_info.CopyFrom(client_req.driver_info)
    resp.car_id.a = 12345; resp.car_id.b = 0; resp.car_number = 1; resp.result = 1
    resp.spawn_transform.position.x = -18.0; resp.spawn_transform.position.y = 104.5; resp.spawn_transform.position.z = -1800.0
    return make_kunos_packet("ChangePlayerCarResponseEvent", resp)
def build_physics_reset():
    cmd = PC.CommandFromRemote.Reset(); cmd.soft_reset = True
    return make_kunos_packet("CommandFromRemote.Reset", cmd)
def build_teleport_car():
    cmd = PC.TeleportCarCommand()
    cmd.car_id.a = 12345; cmd.car_id.b = 0; cmd.spawn_transform.position.x = -18.0; cmd.spawn_transform.position.y = 104.5; cmd.spawn_transform.position.z = -1800.0
    cmd.repair_car = True; cmd.reset_car_systems = True
    return make_kunos_packet("TeleportCarCommand", cmd)
def build_time_sync(time_ms=0.0):
    cmd = TA.TimeAttack.Command.UpdateGamemodeTime(); cmd.current_session_time_ms = time_ms; cmd.running = True
    return make_kunos_packet("TimeAttack.Command.UpdateGamemodeTime", cmd)
def build_udp_auth():
    resp = CSP.AssociateUDPSocketResponse(); resp.success = True; resp.connectionId = 1001
    return make_kunos_packet("AssociateUDPSocketResponse", resp)

# --- LOOPS ---
def game_update_task(client, stop_event, lock):
    print("[GAME LOOP] Démarrage horloge...")
    start_time = time.time()
    last_state_update = 0
    while not stop_event.is_set():
        try:
            # 10Hz (0.1s) est suffisant et évite de saturer si le thread est lent
            time.sleep(0.1)
            now_ms = (time.time() - start_time) * 1000.0
            send_packet(client, lock, build_time_sync(now_ms))
            if time.time() - last_state_update > 3.0:
                send_packet(client, lock, build_state_broadcast_cloned())
                last_state_update = time.time()
        except Exception: break

def game_session_init_task(client, payload, stop_event, lock):
    print("[TASK] Démarrage séquence Async...")
    try:
        send_packet(client, lock, build_pre_spawn_state_cloned()); time.sleep(0.5)
        send_packet(client, lock, build_car_spawn_mirror(payload)); time.sleep(0.5)
        send_packet(client, lock, build_physics_reset()); time.sleep(0.5)
        send_packet(client, lock, build_state_broadcast_cloned()); time.sleep(0.5)
        send_packet(client, lock, build_teleport_car()); time.sleep(0.5)
        send_packet(client, lock, build_session_initialization_cloned()); time.sleep(0.5)
        send_packet(client, lock, build_ui_gamemode_event_cloned()); time.sleep(0.5)
        
        print("✅ SESSION INITIALISÉE ! Passage à la boucle de temps.")
        game_update_task(client, stop_event, lock)
    except Exception as e: print(f"[TASK] Erreur: {e}")

def query_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.bind((BIND_IP, QUERY_PORT))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data == b"SQCR_QUERY":
                info = {"name": SERVER_CONFIG["server_name"], "track": SERVER_CONFIG["track_name"], "cars": SERVER_CONFIG["cars"], "port": PORT, "uuid": SERVER_CONFIG["uuid"], "max_players": SERVER_CONFIG["max_players"], "session_type": SERVER_CONFIG["session_type"]}
                sock.sendto(json.dumps(info).encode('utf-8'), addr)
        except: pass

def udp_game_logic():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.bind((BIND_IP, PORT))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if len(data) > 0 and data[0] == 0x05: sock.sendto(b'\x06' + data[1:], addr)
        except: pass

def tcp_client_handler(client, addr):
    print(f"🔥🔥 [TCP] Connexion : {addr}")
    stop_game_loop = threading.Event()
    client_lock = threading.Lock()
    try:
        while True:
            header = client.recv(2)
            if not header: break
            size = struct.unpack('<H', header)[0]
            
            # OPTIMISATION : Lecture bufferisée pour ne pas bloquer
            body = bytearray()
            while len(body) < size:
                packet = client.recv(size - len(body))
                if not packet: break
                body.extend(packet)
            
            if len(body) < size: break
            
            name_len = body[2]
            msg_name = body[3 : 3+name_len].decode('utf-8', errors='ignore')
            payload = body[3+name_len:]
            
            if msg_name == "ClientConnectionRequest":
                send_packet(client, client_lock, build_handshake())
                time.sleep(0.05)
                send_packet(client, client_lock, build_udp_auth())

            elif msg_name == "RequestPlayerCar":
                threading.Thread(target=game_session_init_task, args=(client, payload, stop_game_loop, client_lock), daemon=True).start()
            
            elif msg_name == "UpdateGameCarState":
                print("UpdateGameCarState")
                pass 

    except Exception as e: print(f"   Erreur TCP: {e}")
    finally:
        stop_game_loop.set()
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
    print("--- SQCR GAME Server ---")
    start_server()
