import sys
from PyQt5.QtWidgets import QApplication
from ui import VideoPlayer

WINDOW_TITLE = "视频格式化处理器"

def main() -> None:
    app = QApplication(sys.argv)
    video_player = VideoPlayer()
    video_player.setWindowTitle(WINDOW_TITLE)
    video_player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
