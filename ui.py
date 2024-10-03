# ui.py
from PyQt5.QtCore import (QByteArray, QBuffer, QIODevice, QMimeData, QSize, QTimer, Qt, pyqtSignal, 
                          QThread, QMetaObject, Q_ARG, pyqtSlot, QPoint, QRect)  # 添加这一行以导入 QRect
from PyQt5.QtGui import (QColor, QClipboard, QImage, QIcon, QPainter, QPixmap, QTextCharFormat, QTextCursor, QBrush, QFont)
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, 
                             QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QProgressDialog, QSlider, 
                             QTextEdit, QVBoxLayout, QWidget, QFileDialog, QComboBox, QGroupBox, 
                             QSplitter, QFrame)

from video_player import VideoPlayer as VLCVideoPlayer
from rich_text_editor import RichTextEditor
from optimized_text_window import OptimizedTextWindow
from subtitles import SubtitleThread
from text_optimization import TextOptimizer
from utils import parse_srt_time_range, convert_srt_time_to_milliseconds
from bs4 import BeautifulSoup
import re
import os
import fitz
from io import BytesIO
import base64
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from typing import Callable, Optional

class VideoPlayer(QMainWindow):
    progress_dialog_closed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.video_player = VLCVideoPlayer()
        self.init_ui()
        
        # 设置复读按钮为浮动窗口
        self.repeat_button.setAttribute(Qt.WA_TranslucentBackground)
        self.repeat_button.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.Tool)

    def init_ui(self):
        self.setWindowTitle('视频格式化处理器')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }            
            
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # 左侧布局
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        video_group = QGroupBox("视频控制")
        video_layout = QVBoxLayout(video_group)
        
        self.load_video_button = self.create_button("加载演示视频", self.load_video, "icons/load_video.png")
        video_layout.addWidget(self.load_video_button)

        self.video_frame = QFrame(self)
        self.video_frame.setMinimumHeight(300)
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_player.player.set_hwnd(self.video_frame.winId())
        video_layout.addWidget(self.video_frame)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.sliderReleased.connect(self.slider_released)
        self.slider.sliderMoved.connect(self.set_position)
        video_layout.addWidget(self.slider)

        control_layout = QHBoxLayout()
        self.play_button = self.create_button("播放", self.video_player.player.play, "icons/play.png")
        self.pause_button = self.create_button("暂停", self.video_player.player.pause, "icons/pause.png")
        self.stop_button = self.create_button("停止", self.video_player.player.stop, "icons/stop.png")
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        video_layout.addLayout(control_layout)

        left_layout.addWidget(video_group)

        subtitle_group = QGroupBox("字幕生成")
        subtitle_layout = QVBoxLayout(subtitle_group)

        model_layout = QHBoxLayout()
        model_label = QLabel("Whisper 模型:")
        self.model_combo_box = QComboBox()
        self.model_combo_box.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo_box.setCurrentText("small")  # 默认选择 small 模型
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo_box)
        subtitle_layout.addLayout(model_layout)

        self.generate_subtitles_button = self.create_button("生成字幕", self.generate_subtitles, "icons/subtitles.png")
        subtitle_layout.addWidget(self.generate_subtitles_button)
        left_layout.addWidget(subtitle_group)

        pdf_group = QGroupBox("PDF控制")
        pdf_layout = QVBoxLayout(pdf_group)
        self.load_pdf_button = self.create_button("加载演示PDF", self.load_pdf, "icons/load_pdf.png")
        pdf_layout.addWidget(self.load_pdf_button)
        self.pdf_list_widget = QListWidget()
        self.pdf_list_widget.setVisible(False)
        self.pdf_list_widget.itemDoubleClicked.connect(self.insert_image)
        pdf_layout.addWidget(self.pdf_list_widget)
        left_layout.addWidget(pdf_group)

        # 右侧布局
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        editor_group = QGroupBox("文本编辑")
        editor_layout = QVBoxLayout(editor_group)
        
        self.text_edit = RichTextEditor(self)        
        self.text_edit.set_mouse_move_event(self.mouseMoveEvent)  # 设置鼠标移动事件
        editor_layout.addWidget(self.text_edit)  # 添加到布局中
        
        self.repeat_button = QPushButton('重播', self)
        self.repeat_button.setVisible(False)
        self.repeat_button.clicked.connect(self.repeat_current_line)
        editor_layout.addWidget(self.repeat_button)  # 添加到布局中
        
        right_layout.addWidget(editor_group)

        
        
        optimization_group = QGroupBox("文本优化")
        optimization_layout = QVBoxLayout(optimization_group)
        
        # 加载环境变量
        load_dotenv()

        api_layout = QHBoxLayout()
        self.api_provider_combo = QComboBox(self)
        self.api_provider_combo.addItems(["OpenAI", "Groq", "Claude"])
        self.api_provider_combo.currentTextChanged.connect(self.on_api_provider_changed)
        api_layout.addWidget(QLabel("API提供商:"))
        api_layout.addWidget(self.api_provider_combo)
        
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("输入API密钥")
        api_layout.addWidget(QLabel("API密钥:"))
        api_layout.addWidget(self.api_key_input)
        
        optimization_layout.addLayout(api_layout)
        
        self.optimize_button = self.create_button("书面化", self.optimize_text, "icons/optimize.png")
        optimization_layout.addWidget(self.optimize_button)
        
        right_layout.addWidget(optimization_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_subtitles)
        self.timer.start(100)

        self.last_highlighted_line = -1
        self.is_slider_being_dragged = False

        self.model_combo_box.setToolTip(
            "tiny: 最快,质量最低\n"
            "base: 快速,质量一般\n"
            "small: 平衡速度和质量\n"
            "medium: 较慢,质量较高\n"
            "large: 最慢,质量最高"
        )

        self.statusBar()  # 创建状态栏

        # 初始化时加载默认API提供商的密钥
        default_provider = self.api_provider_combo.currentText()
        self.load_api_key(default_provider)

    def create_button(self, text: str, callback: Callable, icon_path: Optional[str] = None) -> QPushButton:
        button = QPushButton(text, self)
        if icon_path:
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(24, 24))
        button.clicked.connect(callback)
        return button

    def optimize_text(self):
        api_key = self.api_key_input.text()
        api_provider = self.api_provider_combo.currentText()
        if api_key == '':
            QMessageBox.information(self, "Info", "API is ")
            return
        
        segments = self.text_edit.extract_text_and_images()

        self.text_optimizer = TextOptimizer(api_key, api_provider)
        self.text_optimizer.optimization_finished.connect(self.on_progress_dialog_closed)
        self.text_optimizer.optimize_text(segments)

    @pyqtSlot(str)
    def on_progress_dialog_closed(self, optimized_text):
        self.optimized_window = OptimizedTextWindow(optimized_text)
        self.optimized_window.show()

    def slider_pressed(self):
        self.is_slider_being_dragged = True

    def slider_released(self):
        new_position = self.slider.value() / self.slider.maximum()
        self.video_player.setPosition(new_position)
        self.is_slider_being_dragged = False        

    def set_position(self, position):
        self.video_player.setPosition(position)

    def update_slider(self):
        self.video_player.updateSlider(self.slider, self.is_slider_being_dragged)  

    def load_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4)")
        if video_path:
            self.video_path = video_path
            self.video_player.play_video(video_path)

    def generate_subtitles(self):
        if hasattr(self, 'video_path'):
            # 创建并显示进度对话框
            self.progress_dialog = QProgressDialog("正在生成字幕...", "取消", 0, 100, self)
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setWindowTitle("生成字幕")
            self.progress_dialog.setValue(0)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setAutoReset(False)
            self.progress_dialog.canceled.connect(self.cancel_subtitle_generation)
            self.progress_dialog.show()

            selected_model = self.model_combo_box.currentText()
            self.subtitle_thread = SubtitleThread(self.video_path, selected_model)
            self.subtitle_thread.progress_signal.connect(self.update_subtitle_progress)
            self.subtitle_thread.finished_signal.connect(self.on_subtitle_thread_finished)
            self.subtitle_thread.start()

    def cancel_subtitle_generation(self):
        if hasattr(self, 'subtitle_thread') and self.subtitle_thread.isRunning():
            self.subtitle_thread.terminate()
            self.subtitle_thread.wait()
        if self.progress_dialog:
            self.progress_dialog.close()

    def update_subtitle_progress(self, progress):
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)

    def on_subtitle_thread_finished(self, srt_path):
        if self.progress_dialog:
            self.progress_dialog.close()
        self.load_srt(srt_path)
        self.video_player.play_video(self.video_path)

    def insert_image(self, item):
        list_widget = item.listWidget()
        row = list_widget.row(item)
        pixmap = self.pdf_images[row]

        cursor = self.text_edit.textCursor()
        image = pixmap.toImage()
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        base64_data = byte_array.toBase64().data()

        cursor.insertImage(pixmap.toImage(), "data:image/png;base64,{}".format(str(base64_data, encoding='utf-8')))
        self.text_edit.setTextCursor(cursor)

    def load_srt(self, srt_path):
        with open(srt_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        self.text_edit.setText("".join(lines))

    def clear_highlight(self):
        cursor = QTextCursor(self.text_edit.document())
        cursor.select(QTextCursor.Document)
        fmt = QTextCharFormat()
        fmt.setBackground(QBrush(QColor("white")))
        cursor.mergeCharFormat(fmt)

    def highlight_text(self, line_number):
        if line_number == self.last_highlighted_line:
            return
        self.clear_highlight()

        fmt = QTextCharFormat()
        fmt.setBackground(QBrush(QColor("yellow")))

        cursor = QTextCursor(self.text_edit.document())
        block = cursor.block()

        for _ in range(line_number):
            block = block.next()

        cursor.setPosition(block.position())
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.mergeCharFormat(fmt)

        self.last_highlighted_line = line_number

    def update_subtitles(self):
        current_time = self.video_player.player.get_time()
        self.yellow_line(current_time)

    def yellow_line(self, current_time):
        text = self.text_edit.toPlainText()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if '-->' in line:
                time_range = line
                start_time, end_time = parse_srt_time_range(time_range)
                if start_time <= current_time <= end_time:
                    self.highlight_text(i + 1)  # 高亮时间所在行的下一行文本
                    break

    def load_pdf(self):
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if pdf_path:
            self.display_pdf(pdf_path)

    def display_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        self.pdf_images = []
        self.pdf_list_widget.clear()
        self.pdf_list_widget.setVisible(True)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = QPixmap.fromImage(QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888))
            self.pdf_images.append(img)

            scaled_img = img.scaled(pix.width // 2, pix.height // 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            item = QListWidgetItem()
            item.setSizeHint(scaled_img.size())

            label = QLabel()
            label.setPixmap(scaled_img)
            self.pdf_list_widget.addItem(item)
            self.pdf_list_widget.setItemWidget(item, label)

    def mouseMoveEvent(self, event):
        cursor = self.text_edit.cursorForPosition(event.pos())
        line_number = cursor.blockNumber()
        self.update_repeat_button(line_number)

    def update_repeat_button(self, line_number):
        text = self.text_edit.toPlainText()
        lines = text.split('\n')

        # 检查当前行、上一行和下一行是否包含 '-->'
        if line_number < len(lines):
            if '-->' in lines[line_number]:  # 检查当前行
                self.current_line_number = line_number  # 设置当前行号
            elif line_number > 0 and '-->' in lines[line_number - 1]:  # 检查上一行
                self.current_line_number = line_number - 1  # 设置当前行号为上一行
            elif line_number < len(lines) - 1 and '-->' in lines[line_number + 1]:  # 检查下一行
                self.current_line_number = line_number + 1  # 设置当前行号为下一行
            else:
                self.repeat_button.setVisible(False)  # 如果不包含 '-->'，隐藏按钮
                return  # 直接返回，避免后续代码执行

            self.repeat_button.setVisible(True)  # 显示复读按钮

            # 创建一个新的光标，不改变当前光标位置
            cursor = QTextCursor(self.text_edit.document())
            cursor.movePosition(cursor.Start)  # 移动到文档开始
            for _ in range(self.current_line_number):
                cursor.movePosition(cursor.NextBlock)  # 移动到目标行
            cursor.movePosition(cursor.EndOfBlock)  # 移动到当前行的行尾
            rect_current = self.text_edit.cursorRect(cursor)  # 当前行的矩形区域
            
            # 获取下一行的矩形区域
            if self.current_line_number < len(lines) - 1:
                cursor.movePosition(cursor.NextBlock)  # 移动到下一行
                cursor.movePosition(cursor.EndOfBlock)  # 移动到当前行的行尾
                rect_next = self.text_edit.cursorRect(cursor)  # 下一行的矩形区域
            else:
                rect_next = QRect()  # 如果没有下一行，设置为空矩形
            
            # 计算最大宽度
            max_x = max(rect_current.right(), rect_next.right()) + 5
            # 移动按钮到最大宽度的右侧
            self.repeat_button.move(self.text_edit.mapToGlobal(QPoint(max_x, rect_current.top() )))
            self.repeat_button.setFixedWidth(100)  # 设置按钮宽度为100
        else:
            self.repeat_button.setVisible(False)  # 行号超出范围，隐藏按钮

    def repeat_current_line(self):
        text = self.text_edit.toPlainText()
        lines = text.split('\n')
        if self.current_line_number < len(lines):
            time_range = lines[self.current_line_number]
            start_time, end_time = parse_srt_time_range(time_range)
            self.video_player.set_playback_milliseconds_position(start_time + 1)  # 设置播放位置为起始时间
            
            # 禁用复读按钮
            self.repeat_button.setEnabled(False)
            
            # 播放完成后暂停并重新启用按钮
            QTimer.singleShot((end_time - start_time), self.on_playback_finished)  # 播放完成后调用回调

    def on_playback_finished(self):
        self.video_player.player.pause()  # 暂停视频播放
        self.repeat_button.setEnabled(True)  # 重新启用复读按钮

    def on_api_provider_changed(self, provider):
        self.load_api_key(provider)

    def load_api_key(self, provider):
        if provider == "OpenAI":
            api_key = os.getenv("OPENAI_API_KEY", "")
        elif provider == "Groq":
            api_key = os.getenv("GROQ_API_KEY", "")
        elif provider == "Claude":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
        else:
            api_key = ""

        self.api_key_input.setText(api_key)

    
    