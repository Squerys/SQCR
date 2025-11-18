import socket
import threading
import select
import time
import os
import re
import sys

# --- CONFIGURATION ---
LOCAL_IP = "0.0.0.0"
LOCAL_PORT = 9000

# REAL TARGET SERVER (LFM ZURICH or another working server)
# Ensure this IP/Port is correct for the current moment!
REMOTE_IP = "45.143.159.102" 
REMOTE_PORT = 9003

# Dump directory
DUMP_DIR = "dumps_proxy"
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)

def save_dump(data, prefix):
    """Saves data to a file without crashing the script."""
    try:
        # 1. Sanitize the filename prefix (remove newlines, spaces, special chars)
        clean_prefix = prefix.strip().replace('>', '').replace('-', '').replace(' ', '_')
        clean_prefix = re.sub(r'[^a-zA-Z0-9_]', '', clean_prefix)
        
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}_{clean_prefix}.bin"
        filepath = os.path.join(DUMP_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(data)
            
        print(f"[{prefix}] ({len(data)} bytes) -> Saved as {filename}")
        
    except Exception as e:
        print(f"[ERROR_DUMP] ({prefix}): {e}")
        # IMPORTANT: Do not re-raise the error to keep the connection alive!

def forward(src, dst, direction):
    """Transfers data and logs the exchange."""
    try:
        while True:
            # Check for data available to read
            rlist, _, _ = select.select([src], [], [], 0.1) # Check every 100ms
            if rlist:
                data = src.recv(4096)
                if not data: break
                
                # Log and Save DUMP
                if direction == "C->S":
                    save_dump(data, "CLIENT_TO_SERVER")
                else:
                    save_dump(data, "SERVER_TO_CLIENT")
                    
                # Forward the data
                dst.sendall(data)
            time.sleep(0.001) # Small sleep to avoid CPU excessive usage
    except Exception as e:
        # Catch connection reset/closed errors
        print(f"[FORWARD_END] Connection closed by {direction}")
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def start_tcp_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCAL_IP, LOCAL_PORT))
    server.listen(5)
    print(f"[INFO] TCP Proxy Dumper ready: :{LOCAL_PORT} ===> {REMOTE_IP
