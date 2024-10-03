# rich_text_editor.py
from PyQt5.QtWidgets import QTextEdit, QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox, QHBoxLayout, QToolBar, QAction, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtCore import QMimeData, Qt, QSize
from PyQt5.QtGui import QTextCursor, QTextDocument, QIcon, QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QGroupBox, QRadioButton 
from PyQt5.QtGui import QTextCursor, QTextDocument, QTextCharFormat, QColor  # 添加 QColor 导入
from bs4 import BeautifulSoup
from typing import Callable, Optional, List, Dict

class FindReplaceDialog(QDialog):
    def __init__(self, editor, replace_mode=False):
        super().__init__(editor)  # 将 editor 作为父窗口传递
        self.editor = editor
        self.replace_mode = replace_mode
        self.setWindowTitle("查找和替换" if replace_mode else "查找")
        
        # 设置为非模态并保持在最上层
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # 不调用 raise_() 和 activateWindow()，以允许主 UI 操作
        ...
        
        layout = QVBoxLayout()
        
        self.find_label = QLabel("查找内容(N):")
        self.find_input = QLineEdit()
        layout.addWidget(self.find_label)
        layout.addWidget(self.find_input)

        self.replace_label = QLabel("替换为(D):")
        self.replace_input = QLineEdit()
        layout.addWidget(self.replace_label)
        layout.addWidget(self.replace_input)

        # 方向选择
        direction_group = QGroupBox("方向")
        direction_layout = QHBoxLayout()
        self.up_radio = QRadioButton("向上(U)")
        self.down_radio = QRadioButton("向下(D)")
        self.down_radio.setChecked(True)  # 默认选择向下
        direction_layout.addWidget(self.up_radio)
        direction_layout.addWidget(self.down_radio)
        direction_group.setLayout(direction_layout)
        layout.addWidget(direction_group)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.find_button = QPushButton("查找下一个(E)")
        self.find_button.clicked.connect(self.find_text)
        button_layout.addWidget(self.find_button)
        
        self.replace_button = QPushButton("替换(R)")
        self.replace_button.clicked.connect(self.replace_text)  # 连接替换按钮
        button_layout.addWidget(self.replace_button)

        self.replace_all_button = QPushButton("全部替换(A)")
        self.replace_all_button.clicked.connect(self.replace_all_text)  # 连接全部替换按钮
        button_layout.addWidget(self.replace_all_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        # 选项
        self.case_sensitive_checkbox = QCheckBox("区分大小写(C)")
        layout.addWidget(self.case_sensitive_checkbox)
        
        self.wrap_checkbox = QCheckBox("循环(R)")
        layout.addWidget(self.wrap_checkbox)

        self.setLayout(layout)

    def find_text(self):
        text = self.find_input.text()
        direction = 'down' if self.down_radio.isChecked() else 'up'  # 获取查找方向
        case_sensitive = self.case_sensitive_checkbox.isChecked()
        wrap_around = self.wrap_checkbox.isChecked()

        if not text:
            QMessageBox.warning(self, "输入错误", "请输入查找内容。")
            return
        
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        found = self.editor.find_text(text, direction, case_sensitive)

        if not found and wrap_around:  # 如果未找到且选择了循环查找            
            cursor.movePosition(QTextCursor.Start)  # 移动到文档开头
            self.editor.setTextCursor(cursor)  # 设置光标到开头
            found = self.editor.findText(text, direction, case_sensitive)  # 从头开始查找
        if found:
            # 选中找到的文本
            cursor.setPosition(found.position())  # 设置光标到找到的文本位置
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(text))  # 选中找到的文本
            self.editor.setTextCursor(cursor)
            pass  # 不关闭对话框
        else:
            QMessageBox.warning(self, "未找到", "未找到指定文本。")
        cursor.endEditBlock()

    def replace_text(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        case_sensitive = self.case_sensitive_checkbox.isChecked()
        direction = 'down' if self.down_radio.isChecked() else 'up'  # 获取查找方向
        if not find_text:
            QMessageBox.warning(self, "输入错误", "请输入查找内容。")
            return     
                
        found = self.editor.find_text(find_text, direction, case_sensitive)
        if found:
            cursor.beginEditBlock()
            cursor = self.editor.textCursor()
            cursor.setPosition(found.position())  # 设置光标到找到的文本位置
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(find_text))  # 选中找到的文本                        
            cursor.removeSelectedText()  # 移除选中的文本
            cursor.insertText(replace_text)  # 替换找到的文本
            self.editor.setTextCursor(cursor)
            cursor.endEditBlock()
            QMessageBox.information(self, "替换成功", "已替换指定文本。")
        else:
            QMessageBox.warning(self, "未找到", "未找到指定文本。")
        
    def replace_all_text(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        case_sensitive = self.case_sensitive_checkbox.isChecked()
        direction = 'down' if self.down_radio.isChecked() else 'up'  # 获取查找方向

        if not find_text:
            QMessageBox.warning(self, "输入错误", "请输入查找内容。")
            return

        cursor = self.editor.textCursor()

        count = 0
        cursor.beginEditBlock()
        found = False
        while True:
            found = self.editor.find_text(find_text, direction, case_sensitive)
            if not found:
                break
            cursor = self.editor.textCursor()      
            cursor.setPosition(found.position())  # 设置光标到找到的文本位置
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(find_text))  # 选中找到的文本
                  
            cursor.removeSelectedText()  # 移除选中的文本
            cursor.insertText(replace_text)  # 替换找到的文本
            self.editor.setTextCursor(cursor)    
            count += 1
        cursor.endEditBlock()
        QMessageBox.information(self, "替换完成", f"已替换 {count} 个实例。")

