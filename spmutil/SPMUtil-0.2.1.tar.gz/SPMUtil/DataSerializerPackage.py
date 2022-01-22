import json
import lzma
import os
import threading

import SPMUtil as spmu


class DataSerializerPackage:

    def __init__(self, path, custom_ext=".xzp"):
        self.path = path
        self._ext = custom_ext
        self.dataSerializers = {}
        self.JsonEncoder = spmu.NdarrayEncoder
        self.JsonDecoder = spmu.NdarrayDecoder
        self._is_in_task = False

    @property
    def datas_name_list(self) -> list:
        return list(self.dataSerializers.keys())


    def get_dataSerializer(self, key) -> spmu.DataSerializer:
        if type(key) == bytes:
            key = key.decode()
        if key in self.dataSerializers:
            return self.dataSerializers[key]
        else:
            raise ValueError("Wrong key: " + key)


    def add_data_serializer(self, data_serializer:spmu.DataSerializer, overwrite=False, save=False):
        fileName = os.path.basename(data_serializer.path).split('.')[0]
        if fileName in self.dataSerializers:
            if overwrite:
                self.dataSerializers.pop(fileName)
                self.dataSerializers[fileName] = data_serializer
        else:
            self.dataSerializers[fileName] = data_serializer

        if save:
            self.save()


    def remove_data_serializer(self, data_serializer:spmu.DataSerializer, save=False):
        fileName = os.path.basename(data_serializer.path).split('.')[0]
        if fileName in self.dataSerializers:
            self.dataSerializers.pop(fileName)
        if save:
            self.save()


    def save(self, enable_multi_thread=False):
        if self._is_in_task:
            print("Save Command disposed: this class is running another task")
        if enable_multi_thread:
            self._is_in_task = True
            thread = threading.Thread(target=self._save_task(), args=())
            thread.start()
        else:
            self._save_task()



    def save_from_folder(self, folder_path, file_ext=".pkl", enable_multi_thread=False):
        files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
        for fileName in files:
            extension = os.path.splitext(fileName)[1]
            if extension == file_ext:
                dataSerializer = spmu.DataSerializer(os.path.join(folder_path, fileName))
                dataSerializer.load()
                self.add_data_serializer(dataSerializer)

        self.save(enable_multi_thread)

    def extract_to_folder(self, folder_path):
        for key in self.dataSerializers.keys():
            self.dataSerializers[key].path = os.path.join(folder_path, self.dataSerializers[key].path)
            self.dataSerializers[key].save()


    def load(self, enable_multi_thread=False):
        if self._is_in_task:
            print("Load Command disposed: this class is running another task")
        if enable_multi_thread:
            self._is_in_task = True
            thread = threading.Thread(target=self._load_task(), args=())
            thread.start()
        else:
            self._load_task()




    def _save_task(self):
        print("DataSerializerPacgkage: save begin...(it will take a lot of time)")
        data_dict = {}
        for it in self.dataSerializers.keys():
            data_dict[it] = self.dataSerializers[it].data_dict
        bytes_data = json.dumps(data_dict, indent=2, cls=self.JsonEncoder).encode('utf-8')
        filename, file_extension = os.path.splitext(self.path)
        with lzma.open(filename + self._ext, "wb") as f:
            f.write(lzma.compress(bytes_data))
            f.flush()
            print("save to", filename + self._ext)

        self._is_in_task = False


    def _load_task(self):
        filename, file_extension = os.path.splitext(self.path)
        if file_extension != self._ext:
            filename = self.path
        with lzma.open(filename + self._ext, 'rb') as f:
            print("DataSerializerPacgkage: load begin...")
            datas = json.loads(lzma.decompress(f.read()), cls=self.JsonDecoder)
            for it in datas.keys():
                dataSerializer = spmu.DataSerializer(path=it)
                dataSerializer.data_dict = datas[it]
                self.add_data_serializer(dataSerializer, overwrite=True)

        self._is_in_task = False

