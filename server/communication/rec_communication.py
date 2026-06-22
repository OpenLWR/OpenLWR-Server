import numpy as np
import server.protocols.rec_pb2 as rec_proto
import time
from enum import Enum
import config

class RecStatus(Enum):
    OK = 0,
    REJECTED = 1,
    UNKNOWN = 2,

class RecCommunication:
    def __init__(self):
        pass
        
    def CreateDefaultRecMessage(self,message_type:rec_proto.RECMessageType):
        msg = rec_proto.RECMessage()
        msg.header.magic_number = 0x1312
        msg.header.protocol_version = 1
        msg.type = message_type
        return msg
    
    def CreateRecSessionClose(self,reason:rec_proto.RECSessionClose.Reason,message:str):
        #make the close message
        closemsg = rec_proto.RECSessionClose()
        closemsg.reason = reason
        closemsg.message = message

        #make a default rec message, and add the close message as a payload
        def_message = self.CreateDefaultRecMessage(rec_proto.RECMessageType.REC_SESSION_CLOSE)
        def_message.session_close.CopyFrom(closemsg)
        return def_message
      
    def CreateRecHandshakeAck(self,session_id):
        #make the ack message
        msg = rec_proto.RECHandshakeAck()
        msg.session_id = session_id

        msg.server_tick = 0 #TODO: implement tick
        msg.server_time = int(time.time() * 1000)

        #make a default rec message, and add the message as a payload
        def_message = self.CreateDefaultRecMessage(rec_proto.RECMessageType.REC_HANDSHAKE_ACK)
        def_message.handshake_ack.CopyFrom(msg)

        return def_message

    def CreateRecServerInfo(self,server_name,version,motd,max_sessions,current_sessions): #TODO: capabilities
        msg = rec_proto.RECServerInfo()
        msg.server_name = server_name
        msg.server_version = version
        msg.motd = motd
        msg.max_sessions = max_sessions
        msg.current_sessions = current_sessions

        def_message = self.CreateDefaultRecMessage(rec_proto.RECMessageType.REC_SERVER_INFO)
        def_message.server_info.CopyFrom(msg)

        return def_message

    def CreateRecEvent(self,data:bytes):
        msg = rec_proto.RECEvent()
        msg.data = data

        def_message = self.CreateDefaultRecMessage(rec_proto.RECMessageType.REC_EVENT)
        def_message.event.CopyFrom(msg)
        return def_message


    def RecHandshake(self,data,session_id):
        major_ver = data.handshake.client_major_version

        Status = RecStatus.UNKNOWN

        #TODO: change major and minor version to be configurable
        if major_ver != 1:
            msg = self.CreateRecSessionClose(rec_proto.RECSessionClose.Reason.VERSION_MISMATCH,"Server requires major version 1")
            Status = RecStatus.REJECTED
        else:
            msg = self.CreateRecHandshakeAck(session_id)
            Status = RecStatus.OK
        
        return Status,msg
    
    def RecServerInfo(self,player_count:int):
        major_version = config.config["server_major_version"]
        minor_version = config.config["server_minor_version"]
        server_name = config.config["server_name"]
        motd = config.config["motd"]
        max_player_count = config.config["max_player_count"]
        current_player_count = player_count

        server_version = f"{major_version}.{minor_version}"

        return self.CreateRecServerInfo(server_name,server_version,motd,max_player_count,current_player_count)