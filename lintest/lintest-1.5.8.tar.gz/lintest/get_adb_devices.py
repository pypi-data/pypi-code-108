import subprocess
import traceback

try:
    import settings
except ImportError:
    traceback.print_exc()


def get_adb_devices():
    """
    Returns: the adb devices list

    @author: Wang Lin
    """

    adb_devices = []
    offline_devices = []
    device_name_list = []

    return []  # 暂时不开启 APPIUM

    system_info = subprocess.check_output("adb devices", shell=True, universal_newlines=True)

    for info in system_info.splitlines():
        if info.endswith("device"):
            adb_devices.append(info.split("	")[0])
        elif info.endswith("offline"):
            offline_devices.append(info)

    for device_name in adb_devices:
        if device_name in settings.DEVICE_ID_NAME_DICT.keys():
            device_name_list.append(settings.DEVICE_ID_NAME_DICT.get(device_name))
        else:
            device_name_list.append(device_name)

    return device_name_list


if __name__ == "__main__":
    device_list = get_adb_devices()
    print(device_list)
