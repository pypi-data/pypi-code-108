import wave
from typing import List


class WaveWriter:
    def __init__(self, target_wav_file_path: str, number_of_channels: int = 1, sample_width_in_bytes: int = 2,
                 frame_rate: int = 44100):
        # 打开WAV文档
        self.__target_wav_file = wave.open(target_wav_file_path, "wb")
        # 配置声道数、量化位数和取样频率
        self.__number_of_channels = number_of_channels
        self.__target_wav_file.setnchannels(number_of_channels)

        self.__sample_width_in_bytes = sample_width_in_bytes
        self.__target_wav_file.setsampwidth(sample_width_in_bytes)

        self.__frame_rate = frame_rate
        self.__target_wav_file.setframerate(frame_rate)

    def get_number_of_channels(self) -> int:
        """
        声道数
        """
        return self.__number_of_channels

    def get_sample_width_in_bytes(self) -> int:
        """
        量化位数
        """
        return self.__sample_width_in_bytes

    def get_frame_rate(self) -> int:
        """
        取样频率
        """
        return self.__frame_rate

    def write_frames(self, wave_data: List[int]):
        """
        将wav_data转换为二进制数据写入文件
        记录每一个采样点的频率，给定一个int （0-65535）

        WHEN sample_width_in_bytes IS 2
            写入的目标二进制字节串为 0x10 0x27 | 0x9 0x27 | ...
            自 10000=0x2710 | 9993=0x2709 | ... 转换而来
        """

        frames_in_byte = b""
        for frame in wave_data:
            frames_in_byte += frame.to_bytes(2, byteorder="little", signed=True)

        self.__target_wav_file.writeframes(frames_in_byte)

    def __enter__(self):
        pass

    def close(self):
        self.__target_wav_file.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
