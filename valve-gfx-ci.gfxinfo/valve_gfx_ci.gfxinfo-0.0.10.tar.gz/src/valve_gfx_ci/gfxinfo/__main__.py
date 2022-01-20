from . import find_gpu, VulkanInfo
import sys
import json


def main():
    if gpu := find_gpu():
        gfxinfo = {
            'tags': list(gpu.tags),
            'structured_tags': gpu.structured_tags,
        }
        if info := VulkanInfo.construct():
            gfxinfo["vk:vram_size_gib"] = "%.2f" % info.VRAM_heap.GiB_size
            gfxinfo["vk:gtt_size_gib"] = "%.2f" % info.GTT_heap.GiB_size
            if info.mesa_version is not None:
                gfxinfo["mesa:version"] = info.mesa_version
            if info.mesa_git_version is not None:
                gfxinfo["mesa:git:version"] = info.mesa_git_version
            if info.device_name is not None:
                gfxinfo["vk:device:name"] = info.device_name
            if info.device_type is not None:
                gfxinfo["vk:device:type"] = info.device_type.name
            if info.api_version is not None:
                gfxinfo["vk:api:version"] = info.api_version
            if info.driver_name is not None:
                gfxinfo["vk:driver:name"] = info.driver_name
        json.dump(gfxinfo, sys.stdout)
        sys.stdout.write("\n")
        sys.exit(0)
    else:
        json.dump({"error": "No suitable GPU"})
        sys.exit(1)


if __name__ == '__main__':
    main()
