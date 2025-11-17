from mitmproxy import ctx
import os
import time

#mitm proxy script to dump interesting protobuf entries
OUTPUT_DIR = r"C:\Users\ADRN\Desktop\ACC\dump_join_seq"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class JoinDumper:
    def __init__(self):
        self.counter = 0

    def websocket_message(self, flow):
        message = flow.websocket.messages[-1]
        
        direction = "REQ" if message.from_client else "RESP"
        
        content = message.content
        name = "Unknown"

        
        if b"MultiplayerServerListRequestSelectServer" in content:
            name = "01_Select_Request"
        elif b"MultiplayerServerListResponseSelectServer" in content:
            name = "02_Select_Response"
            
        elif b"MultiplayerServerListRequestPing" in content:
            name = "03_Ping_Request"
        elif b"MultiplayerServerListResponsePing" in content:
            name = "04_Ping_Response" 

        elif b"MultiplayerServerListRequestConnectToServer" in content:
            name = "05_Connect_Request"
        elif b"MultiplayerServerListResponseConnectToServer" in content:
            name = "06_Connect_Response"


        if name != "Unknown":
            self.counter += 1
            filename = f"{self.counter:02d}_{direction}_{name}.bin"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(content)
            
            ctx.log.alert(f"[SQCR] Capturé : {filename}")

addons = [JoinDumper()]

