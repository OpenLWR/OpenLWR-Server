import base64

def build(packet_id, data):
    return f"{packet_id}|{base64.b64encode(data.encode('utf-8'))}"