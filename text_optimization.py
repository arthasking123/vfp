import re
import threading
from PyQt5.QtCore import QObject, pyqtSignal, QMetaObject, Qt, Q_ARG, pyqtSlot
from PyQt5.QtWidgets import QProgressDialog, QMessageBox, QApplication
from bs4 import BeautifulSoup
from langchain_openai import OpenAI
from langchain_anthropic import Anthropic
from langchain_groq import ChatGroq
from groq import Groq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import langchain
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, Runnable, RunnableConfig
from langchain_community.cache import InMemoryCache
from typing import Any, Dict, Optional, List


class CustomInMemoryCache(InMemoryCache):
    def __init__(self):
        super().__init__()
        self.summaries = []

    def lookup(self, prompt: str, llm_string: str) -> Any:
        return super().lookup(prompt, llm_string)

    def update(self, prompt: str, llm_string: str, return_val: Any) -> None:
        super().update(prompt, llm_string, return_val)
        if "生成摘要" in prompt:
            self.summaries.append(return_val)

    def clear(self) -> None:
        super().clear()
        self.summaries = []

class TextOptimizer(QObject):
    progress_updated = pyqtSignal(int)
    optimization_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key: str, api_provider: str):
        super().__init__()
        self.api_key = api_key
        self.api_provider = api_provider
        self.progress_dialog = None
        self.is_cancelled = False

        # 初始化缓存
        langchain.llm_cache = InMemoryCache()

        # 根据用户选择的API类型初始化LLM
        if self.api_provider == "OpenAI":
            self.llm = OpenAI(api_key=self.api_key, model="gpt-3.5-turbo")
        elif self.api_provider == "Anthropic":
            self.llm = Anthropic(api_key=self.api_key, model="claude-2")
        elif self.api_provider == "Groq":
            self.llm = ChatGroq(api_key=self.api_key, model="mixtral-8x7b-32768")
        else:
            raise ValueError(f"不支持的API提供商: {self.api_provider}")

        # 定义优化文本的提示模板
        self.optimize_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            将以下口语化表述整理成连贯性的技术文章段落。要求如下：
            1.逻辑结构清晰 
            2.不要扩写句子，不要改变文本原意，按顺序仅把口语化的表述书面化 
            3.使用中文语言 
            4.遇到问句不要回答问题，保留原始文本 
            5.数字要精确 
            6.不要丢失信息

            文本：
            {text}

            优化后的文本：
            """
        )

        # 定义生成摘要的提示模板
        self.summary_prompt = PromptTemplate(
            input_variables=["optimized_text"],
            template="""
            请基于原文生成一个简短的摘要，突出其中的主要观点和关键信息。
            请用中文回答，控制在200字以内。

            文本：
            {optimized_text}

            摘要：
            """
        )

        # 定义生成导读的提示模板
        self.intro_prompt = PromptTemplate(
            input_variables=["summaries"],
            template="""
            请根据以下文章摘要生成一段简洁的导读文本。导读应基于文章内容，包括以下几个方面：
            1. 问题背景：文章要解决的主要问题或挑战
            2. 所做的工作：为解决问题采取的主要措施或开发的系统
            3. 取得的成效：实施措施或系统后取得的主要成果

            请用中文回答，控制在200字以内。

            文章摘要：
            {summaries}

            导读：
            """
        )

        # 创建优化和摘要的链
        self.optimize_chain = self.optimize_prompt | self.llm | StrOutputParser()
        self.summary_chain = self.summary_prompt | self.llm | StrOutputParser()

    def optimize_text(self, segments: List[Dict[str, Any]]) -> None:
        self.is_cancelled = False
        self.progress_dialog = QProgressDialog("正在优化文本...", "取消", 0, 100)
        self.progress_dialog.setWindowModality(Qt.WindowModal)        
        self.progress_dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.progress_dialog.canceled.connect(self.cancel_optimization)
        self.progress_updated.connect(self.progress_dialog.setValue)
        self.error_occurred.connect(self.show_error_and_close_dialog)
        self.progress_dialog.show()
        

        threading.Thread(target=self._optimize_text_thread, args=(segments,), daemon=True).start()

    def cancel_optimization(self) -> None:
        self.is_cancelled = True

    def _optimize_text_thread(self, segments: List[Dict[str, Any]]) -> None:
        try:
            optimized_segments = []
            summaries = []
            for i, segment in enumerate(segments):
                if self.is_cancelled:
                    QMetaObject.invokeMethod(self.progress_dialog, "close", Qt.QueuedConnection)
                    return

                print(segment)
                if segment['type'] == 'text':
                    text_to_optimize = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', segment['content'])
                    
                    # 优化文本
                    optimized_text = self.optimize_chain.invoke({"text": text_to_optimize})
                    optimized_segments.append(optimized_text.strip())
                    
                    # 生成摘要
                    summary = self.summary_chain.invoke({"optimized_text": optimized_text})
                    summaries.append(summary)
                    
                elif segment['type'] == 'image':
                    optimized_segments.append(segment['content'])

                # 更新进度
                progress = min(99, int(100 * (i + 1) / len(segments)))
                self.progress_updated.emit(progress)

            if self.is_cancelled:
                QMetaObject.invokeMethod(self.progress_dialog, "close", Qt.QueuedConnection)
                return

            # 生成文章导读
            all_summaries = "\n".join(summaries)
            intro = self.generate_intro(all_summaries)
            
            # 将导读放在优化后的文本之前
            final_content = f"导读：\n{intro}\n\n" + "\n\n".join(optimized_segments)

            self.optimization_finished.emit(final_content)
            QMetaObject.invokeMethod(self.progress_dialog, "close", Qt.QueuedConnection)
        except Exception as e:
            self.error_occurred.emit(str(e))

    @pyqtSlot(str)
    def show_error_and_close_dialog(self, error_message: str) -> None:
        QMessageBox.critical(None, "错误", f"优化过程中发生错误:\n{error_message}")
        if self.progress_dialog:
            self.progress_dialog.close()
    def generate_intro(self, summaries: str) -> str:
        intro_chain = self.intro_prompt | self.llm | StrOutputParser()
        return intro_chain.invoke({"summaries": summaries})