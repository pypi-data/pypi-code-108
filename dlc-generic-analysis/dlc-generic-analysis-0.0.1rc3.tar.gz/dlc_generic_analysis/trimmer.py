import logging
import multiprocessing
import os
from qtpy import QtWidgets, QtCore, QtMultimedia, QtMultimediaWidgets
from qtpy.QtCore import Qt
from .gui_objects import PlayPause
from typing import List, Tuple
from moviepy.editor import VideoFileClip


def _trim_pool(args: Tuple[str, float, float]) -> None:
    """
    trims a file and writes it to a new file with "_trimmed" appended to the end
    :param args: A tuple of (str, float, float) where str is the video path, the first float is the
    start of the trim region and the second float is the end of the trim region
    :return: None
    """
    clip = VideoFileClip(args[0])
    clip.cutout(args[1] / 1000, args[2] / 1000)
    fname, ext = os.path.splitext(args[0])
    outfile = fname + "_trimmed" + ext
    clip.write_videofile(outfile)


class GoToTime(QtWidgets.QHBoxLayout):
    def __init__(self, text: str = "", time: float = 0):
        """
        A button that says go to with an editable label
        :param text: the text of the label
        :param time: the initial time value
        """
        super(GoToTime, self).__init__()
        self.text = text
        self.setContentsMargins(0, 0, 0, 0)
        if text != "":
            self.label = QtWidgets.QLabel(f"{text} {round(time, 2)}")
        else:
            self.label = QtWidgets.QLabel("")
        self.addWidget(self.label)
        self.goto_button = QtWidgets.QPushButton("Go To")
        self.addWidget(self.goto_button)

    def update_label(self, time):
        self.label.setText(f"{self.text} {round(time, 2)}")


