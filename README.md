# SQCR

The AC Evo client does not hardcode IP addresses for game servers. Instead, it fetches a list from a "Master Server" via a secure WebSocket connection.

Current data acquired by:

    Redirecting the Master Server domain (b.gk.sd) to 127.0.0.1 (localhost) via the hosts file.

    Emulating the WSS handshake and SSL termination locally.

    Replying to the game client with a custom-generated server list (Protobuf) containing your IP addresses instead of the official ones.

Protocol Analysis & Reverse Engineering :

Connection Endpoints

    Target Domain: b.gk.sd

    Protocol: WSS (WebSocket over TLS)

    Port: 6990 (TCP)

    Payload Format: Hybrid (Text-based Handshake + Google Protocol Buffers)

The Connection Flow

The communication happens in 4 distinct phases within the WebSocket stream:

1. The Text-Based Handshake

Upon establishing the socket connection, the client sends a raw text string separated by pipes (|). This is not Protobuf.

Client sends:
Plaintext

1|AuthTokenString|SteamID64|1

Example: 1|thisIsTheAuthToken|4404427680|1

2. Registration (Protobuf)

The client switches to binary Protobuf messages. Messages are identified by a string header (e.g., type.googleapis.com/...).

    Client Request: type.googleapis.com/RegisterRequest

        Payload: Machine ID / Server Token.

    Server Response: type.googleapis.com/RegisterResponse

3. Account Authentication

    Client Request: type.googleapis.com/GameEconomyClientRequestAccount

        Payload: Contains the user's SteamID.

    Server Response: type.googleapis.com/GameEconomyClientResponseAccount

        Payload: Returns the player's UUID and Display Name (e.g., "Mathieu Buannic").

4. The Server List (The Payload)

This is where the magic happens.

    Client Request: type.googleapis.com/MultiplayerServerListRequestServerList

    Server Response: type.googleapis.com/MultiplayerServerListResponseServerList

This response contains a repeated list of Server Objects. We have decoded the following string fields within the binary blob:

    Server Name: Beta | Server #28 | MX5 @ Mount Panorama

    Address: 31.44.44.11:58634 (Zurich) or 46.21.29.21:53060 (Milan)

    UUID: 85ea98bc-2c2e-4615-aca8-b15f58c0aa52

    Session Config: Race Weekend, Practice, Qualifying

    Track ID: Mount Panorama, Red Bull Ring

    Allowed Cars: ks_mazda_mx5_nd_cup, ks_bmw_m4_gt3

Contributing: Decoding the Schema

You could theoratically already add servers to the list by intercepting the server's list response, editing it and replaying it to the client
I suck at developping and reverse engineering, if you got some skills, no matter what your level is, any help is appreciated.

TODO :
 * Capturing traffic when joining, playing and leaving official servers
 * Completely understand used data structures
 * Implement a custom server binary based the previous data.
