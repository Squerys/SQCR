from mitmproxy import ctx
import os
import time

# Dossier de sortie (Sur ton bureau pour être sûr)
OUTPUT_DIR = r"C:\Users\ADRN\Desktop\ACC\dump_join_seq"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class JoinDumper:
    def __init__(self):
        self.counter = 0

    def websocket_message(self, flow):
        message = flow.websocket.messages[-1]
        
        # On veut voir ce que le CLIENT demande (>>), et ce que le SERVEUR répond (<<)
        # pour comprendre le dialogue complet.
        direction = "REQ" if message.from_client else "RESP"
        
        content = message.content
        name = "Unknown"
        
        # --- DÉTECTION DES MESSAGES CRITIQUES ---
        
        # 1. Le Clic (Sélection)
        if b"MultiplayerServerListRequestSelectServer" in content:
            name = "01_Select_Request"
        elif b"MultiplayerServerListResponseSelectServer" in content:
            name = "02_Select_Response"
            
        # 2. Le Ping (La vérification de vie)
        elif b"MultiplayerServerListRequestPing" in content:
            name = "03_Ping_Request"
        elif b"MultiplayerServerListResponsePing" in content:
            name = "04_Ping_Response" # <--- C'est probablement celui qui te manque !

        # 3. La Connexion (Le bouton Join)
        elif b"MultiplayerServerListRequestConnectToServer" in content:
            name = "05_Connect_Request"
        elif b"MultiplayerServerListResponseConnectToServer" in content:
            name = "06_Connect_Response"

        # Si c'est un message intéressant, on le sauvegarde
        if name != "Unknown":
            self.counter += 1
            filename = f"{self.counter:02d}_{direction}_{name}.bin"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(content)
            
            ctx.log.alert(f"🎯 [SQCR] Capturé : {filename}")

addons = [JoinDumper()]
