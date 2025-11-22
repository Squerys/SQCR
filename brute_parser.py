import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, 'generated_protos')
sys.path.append(proto_dir)

import generated_protos.gamemodes.CruiseGameModeData_pb2 as CruiseGameModeData_pb2 
import generated_protos.gamemodes.DriftChallengeData_pb2 as DriftChallengeData_pb2
import generated_protos.gamemodes.HotStintData_pb2 as HotStintData_pb2
import generated_protos.gamemodes.InstantRaceData_pb2 as InstantRaceData_pb2
import generated_protos.gamemodes.PaintShopGameModeData_pb2 as PaintShopGameModeData_pb2
import generated_protos.gamemodes.TimeAttackData_pb2 as TimeAttackData_pb2
import generated_protos.gamemodes.VehicleAnalysisMode_pb2 as VehicleAnalysisMode_pb2

import generated_protos.AiCarData_pb2 as AiCarData_pb2
import generated_protos.AIData_pb2 as AIData_pb2
import generated_protos.AudioData_pb2 as AudioData_pb2
import generated_protos.BackendMessages_pb2 as BackendMessages_pb2
import generated_protos.BackendMessage_pb2 as BackendMessage_pb2
import generated_protos.BackendTest_pb2 as BackendTest_pb2
import generated_protos.CameraProperties_pb2 as CameraProperties_pb2
import generated_protos.CarBehaviour_pb2 as CarBehaviour_pb2
import generated_protos.CarCustomizationCommands_pb2 as CarCustomizationCommands_pb2
import generated_protos.CarDataCache_pb2 as CarDataCache_pb2
import generated_protos.CarData_pb2 as CarData_pb2
import generated_protos.CarInstrumentationData_pb2 as CarInstrumentationData_pb2
import generated_protos.CarSelectionClientCommands_pb2 as CarSelectionClientCommands_pb2
import generated_protos.CarSetupCommands_pb2 as CarSetupCommands_pb2
import generated_protos.CarSetupLimits_pb2 as CarSetupLimits_pb2
import generated_protos.CarSetup_pb2 as CarSetup_pb2
import generated_protos.CarTuning_pb2 as CarTuning_pb2
import generated_protos.ClientCommandsUtil_pb2 as ClientCommandsUtil_pb2
import generated_protos.ClientServerProtocol_pb2 as ClientServerProtocol_pb2
import generated_protos.Customization_pb2 as Customization_pb2
import generated_protos.CustomTable_pb2 as CustomTable_pb2
import generated_protos.DateTime_pb2 as DateTime_pb2
import generated_protos.DriverManager_pb2 as DriverManager_pb2
import generated_protos.EvoUiTypes_pb2 as EvoUiTypes_pb2
import generated_protos.GameEconomyClientCommands_pb2 as GameEconomyClientCommands_pb2
import generated_protos.GameEconomy_pb2 as GameEconomy_pb2
import generated_protos.GameModeCommands_pb2 as GameModeCommands_pb2
import generated_protos.GameModeSelectionClientCommands_pb2 as GameModeSelectionClientCommands_pb2
import generated_protos.GameplaySettings_pb2 as GameplaySettings_pb2
import generated_protos.GameplayUI_pb2 as GameplayUI_pb2
import generated_protos.Gameplay_pb2 as Gameplay_pb2
import generated_protos.GraphicsSettingsOverride_pb2 as GraphicsSettingsOverride_pb2
import generated_protos.InputConfigurationCommands_pb2 as InputConfigurationCommands_pb2
import generated_protos.InputConfiguration_pb2 as InputConfiguration_pb2
import generated_protos.InputEnum_pb2 as InputEnum_pb2
import generated_protos.LogicScene_pb2 as LogicScene_pb2
import generated_protos.Math_pb2 as Math_pb2
import generated_protos.Mesh_pb2 as Mesh_pb2
import generated_protos.MfdCommands_pb2 as MfdCommands_pb2
import generated_protos.Mirrors_pb2 as Mirrors_pb2
import generated_protos.MultiplayerServerListCommands_pb2 as MultiplayerServerListCommands_pb2
import generated_protos.Options_pb2 as Options_pb2
import generated_protos.PenaltySystem_pb2 as PenaltySystem_pb2
import generated_protos.PhysicsSnapshot_pb2 as PhysicsSnapshot_pb2
import generated_protos.PlatformCommands_pb2 as PlatformCommands_pb2
import generated_protos.PlatformGameState_pb2 as PlatformGameState_pb2
import generated_protos.PlatformUiTypes_pb2 as PlatformUiTypes_pb2
import generated_protos.PostProcessing_pb2 as PostProcessing_pb2
import generated_protos.RacingSettingsCommands_pb2 as RacingSettingsCommands_pb2
import generated_protos.RatingData_pb2 as RatingData_pb2
import generated_protos.RegisterConnection_pb2 as RegisterConnection_pb2
import generated_protos.Renderer_pb2 as Renderer_pb2
import generated_protos.ReplayCommands_pb2 as ReplayCommands_pb2
import generated_protos.ReplayDebug_pb2 as ReplayDebug_pb2
import generated_protos.ReplayGalleryCommands_pb2 as ReplayGalleryCommands_pb2
import generated_protos.RuntimeStats_pb2 as RuntimeStats_pb2
import generated_protos.Scene_pb2 as Scene_pb2
import generated_protos.SeasonInfoCommands_pb2 as SeasonInfoCommands_pb2
import generated_protos.SettingsCommands_pb2 as SettingsCommands_pb2
import generated_protos.ShowroomCommands_pb2 as ShowroomCommands_pb2
import generated_protos.TerrainNew_pb2 as TerrainNew_pb2
import generated_protos.ThumbnailSettings_pb2 as ThumbnailSettings_pb2
import generated_protos.TimeTableCommands_pb2 as TimeTableCommands_pb2
import generated_protos.TrackData_pb2 as TrackData_pb2
import generated_protos.TyresData_pb2 as TyresData_pb2
import generated_protos.UIAudioCommands_pb2 as UIAudioCommands_pb2
import generated_protos.UIStorageCommands_pb2 as UIStorageCommands_pb2
import generated_protos.ViewSettingsCommands_pb2 as ViewSettingsCommands_pb2
import generated_protos.Weather_pb2 as Weather_pb2

