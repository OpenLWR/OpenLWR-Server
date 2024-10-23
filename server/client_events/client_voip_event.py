from server.server_events import server_voip_event


def handle(data, source_user):
    server_voip_event.fire(data,source_user)
