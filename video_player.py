# video_player.py
import vlc
from typing import Any
from PyQt5.QtWidgets import QSlider

class VideoPlayer:
    def __init__(self):
        self.instance: Any = vlc.Instance()
        self.player: Any = self.instance.media_player_new()

    def play_video(self, video_path: str) -> None:
        media = self.instance.media_new(video_path)
        self.player.set_media(media)
        self.player.play()

    def set_position(self, position: float) -> None:
        self.player.set_position(position / 1000.0)

    def set_playback_milliseconds_position(self, milliseconds: int) -> None:
        if milliseconds >= 0:
            self.player.set_time(milliseconds)
            self.player.play()
        else:
            print("时间必须为非负值")

    def update_slider(self, slider: QSlider, is_slider_being_dragged: bool = False) -> None:
        if not is_slider_being_dragged:
            max_value = slider.maximum()
            current_position = self.player.get_position()
            progress_value = int(current_position * max_value)
            slider.setValue(progress_value)