class Trimmer(QtWidgets.QWidget):
    keyPressed = QtCore.Signal(int)

    def __init__(self, video_paths: List[str]):
        """
        Creates a window that assists the user in trimming the ends off a list of videos
        """
        super(Trimmer, self).__init__()
        self.setWindowTitle("Trim Video(s)")
        self.setLayout(QtWidgets.QVBoxLayout())
        self.video_loaded = False
        self.video_playing = False
        self.video_paths = video_paths
        self.current_video_index = 0
        self.top_ui = QtWidgets.QVBoxLayout()
        self.top_ui.setContentsMargins(0, 0, 0, 0)
        self.videos_navigate = QtWidgets.QHBoxLayout()
        self.previous_video_button = QtWidgets.QPushButton("Previous Video")
        self.previous_video_button.clicked.connect(self._on_click_previous_video)
        self.previous_video_button.setDisabled(True)
        self.videos_navigate.addWidget(self.previous_video_button)
        self.next_video_button = QtWidgets.QPushButton("Next Video")
        if len(self.video_paths) < 2:
            self.next_video_button.setDisabled(True)
        self.next_video_button.clicked.connect(self._on_click_next_video)
        self.videos_navigate.addWidget(self.next_video_button)
        self.filename_label = QtWidgets.QLabel()
        self.filename_label.setMargin(0)
        self.videos_navigate.setContentsMargins(0, 0, 0, 0)
        self.top_ui.addLayout(self.videos_navigate)
        self.top_ui.setContentsMargins(0, 0, 0, 0)
        self.video_viewer = QtMultimediaWidgets.QVideoWidget()
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMuted(True)
        self.trim_start = [0] * len(
            self.video_paths
        )  # the beginning point for the trim in milliseconds
        self.trim_end = [0] * len(self.video_paths)  # the end point for the trim in milliseconds
        self.play_pause = PlayPause()
        self.play_pause.fast_reverse_button.clicked.connect(self._on_click_fast_reverse)
        self.play_pause.play_pause_button.clicked.connect(self.on_click_play_pause)
        self.play_pause.fast_forward_button.clicked.connect(self._on_click_fast_forward)
        self.trim_buttons = QtWidgets.QHBoxLayout()
        self.trim_buttons.setContentsMargins(0, 0, 0, 0)
        self.trim_start_button = QtWidgets.QPushButton("Trim Start")
        self.trim_start_button.clicked.connect(self._on_click_trim_start)
        self.trim_buttons.addWidget(self.trim_start_button)
        self.trim_end_button = QtWidgets.QPushButton("Trim End")
        self.trim_end_button.clicked.connect(self._on_click_trim_end)
        self.trim_buttons.addWidget(self.trim_end_button)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self._on_slider_move)
        self.goto_start = GoToTime("Start Time")
        self.goto_start.goto_button.clicked.connect(self._on_goto_start)
        self.goto_end = GoToTime("End Time")
        self.goto_end.goto_button.clicked.connect(self._on_goto_end)
        self.subclip_duration_label = QtWidgets.QLabel(f"Sub-clip Duration {0}")
        self.finish_buttom = QtWidgets.QPushButton("Finish")
        self.finish_buttom.clicked.connect(self._on_click_finish)
        self.trim_control = QtWidgets.QGridLayout()
        self.trim_control.setContentsMargins(0, 0, 0, 0)
        x, y = 0, 0
        self.trim_control.addLayout(self.play_pause, 0, 0)
        self.trim_control.addLayout(self.trim_buttons, 0, 2)
        y = 0
        x += 1
        self.trim_control.addWidget(self.slider, x, y, x, -1)
        y = 0
        x += 1
        self.trim_control.addLayout(self.goto_start, x, y)
        y += 1
        self.trim_control.addLayout(self.goto_end, x, y)
        y += 1
        self.trim_control.addWidget(self.subclip_duration_label, x, y)
        y += 1
        self.trim_control.addWidget(self.finish_buttom, x, y)
        self.layout().addLayout(self.top_ui)
        self.layout().addWidget(self.video_viewer)
        self.layout().addLayout(self.trim_control)
        self.player.setVideoOutput(self.video_viewer)
        self.player.stateChanged.connect(self._state_changed)
        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self._load_video(self.video_paths[self.current_video_index])

    def _load_video(self, path):
        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
        self.filename_label.setText(os.path.split(path)[1])
        self.filename_label.resize(self.filename_label.sizeHint())
        self.trim_end[self.current_video_index] = self.player.duration()
        self._update_subclip_duration()

    def _on_click_previous_video(self, e):
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self._load_video(self.video_paths[self.current_video_index])
            if self.current_video_index == 0:
                self.previous_video_button.setEnabled(False)
            if self.current_video_index < len(self.video_paths) - 1:
                self.next_video_button.setEnabled(True)

    def _on_click_next_video(self, e):
        if self.current_video_index < len(self.video_paths) - 1:
            self.current_video_index += 1
            self._load_video(self.video_paths[self.current_video_index])
            if self.current_video_index > 0:
                self.previous_video_button.setEnabled(True)
            if self.current_video_index == len(self.video_paths) - 1:
                self.next_video_button.setEnabled(False)

    def on_click_play_pause(self):
        logging.info(f"state = {self.player.state()}")
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
            logging.info("pause")
        else:
            self.player.play()
            logging.info("play")

    def _on_click_fast_forward(self):
        if self.player.state() != QtMultimedia.QMediaPlayer.StoppedState:
            self.player.setPosition(self.player.position() + 1000)

    def _on_click_fast_reverse(self):
        if self.player.state() != QtMultimedia.QMediaPlayer.StoppedState:
            self.player.setPosition(self.player.position() - 1000)

    def _on_slider_move(self, position):
        self.player.setPosition(position)

    def _on_click_trim_start(self, e):
        logging.info(f"current position {self.player.position()}")
        self.trim_start[self.current_video_index] = self.player.position()
        self.goto_start.update_label(self.trim_start[self.current_video_index] / 1000)

        if self.trim_end[self.current_video_index] < self.trim_start[self.current_video_index]:
            self.trim_end[self.current_video_index] = self.trim_start[self.current_video_index]
        self._update_subclip_duration()

    def _on_click_trim_end(self, e):
        self.trim_end[self.current_video_index] = self.player.position()
        logging.info(f"current position {self.trim_end[self.current_video_index] }")

        self.goto_end.update_label(self.trim_end[self.current_video_index] / 1000)
        if self.trim_start > self.trim_end:
            self.trim_start = self.trim_end
        self._update_subclip_duration()

    def _update_subclip_duration(self):
        subclip_duration = round(
            self.trim_end[self.current_video_index] / 1000
            - self.trim_start[self.current_video_index] / 1000,
            1,
        )
        logging.info(f"subclip_duration {subclip_duration}")
        self.subclip_duration_label.setText(f"Sub-clip Duration {subclip_duration}")

    def _on_close(self, e):
        self.loop.quit()
        self.destroy()

    def _state_changed(self, e):
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.play_pause.play_pause_button.setIcon(self.play_pause.pause_icon)
        else:
            self.play_pause.play_pause_button.setIcon(self.play_pause.play_icon)

    def _position_changed(self, position):
        self.slider.setValue(position)

    def _duration_changed(self, length):
        self.slider.setRange(0, length)

    def _keyPressEvent(self, e) -> None:
        key = e.key
        if key == Qt.Key_Space:
            self.on_click_play_pause()
        if key == Qt.Key_Forward:
            self._on_click_fast_forward()
        if key == Qt.Key_Back:
            self._on_click_fast_reverse()

    def _on_goto_start(self, e):
        self.player.setPosition(self.trim_start[self.current_video_index])

    def _on_goto_end(self, e):
        self.player.setPosition(self.trim_end[self.current_video_index])

    def _on_click_finish(self, e):
        args = zip(self.video_paths, self.trim_start, self.trim_end)
        with multiprocessing.Pool() as pool:
            pool.imap_unordered(_trim_pool, args)
        logging.info("done")
