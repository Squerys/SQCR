import sys
import os
import struct
import difflib
from google.protobuf import text_format

# --- IMPORT DU SERVEUR EXISTANT ---
# On importe ton script pour utiliser sa fonction build_handshake()
# Assure-toi que ton script s'appelle bien 'sqcr_gameserver.py' (ou modifie la ligne ci-dessous)
try:
    import gameserver as MyServer 
except ImportError:
    print("❌ Impossible d'importer 'gameserver.py'. Vérifie le nom du fichier.")
    sys.exit(1)

# --- CONFIG ---
TEMPLATE_FILE = "1_handshake_FULL.bin"

def extract_proto_from_kunos_packet(data):
    """Retire l'en-tête TCP Kunos pour récupérer le Protobuf pur"""
    if len(data) < 37: return None
    
    # L'entête Kunos standard fait 37 octets pour ce message :
    # [TotalLen 2] + [ID 2] + [NameLen 1] + ["ConnectToServerHandshakeResponse" 32]
    # On vérifie quand même la longueur du nom pour être robuste
    name_len = data[4]
    header_size = 2 + 2 + 1 + name_len
    
    return data[header_size:]

def compare():
    print(f"🔍 COMPARATIF : Généré vs Référence ({TEMPLATE_FILE})")
    
    # 1. CHARGEMENT DE LA RÉFÉRENCE (DUMP)
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Fichier de référence '{TEMPLATE_FILE}' introuvable.")
        return

    ref_proto = MyServer.PC.ConnectToServerHandshakeResponse()
    with open(TEMPLATE_FILE, "rb") as f:
        raw_ref = f.read()
        proto_data_ref = extract_proto_from_kunos_packet(raw_ref)
        try:
            ref_proto.ParseFromString(proto_data_ref)
            print("✅ Référence (Dump) décodée.")
        except Exception as e:
            print(f"❌ Erreur décodage référence : {e}")
            return

    # 2. GÉNÉRATION DE TA VERSION
    try:
        # On appelle la fonction de ton serveur
        raw_gen = MyServer.build_handshake()
        proto_data_gen = extract_proto_from_kunos_packet(raw_gen)
        
        gen_proto = MyServer.PC.ConnectToServerHandshakeResponse()
        gen_proto.ParseFromString(proto_data_gen)
        print("✅ Génération (Script) décodée.")
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        return

    # 3. COMPARAISON TEXTUELLE
    # Convertit les objets en texte lisible pour les comparer
    ref_str = text_format.MessageToString(ref_proto)
    gen_str = text_format.MessageToString(gen_proto)

    print("\n" + "="*40)
    print("RÉSULTAT DU DIFFÉRENTIEL")
    print("="*40)
    
    diff = difflib.unified_diff(
        ref_str.splitlines(),
        gen_str.splitlines(),
        fromfile='REFERENCE (Dump)',
        tofile='GÉNÉRÉ (Ton Script)',
        lineterm=''
    )
    
    diff_found = False
    for line in diff:
        diff_found = True
        # Coloriage basique pour la console
        if line.startswith('+'):
            print(f"\033[92m{line}\033[0m") # Vert (Ce que tu as ajouté/changé)
        elif line.startswith('-'):
            print(f"\033[91m{line}\033[0m") # Rouge (Ce qui manque par rapport au dump)
        elif line.startswith('^'):
            print(f"\033[94m{line}\033[0m") # Bleu (Info structure)
        else:
            print(line)

    if not diff_found:
        print("🎉 INCROYABLE ! Les deux paquets sont strictement identiques.")
    else:
        print("\n" + "="*40)
        print("LÉGENDE :")
        print("[-] Rouge : Présent dans le vrai serveur, mais MANQUANT chez toi.")
        print("[+] Vert  : Présent chez toi, mais différent ou absent du vrai serveur.")

if __name__ == "__main__":
    compare()