from google.protobuf.message import Message
from google.protobuf.json_format import MessageToJson, Parse

# hex payload we want to reverse
# example payload takes a while cause it's quite large and doesn't directly match

hex_payload = "0A0808031201021A010212B5010AAB010A240A0F0D1D678DC415CAB6F5421D0B8D09C512001A0F0D0000803F150000803F1D0000803F0A240A0F0D562690C415B345F2421D76DD06C512001A0F0D0000803F150000803F1D0000803F0A240A0F0DACDF8FC415C219F2421DF8CE06C512001A0F0D0000803F150000803F1D0000803F0A240A0F0D39318DC415D16FF5421DA28109C512001A0F0D0000803F150000803F1D0000803FAA010A15F195483F1D0000803FB501CDCC4C3F1205920702080212B2040ABF010A290A0F0DBE106DC315427B23431D4C3334C4120515336A51C11A0F0DECFF7F3F150000803F1DECFF7F3F0A290A0F0DA7C253C315C21A24431D573C36C41205158D4C51C11A0F0DEDFF7F3F150000803F1DEDFF7F3F0A290A0F0D010F54C31520FD23431DB89036C4120515C81E51C11A0F0DECFF7F3F150000803F1DECFF7F3F0A290A0F0D926D6DC315828E23431DCC8034C4120515A6C751C11A0F0DECFF7F3F150000803F1DECFF7F3FAA010A0D0000803F159752663FB501CDCC4C3F0ABF010A290A0F0D55C4ADC4157EA592421D25638FC31205155C5ABC411A0F0DF9FF7F3F150000803F1DF9FF7F3F0A290A0F0D74E1AAC41516BC90421D020AA0C312051562B9BB411A0F0DF9FF7F3F150000803F1DFAFF7F3F0A290A0F0D2A11ABC415F6BF90421DC0F99FC312051518F8BB411A0F0DF8FF7F3F150000803F1DF8FF7F3F0A290A0F0D30E1ADC415868692421D52AF8FC3120515028ABC411A0F0DFAFF7F3F150000803F1DFAFF7F3FAA010A150000803F1D2D0FC03CB501CDCC4C3F0AA6010A240A0F0D57A885C415916CED421DDCEAE8C412001A0F0D0000803F150000803F1D0000803F0A240A0F0D62EF7EC415609EF0421DD4C9ECC412001A0F0D0000803F150000803F1D0000803F0A240A0F0DBA017FC415C1A6F0421DECDCECC412001A0F0D0000803F150000803F1D0000803F0A240A0F0D10BB85C4158D88ED421DEC07E9C412001A0F0D0000803F150000803F1D0000803FAA01050D0000803FB501CDCC4C3F1203A20600D40002001E54696D6541747461636B2E436F6D6D616E642E4164645A6F6E65446174610AB0010AA8010A220A0F0D4D9093C415C75DF4421D086903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3F0A220A0F0D4DD093C415C75DF4421D086903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3F0A220A0F0D4DD093C415C75DF4421D088903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3F0A220A0F0D4D9093C415C75DF4421D088903C51A0F0DC0FF7F3F1520FF7F3F1DCAFF7F3FAA010F0D0000803F1567D5573F250000803FB501000000401203B206003C0002002354696D6541747461636B2E436F6D6D616E642E436F6E6E656374696F6E4C6F616465640A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6068A0002001554696D6541747461636B2E53746174652E47616D650A230A000A02080A0A0208140A0208150A0208160A02081E0A02085A1900901804DEACDD40122412220A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6063A0632003A0048014001483B1A0042180A160A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E606C23E085072616374696365310002002554696D6541747461636B2E436F6D6D616E642E55706461746547616D656D6F646554696D650900901804DEACDD4032000200174173736F63696174654361724E756D6265724576656E740A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E606103B860002001542726F61646361737453746174654D657373616765080212530A2B747970652E676F6F676C65617069732E636F6D2F506C6174666F726D526163654C6561646572626F617264122412220A1408A091D9AAF3BCCDE34610B7ED8AFCA987E2E6063A0632003A0048014001483B1A1554696D6541747461636B2E53746174652E47616D65"
message = bytes.fromhex(hex_payload)

