import base64

def build(packet_id, data = ""):
    return f"{packet_id}|{base64.b64encode(data.encode('utf-8')).decode('utf-8')}"

def parse(packet):
    packet = packet.split("|")
    return int(packet[0]), base64.b64decode(packet[1]).decode('utf-8')