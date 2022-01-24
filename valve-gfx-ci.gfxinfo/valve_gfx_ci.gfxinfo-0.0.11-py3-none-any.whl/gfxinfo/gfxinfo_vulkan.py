try:
    from functools import cached_property
except ImportError:
    from backports.cached_property import cached_property
from enum import Enum
from cffi import FFI

import re
import vulkan as vk


class VulkanExtension:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __str__(self):
        return f"<VK extension {self.name} version {self.version}>"

    def __repr__(self):
        return f"{self.__class__}({self.__dict__})"


class VulkanHeap:
    DEVICE_LOCAL_BIT = vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
    VISIBLE_BIT = vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT
    COHERENT_BIT = vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
    HOST_CACHED_BIT = vk.VK_MEMORY_PROPERTY_HOST_CACHED_BIT
    LAZILY_ALLOCATED_BIT = vk.VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT

    def __init__(self, size, flags):
        self.size = size
        self.flags = flags
        self.types = 0

    def add_type(self, flags):
        self.types |= flags

    def has_type(self, flags):
        return self.types & flags

    @property
    def GiB_size(self):
        return self.size / (1024*1024*1024)


class VulkanDeviceType(Enum):
    OTHER = vk.VK_PHYSICAL_DEVICE_TYPE_OTHER
    INTEGRATED = vk.VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU
    DISCRETE = vk.VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
    VIRTUAL = vk.VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU
    CPU = vk.VK_PHYSICAL_DEVICE_TYPE_CPU


def get_vk_instance(app_info, enabled_extensions=None):
    if enabled_extensions is None:
        enabled_extensions = []
    create_info = vk.VkInstanceCreateInfo(
        sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        flags=0,
        pApplicationInfo=app_info,
        enabledExtensionCount=len(enabled_extensions),
        ppEnabledExtensionNames=enabled_extensions,
        enabledLayerCount=0,
        ppEnabledLayerNames=[])
    return vk.vkCreateInstance(create_info, None)