def try_parse_values_recursive(value, blob):
    success = []
    for v in vars(value).values():
        if isinstance(v, type) and issubclass(v, Message):
            success.extend(try_parse_values_recursive(v, blob))
            obj = v()
            try:
                obj.ParseFromString(blob)
                obj.DiscardUnknownFields()
                output = obj.SerializeToString()
                if output == blob:
                    success.append(obj)
            except Exception as e:
                continue
    return success


def try_parse_blob(blob: bytes):
    protos = [CruiseGameModeData_pb2, DriftChallengeData_pb2, HotStintData_pb2, InstantRaceData_pb2, PaintShopGameModeData_pb2, TimeAttackData_pb2, VehicleAnalysisMode_pb2, AiCarData_pb2, AIData_pb2, AudioData_pb2, BackendMessages_pb2, BackendMessage_pb2, BackendTest_pb2, CameraProperties_pb2, CarBehaviour_pb2, CarCustomizationCommands_pb2, CarDataCache_pb2, CarData_pb2, CarInstrumentationData_pb2, CarSelectionClientCommands_pb2, CarSetupCommands_pb2, CarSetupLimits_pb2, CarSetup_pb2, CarTuning_pb2, ClientCommandsUtil_pb2, ClientServerProtocol_pb2, Customization_pb2, CustomTable_pb2, DateTime_pb2, DriverManager_pb2, EvoUiTypes_pb2, GameEconomyClientCommands_pb2, GameEconomy_pb2, GameModeCommands_pb2, GameModeSelectionClientCommands_pb2, GameplaySettings_pb2, GameplayUI_pb2, Gameplay_pb2, GraphicsSettingsOverride_pb2, InputConfigurationCommands_pb2, InputConfiguration_pb2, InputEnum_pb2, LogicScene_pb2, Math_pb2, Mesh_pb2, MfdCommands_pb2, Mirrors_pb2, MultiplayerServerListCommands_pb2, Options_pb2, PenaltySystem_pb2, PhysicsSnapshot_pb2, PlatformCommands_pb2, PlatformGameState_pb2, PlatformUiTypes_pb2, PostProcessing_pb2, RacingSettingsCommands_pb2, RatingData_pb2, RegisterConnection_pb2, Renderer_pb2, ReplayCommands_pb2, ReplayDebug_pb2, ReplayGalleryCommands_pb2, RuntimeStats_pb2, Scene_pb2, SeasonInfoCommands_pb2, SettingsCommands_pb2, ShowroomCommands_pb2, TerrainNew_pb2, ThumbnailSettings_pb2, TimeTableCommands_pb2, TrackData_pb2, TyresData_pb2, UIAudioCommands_pb2, UIStorageCommands_pb2, ViewSettingsCommands_pb2, Weather_pb2]
    parsings = []
    for proto in protos:
        parsings.extend(try_parse_values_recursive(proto, blob))
    return parsings


# first we check for the entire message and see if we can parse it
# if we can't parse it we try again but with one less byte
# rinse and repeat untill we get a successfull parsing
for i in reversed(range(0,len(hex_payload))):
    msgs = try_parse_blob(message[:i])
    for msg in msgs:
        print("=================================================================")
        print("Message Type ================")
        print(type(msg))
        print("Message ================")
        json_msg = MessageToJson(msg)
        print(json_msg)
        print("================")
        print(f"{len(msg.SerializeToString())} bytes matched with input {len(message)}")
        print(msg.SerializeToString().hex())
        # go from JSON back to protobuf
        # parsed = Parse(json_msg, HotStintData_pb2.HotStint.Command.SessionInitialization())
        # print(parsed)
        exit()

print("No suitable parsing found")