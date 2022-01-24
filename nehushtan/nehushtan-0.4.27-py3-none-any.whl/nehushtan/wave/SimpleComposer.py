import math
from typing import List

from nehushtan.wave.Note import Note
from nehushtan.wave.WaveWriter import WaveWriter


class SimpleComposer:
    def __init__(self, target_wav_file_path: str, beats_in_minute: int = 96):
        self.__wave_writer = WaveWriter(target_wav_file_path)
        self.__beats_in_minute = beats_in_minute

        self.__notes_lines = {0: []}
        # self.__note_frames_cache = []

    def add_note_to_line(self, note: Note, line_index: int = 0):
        if not self.__notes_lines.get(line_index):
            self.__notes_lines[line_index] = []
        self.__notes_lines[line_index].append(note)

    def add_notes_to_lines(self, notes: List[Note]):
        for line_index in range(len(notes)):
            self.add_note_to_line(notes[line_index], line_index)

    def __process_notes(self):
        # 每次采样代表的秒数 = 1秒 / 每秒采样次数
        step = 1.0 / self.__wave_writer.get_frame_rate()
        mixed_frames = []
        print("TO PROCESS NOTES")
        time_piece_index = 0
        for line_index, line in self.__notes_lines.items():
            line_frames = []
            for note in line:
                hz = note.get_sound_in_hz()
                beats = note.get_beats()
                # 本音占用时长 = 拍数 * (一分钟 / 每分钟拍数)
                time = beats * 60.0 / self.__beats_in_minute
                piece_count = int(round(time / step))

                for i in range(piece_count):
                    t = step * time_piece_index

                    frame = math.cos(2 * math.pi * (hz * t))
                    frame = frame * 10000  # it is like volumn

                    line_frames.append(int(frame))
                    time_piece_index += 1

            for i in range(len(line_frames)):
                frame = line_frames[i]
                if line_index == 0:
                    mixed_frames.append(frame)
                else:
                    mixed_frames[i] += frame

        print("PREPARED")

        self.__wave_writer.write_frames(mixed_frames)

    def close(self):
        self.__process_notes()
        self.__wave_writer.close()
        print("WRITTEN AND CLOSED")