class VulkanInfo:
    @classmethod
    def construct(cls, device_index=0):
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName='gfxinfo',
            applicationVersion=vk.VK_MAKE_VERSION(0, 0, 3),
            pEngineName='No Engine',
            engineVersion=vk.VK_MAKE_VERSION(0, 0, 3),
            apiVersion=vk.VK_API_VERSION_1_0)

        try:
            instance = get_vk_instance(
                app_info,
                [vk.VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME])
            physical_device_properties_2_supported = True
        except vk.VkErrorIncompatibleDriver:
            print('Exception finding a compatible Vulkan diver (ICD).')
            return
        except vk.VkErrorExtensionNotPresent:
            physical_device_properties_2_supported = False
            print('WARNING: The {} extension is not supported. '
                  'Some information is not available.'.format(
                      vk.VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME))
            try:
                instance = get_vk_instance(app_info)
            except Exception as err:
                print('Exception creating Vulkan instance:', type(err))
                return
        except Exception as err:
            print('Exception creating Vulkan instance:', type(err))
            return

        try:
            physical_devices = vk.vkEnumeratePhysicalDevices(instance)
        except vk.VkErrorInitializationFailed:
            print('No supported Vulkan physical devices found.')
            vk.vkDestroyInstance(instance, None)
            return
        except Exception as err:
            print('Exception getting the physical Vulkan devices.', type(err))
            vk.vkDestroyInstance(instance, None)
            return

        if not physical_devices or (device_index + 1) > len(physical_devices):
            vk.vkDestroyInstance(instance, None)
            print("No Vulkan physical devices or bad device index: "
                  f"device_index={device_index} len(physical_devices)={len(physical_devices)}")
            return

        physical_device = physical_devices[device_index]
        return cls(instance, physical_device, physical_device_properties_2_supported)

    def __init__(self, instance, physical_device,
                 physical_device_properties_2_supported=False):
        self._physical_device_properties = vk.vkGetPhysicalDeviceProperties(
            physical_device)
        self._physical_device_memory_properties = vk.vkGetPhysicalDeviceMemoryProperties(
            physical_device)
        self._enumerate_device_extension_properties = vk.vkEnumerateDeviceExtensionProperties(
            physicalDevice=physical_device, pLayerName=None)
        if physical_device_properties_2_supported:
            vkGetPhysicalDeviceProperties2KHR = vk.vkGetInstanceProcAddr(
                instance, 'vkGetPhysicalDeviceProperties2KHR')
            self._physical_device_driver_properties = vk.VkPhysicalDeviceDriverPropertiesKHR()
            physical_device_properties2 = vk.VkPhysicalDeviceProperties2(
                pNext=self._physical_device_driver_properties)
            physical_device_properties2 = vkGetPhysicalDeviceProperties2KHR(
                physical_device, physical_device_properties2)
        vk.vkDestroyInstance(instance, None)

    @property
    def device(self):
        if self._physical_device_properties is None:
            return (None, None)

        return (self._physical_device_properties.vendorID,
                self._physical_device_properties.deviceID)

    @property
    def device_name(self):
        if self._physical_device_properties is None:
            return None

        return self._physical_device_properties.deviceName

    @cached_property
    def device_type(self):
        if self._physical_device_properties is None:
            return None

        return VulkanDeviceType(self._physical_device_properties.deviceType)

    @cached_property
    def api_version(self):
        if self._physical_device_properties is None:
            return None

        version = self._physical_device_properties.apiVersion
        major = version >> 22
        minor = (version >> 12) & 0x3ff
        patch = version & 0xfff
        return '{}.{}.{}'.format(major, minor, patch)

    @cached_property
    def driver_info(self):
        if self._physical_device_driver_properties is None:
            return None

        ffi = FFI()
        return ffi.string(
            self._physical_device_driver_properties.driverInfo).decode()

    @cached_property
    def driver_name(self):
        if self._physical_device_driver_properties is None:
            return None

        ffi = FFI()
        return ffi.string(
            self._physical_device_driver_properties.driverName).decode()

    @cached_property
    def mesa_version(self):
        if self.driver_info is None:
            return None

        m = re.search(r"Mesa (?P<version>[\w\.\d -]+)\b", self.driver_info)
        if m:
            return m.groupdict({}).get('version')

    @cached_property
    def mesa_git_version(self):
        if self.driver_info is None:
            return None

        m = re.search(r"Mesa [\w\.\d -]+ \(git-(?P<hash>[\da-z]+)\)", self.driver_info)
        if m:
            return m.groupdict({}).get('hash')

    @cached_property
    def conformance_version(self):
        if self._physical_device_driver_properties is None:
            return None

        version = self._physical_device_driver_properties.conformanceVersion

        return '{}.{}.{}.{}'.format(version.major, version.minor,
                                    version.subminor, version.patch)

    @property
    def extensions(self):
        extensions = dict()
        for e in self._enumerate_device_extension_properties or []:
            extension = VulkanExtension(name=e.extensionName,
                                        version=e.specVersion)
            extensions[extension.name] = extension
        return extensions

    @cached_property
    def heaps(self):
        if self._physical_device_memory_properties is None:
            return []

        num_heaps = self._physical_device_memory_properties.memoryHeapCount
        heaps = [VulkanHeap(size=heap.size, flags=heap.flags) for heap in
                 self._physical_device_memory_properties.memoryHeaps[0:num_heaps]]

        for mem_type in self._physical_device_memory_properties.memoryTypes[0:num_heaps]:
            heap = heaps[mem_type.heapIndex]
            heap.add_type(mem_type.propertyFlags)

        return heaps

    @cached_property
    def VRAM_heap(self):
        for heap in self.heaps:
            if heap.has_type(VulkanHeap.DEVICE_LOCAL_BIT):
                return heap
        return VulkanHeap(size=0, flags=-1)

    @cached_property
    def GTT_heap(self):
        for heap in self.heaps:
            if heap.has_type(VulkanHeap.VISIBLE_BIT | VulkanHeap.COHERENT_BIT):
                return heap
        return VulkanHeap(size=0, flags=-1)


if __name__ == '__main__':
    if info := VulkanInfo.construct():
        print("The device %s (VRAM=%.2f GiB, GTT=%.2f GiB) implements %d extensions" %
              info.device, info.VRAM_heap.GiB_size, info.GTT_heap.GiB_size, len(info.extensions))
