import os
import subprocess
import whisper
from PyQt5.QtCore import QThread, pyqtSignal
from typing import List, Dict, Any

class SubtitleThread(QThread):
    finished_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    TEMP_AUDIO_PATH = "temp_audio.mp3"
    SRT_PATH = "subtitles.srt"

    def __init__(self, video_path: str, model_name: str, parent: Any = None):
        super().__init__(parent)
        self.video_path = video_path
        self.model_name = model_name

    def extract_audio(self) -> str:
        command = ["ffmpeg", "-i", self.video_path, "-q:a", "0", "-map", "a", "-y", self.TEMP_AUDIO_PATH]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e}")
            return ""
        return self.TEMP_AUDIO_PATH

    def format_as_srt(self, transcription_segments: List[Dict[str, Any]]) -> str:
        srt_output = ""
        for i, segment in enumerate(transcription_segments, 1):
            start = self.format_time(segment['start'])
            end = self.format_time(segment['end'])
            text = segment['text']
            srt_output += f"{i}\n{start} --> {end}\n{text}\n\n"
        return srt_output

    def format_time(self, seconds: float) -> str:
        ms = int((seconds % 1) * 1000)
        s = int(seconds)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def run(self) -> None:
        self.progress_signal.emit(10)  # 开始提取音频
        audio_path = self.extract_audio()
        self.progress_signal.emit(30)  # 音频提取完成

        model = whisper.load_model(self.model_name)
        self.progress_signal.emit(40)  # 模型加载完成

        # 使用自定义的回调函数来获取转录进度
        result = self.transcribe_with_progress(model, audio_path)
        
        srt = self.format_as_srt(result['segments'])

        with open(self.SRT_PATH, "w", encoding="utf-8") as file:
            file.write(srt)
        
        self.progress_signal.emit(100)  # 字幕生成完成
        self.finished_signal.emit(self.SRT_PATH)

    def transcribe_with_progress(self, model: Any, audio_path: str) -> Dict[str, List[Dict[str, Any]]]:
        # 加载音频
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # 获取音频特征
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # 进行解码
        options = whisper.DecodingOptions(language="zh", task="transcribe")
        result = model.transcribe(audio_path, **options.__dict__)
        
        segments = []
        for i, segment in enumerate(result['segments']):
            segments.append(segment)
            progress = int(40 + (i + 1) / len(result['segments']) * 40)  # 40% to 80%
            self.progress_signal.emit(progress)
        
        return {"segments": segments}

    def prompt_user_correction(self, text: str) -> None:
        # 这里可以实现提示用户校正的逻辑
        print(f"请校正以下文本: {text}")

    def terminate(self):
        self.requestInterruption()
        super().terminate()