class RichTextEditor(QTextEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.mouse_move_event_handler: Optional[Callable] = None
        self.find_dialog: Optional[FindReplaceDialog] = None
        self.replace_dialog: Optional[FindReplaceDialog] = None
        self.setStyleSheet("""
            QTextEdit {
                selection-background-color: blue;
                selection-color: white;
            }
        """)
        self.init_ui()

    def init_ui(self) -> None:
        # 创建工具栏
        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(16, 16))
        
        # 添加加载HTML动作
        loadAction = QAction(QIcon("icons/open.png"), "加载HTML", self)
        loadAction.setStatusTip("加载HTML文件")
        loadAction.triggered.connect(self.load_html)
        self.toolbar.addAction(loadAction)
        
        # 添加保存HTML动作
        saveAction = QAction(QIcon("icons/save.png"), "保存HTML", self)
        saveAction.setStatusTip("保存HTML文件")
        saveAction.triggered.connect(self.save_html)
        self.toolbar.addAction(saveAction)
        
        # 将工具栏添加到编辑器的顶部
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        self.setAcceptRichText(True)  # 启用富文本格式
        layout.addWidget(self)
        
    def load_html(self) -> None:
        # 从本地文件读取上一次打开的目录
        try:
            with open('last_directory.txt', 'r') as f:
                last_directory = f.read().strip()
        except FileNotFoundError:
            last_directory = ''  # 如果文件不存在，则使用空字符串

        filename, _ = QFileDialog.getOpenFileName(self, "打开HTML文件", last_directory, "HTML Files (*.html *.htm)")
        if filename:
            with open(filename, "r", encoding="utf-8") as file:
                self.setHtml(file.read())

    def save_html(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "保存HTML文件", "", "HTML Files (*.html)")
        if filename:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(self.toHtml())

    def set_mouse_move_event(self, handler: Callable) -> None:
        self.mouseMoveEvent = handler

    def copy_rich_text(self) -> None:
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return

        mimeData = QMimeData()
        mimeData.setHtml(cursor.selection().toHtml())
        QApplication.clipboard().setMimeData(mimeData)

    def mouse_move_event(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)  # 调用父类的 mouseMoveEvent
        if self.mouse_move_event_handler:  # 如果有设置的处理器，则调用
            self.mouse_move_event_handler(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
            self.open_find_dialog()
        elif event.key() == Qt.Key_H and event.modifiers() == Qt.ControlModifier:
            self.open_replace_dialog()
        else:
            super().keyPressEvent(event)

    def open_find_dialog(self) -> None:
        if self.find_dialog is None:  # 如果对话框尚未创建
            self.find_dialog = FindReplaceDialog(self)
        self.find_dialog.show()  # 显示对话框

    def open_replace_dialog(self) -> None:
        if self.replace_dialog is None:  # 如果对话框尚未创建
            self.replace_dialog = FindReplaceDialog(self, replace_mode=True)
        self.replace_dialog.show()  # 显示对话框

    def find_text(self, text: str, direction: str = 'down', case_sensitive: bool = False) -> bool:
        cursor = self.textCursor()
        found = False

        # 获取文档
        document = self.document()

        flags = QTextDocument.FindFlags()
        if direction == 'up':
            flags |= QTextDocument.FindBackward
        found = document.find(text, cursor, flags)
        if not found.isNull():  # 检查是否找到有效文本            
            self.setTextCursor(cursor)      
        else:
            found = False
        return found  # 返回是否找到文本
    
    def extract_text_and_images(self) -> List[Dict[str, str]]:
        html_content = self.toHtml()
        soup = BeautifulSoup(html_content, 'html.parser')

        segments = []
        current_text = ''  # 用于累积当前段落的文本

        for p_element in soup.find_all('p'):
            # 检查 <p> 标签内是否有 <span>，如果有则提取文本
            span_elements = p_element.find_all('span')
            for span in span_elements:
                current_text += span.get_text() + '\n'

            # 检查 <p> 标签内是否有 <img>，如果有则提取图片
            img_elements = p_element.find_all('img')
            for img in img_elements:
                # 遇到图片时，先添加累积的文本（如果有）
                if current_text:
                    segments.append({'type': 'text', 'content': current_text.strip()})
                    current_text = ''  # 重置文本累积

                # 然后添加图片的 HTML
                image_html = str(img)  # 或使用 img.prettify()
                segments.append({'type': 'image', 'content': f"<p>{image_html}</p>"})

         # 不要忘记添加最后一个累积的文本段落（如果有）
        if current_text:
            segments.append({'type': 'text', 'content': current_text.strip()})
        return segments