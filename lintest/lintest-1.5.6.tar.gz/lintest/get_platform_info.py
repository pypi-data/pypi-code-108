import platform
import subprocess


def get_platform_info():
    """
    Returns: the OS name & release version

    @author: Wang Lin
    """
    if platform.system() == "Windows":

        system_info = subprocess.check_output("systeminfo", shell=True, universal_newlines=True)

        for line in system_info.splitlines():
            if "OS Name:" in line:
                return line.split("OS Name:")[1].strip()

    elif platform.system() == "Darwin":
        system_info = subprocess.check_output("sw_vers", shell=True, universal_newlines=True)
        # print(type(system_info))

        for info in system_info.splitlines():
            if "ProductName" in info:
                product_name = info.split(":")[1].strip()

            if "ProductVersion" in info:
                product_version = info.split(":")[1].strip()

        return product_name + " " + product_version

    else:
        return platform.system() + " " + platform.release()

def get_xcode_version():
    if platform.system() == "Darwin":
        xcode_info = subprocess.check_output("xcodebuild -version", shell=True, universal_newlines=True)

        for info in xcode_info.splitlines():
            if "xcode" in info.lower():
                xcode_version = info.split(" ")[1]
                return xcode_version


def get_ios_platform_version():
    if platform.system() == "Darwin":
        ios_platform_version = subprocess.check_output("xcrun simctl list devices", shell=True, universal_newlines=True)

        for info in ios_platform_version.splitlines():
            if "iOS" in info:
                ios_platform_version = info.split("iOS")[1].strip().split('-')[0]
                return ios_platform_version.strip()


if __name__ == "__main__":
    print(get_platform_info())
