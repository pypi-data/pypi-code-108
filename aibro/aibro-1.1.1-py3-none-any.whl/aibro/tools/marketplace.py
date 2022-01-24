def _check_machines_exist(machine_id, marketplace):
    if machine_id in marketplace and marketplace[machine_id]["CAPACITY"] > 0:
        return True
    else:
        return False
