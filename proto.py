import sys
import os
import importlib

# --- SETUP PATH ---
# On ajoute le dossier COURANT au path pour que Python trouve le dossier "generated_protos"
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# On ajoute AUSSI le sous-dossier pour les dépendances internes
sys.path.append(os.path.join(current_dir, 'generated_protos'))

print(f"🔍 Recherche des modules dans : {current_dir}")

# --- IMPORT ---
try:
    # On essaie d'importer le module principal
    import generated_protos.PlatformCommands_pb2 as PC
    import generated_protos.ClientServerProtocol_pb2 as CSP
    print("✅ Modules chargés.")
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    print("   Vérifiez que le dossier 'generated_protos' existe et contient '__init__.py'")
    # Tentative de fallback (si les fichiers sont à la racine du path)
    try:
        import PlatformCommands_pb2 as PC
        print("✅ Modules chargés (Mode direct).")
    except:
        sys.exit(1)

def inspect_recursive(descriptor, indent=0, visited=None):
    """Parcourt récursivement la structure du message Protobuf"""
    if visited is None: visited = set()
    
    # On évite les boucles infinies (récursion)
    if descriptor.full_name in visited:
        return
    visited.add(descriptor.full_name)

    prefix = "  " * indent
    print(f"{prefix}📦 {descriptor.name}")
    
    for field in descriptor.fields:
        # Type 11 = MESSAGE (Sous-objet)
        if field.type == 11:
            print(f"{prefix}  - [ID {field.number}] {field.name} (Sous-Objet: {field.message_type.name})")
            # On plonge dedans
            inspect_recursive(field.message_type, indent + 1, visited)
        else:
            # Champ simple
            print(f"{prefix}  - [ID {field.number}] {field.name} (Type {field.type})")

print("\n" + "="*40)
print("STRUCTURE DE ConnectToServerHandshakeResponse")
print("="*40)

try:
    resp = PC.ConnectToServerHandshakeResponse.DESCRIPTOR
    inspect_recursive(resp)
except Exception as e:
    print(f"Erreur lors de l'inspection : {e}")

print("\n" + "="*40)
