import server.protocols.ubc_pb2 as ubc_proto
import server.devices as devices
import google.protobuf.any as protobuf

class UbcCommunication:
    def __init__(self):
        pass

    def CreatePayloadFromDevice(self,device:devices.DeviceBase):
        payload = ubc_proto.UBCMessage.Payload()
        payload.device_id = int(device.device_id)
        for field in device.get_fields:
            data = ubc_proto.UBCMessage.Payload.Data()
            data.field = field.field_id
            val = field.value
            if isinstance(val, bool):
                data.bool_value = val
            elif isinstance(val, int):
                data.int_value = val
            elif isinstance(val, float):
                data.float_value = val
            elif isinstance(val, str):
                data.string_value = val
            elif isinstance(val, bytes):
                data.bytes_value = val
            payload.data_fields.append(data)
        return payload

    def CreateMessage(self,session_id:int,tick:int,payloads:list):

        msg = ubc_proto.UBCMessage()
        msg.header.magic_number = 0x1312
        msg.header.protocol_version = 1
        msg.tick = tick
        msg.session_id = session_id
        msg.payloads.extend(payloads)

        any = protobuf.Any()

        any.Pack(msg)

        return any
