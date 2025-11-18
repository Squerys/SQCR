import sys

# --- CONFIG ---
INPUT_FILE = "dump_wss/03_ServerList.bin" # Ton fichier de 84ko
# --------------

def read_varint(data, offset):
    value = 0
    shift = 0
    while True:
        if offset >= len(data): raise IndexError("EOF")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return value, offset
        shift += 7

def decode_proto(data, indent=0):
    offset = 0
    # Limite de sécurité pour éviter la récursion infinie sur des faux positifs
    if indent > 10: return

    while offset < len(data):
        try:
            # On tente de lire un Tag
            # Si ça échoue ou si le tag est invalide, ce n'est pas un message
            tag, new_offset = read_varint(data, offset)
            field_id = tag >> 3
            wire_type = tag & 0x07
            
            # Validité basique
            if field_id == 0: raise ValueError("ID 0 invalide")
            
            offset = new_offset
            prefix = "  " * indent + f"[{indent}] "
            
            if wire_type == 0: # Varint
                val, offset = read_varint(data, offset)
                print(f"{prefix}ID {field_id}: {val} (Int)")

            elif wire_type == 1: # 64-bit
                val = data[offset:offset+8]
                offset += 8
                # print(f"{prefix}ID {field_id}: <64-bit>")

            elif wire_type == 2: # Length Delimited
                length, offset = read_varint(data, offset)
                content = data[offset:offset+length]
                offset += length
                
                # ANALYSE DU CONTENU (Le cœur du problème)
                is_text = False
                try:
                    text = content.decode('utf-8')
                    if len(text) > 2 and text.isprintable():
                        print(f"{prefix}ID {field_id} (String): \"{text}\"")
                        is_text = True
                except: pass

                # Si ce n'est pas du texte évident, on essaie de le décoder comme un message
                if not is_text and length > 0:
                    # On tente une récursion spéculative
                    try:
                        # On affiche l'entête avant, au cas où ça plante
                        print(f"{prefix}ID {field_id} (Bytes {length}) -> Tentative d'ouverture...")
                        decode_proto(content, indent + 1)
                    except:
                        # Si la récursion échoue, c'était juste des octets
                        pass

            elif wire_type == 5: # 32-bit
                offset += 4
                # print(f"{prefix}ID {field_id}: <32-bit>")
                
            else:
                raise ValueError(f"WireType {wire_type} inconnu")

        except Exception:
            # Ce n'était pas un message Protobuf valide, on remonte
            return

def main():
    try:
        with open(INPUT_FILE, "rb") as f:
            data = f.read()
        print(f"📂 Décodage récursif forcé de {INPUT_FILE}...")
        decode_proto(data)
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
