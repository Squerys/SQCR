import sys
import os
import struct

# --- SETUP DES CHEMINS PROTOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, 'generated_protos')
sys.path.append(proto_dir)

try:
    import generated_protos.PlatformCommands_pb2 as PC
    print("[INIT] Modules Protobuf chargés.")
except ImportError as e:
    print(f"[ERREUR] Impossible de charger les protos : {e}")
    sys.exit(1)

# Nom du fichier binaire à lire
INPUT_FILE = "1_handshake_FULL.bin"
OUTPUT_TEXT = "decoded_handshake_full.txt"

def decode_bin_file():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERREUR] Le fichier {INPUT_FILE} est introuvable.")
        return

    print(f"Lecture de {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'rb') as f:
        data = f.read()

    print(f"Taille totale du fichier : {len(data)} bytes")

    # --- 1. ANALYSE DE L'ENTÊTE KUNOS ---
    # Structure: [Length (2)] [MsgID (2)] [NameLen (1)] [ProtoName (NameLen)] [Payload (...)]
    
    offset = 0
    
    try:
        # Lecture Taille (2 bytes) et ID (2 bytes)
        total_len = struct.unpack('<H', data[offset:offset+2])[0]
        msg_id = struct.unpack('<H', data[offset+2:offset+4])[0]
        offset += 4
        
        # Lecture Taille du nom (1 byte)
        name_len = data[offset]
        offset += 1
        
        # Lecture du Nom du Proto
        proto_name = data[offset : offset+name_len].decode('utf-8')
        offset += name_len
        
        print(f"\n[HEADER KUNOS]")
        print(f"  Length: {total_len}")
        print(f"  Msg ID: {msg_id}")
        print(f"  Proto : {proto_name}")
        
        # --- 2. DÉCODAGE PROTOBUF ---
        payload = data[offset:]
        print(f"  Payload Size: {len(payload)} bytes")

        if proto_name == "ConnectToServerHandshakeResponse":
            message = PC.ConnectToServerHandshakeResponse()
            message.ParseFromString(payload)
            
            print("\n[SUCCÈS] Protobuf décodé avec succès !")
            
            # Écriture dans un fichier texte pour analyse
            with open(OUTPUT_TEXT, "w", encoding="utf-8") as out:
                out.write(str(message))
            
            print(f"✅ Résultat sauvegardé dans '{OUTPUT_TEXT}'")
            print("   -> Ouvre ce fichier pour voir tous les champs manquants (EntryList, etc.)")
            
        else:
            print(f"[INFO] Ce décodeur est prévu pour 'ConnectToServerHandshakeResponse', reçu : {proto_name}")
            # Tentative générique si besoin...

    except Exception as e:
        print(f"\n[CRASH] Erreur lors du décodage : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    decode_bin_file()
