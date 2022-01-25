def build_tenant_name(client_id, name):
    if client_id and name:
        return f"{client_id} - {name}"[0:100].strip()
    elif client_id:
        return f"{client_id}"
    else:
        return f"{name}"[0:100].strip()
