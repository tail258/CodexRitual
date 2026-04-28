import importlib
from PyQt6.QtCore import QThread, pyqtSignal

import importlib
import os
import httpx
from PyQt6.QtCore import QThread, pyqtSignal

class AITaskWorker(QThread):
    signal_finished = pyqtSignal(str)
    signal_error = pyqtSignal(str)

    # 【接收新参数：base_url 和 model_name】
    def __init__(self, provider_type: str, api_key: str, base_url: str, model_name: str, context_code: str, prompt_text: str, task_type: str = "comment"):
        super().__init__()
        self.provider_type = provider_type
        self.api_key = api_key
        self.base_url = base_url        # 动态地址
        self.model_name = model_name    # 动态模型
        self.context_code = context_code
        self.prompt_text = prompt_text
        self.task_type = task_type

    def run(self):
        try:
            if self.provider_type == "openai_compatible":
                openai = importlib.import_module("openai")
                import os
                import httpx

                os.environ['http_proxy'] = ''
                os.environ['https_proxy'] = ''
                os.environ['HTTP_PROXY'] = ''
                os.environ['HTTPS_PROXY'] = ''
                os.environ['ALL_PROXY'] = ''

                direct_client = httpx.Client(proxy=None, trust_env=False)

                # 【注入动态 Base URL】
                client = openai.OpenAI(
                    api_key=self.api_key, 
                    base_url=self.base_url,  # <--- 使用用户设置的 URL
                    http_client=direct_client
                )
                
                if self.task_type == "comment":
                    messages = [
                        {"role": "system", "content": self.prompt_text},
                        {"role": "user", "content": self.context_code}
                    ]
                else: 
                    messages = [
                        {"role": "system", "content": "你是一个严谨的编程导师。请结合用户提供的当前代码上下文，专业且简明扼要地解答用户的疑问。"},
                        {"role": "user", "content": f"【当前代码上下文】:\n{self.context_code}\n\n【我的问题】:\n{self.prompt_text}"}
                    ]

                response = client.chat.completions.create(
                    model=self.model_name,  # <--- 使用用户选定或输入的模型名
                    messages=messages,
                    stream=False,
                    temperature=0.3
                )

                result_text = response.choices[0].message.content
                
                # 仅在注释模式下清理 Markdown
                if self.task_type == "comment" and result_text.startswith("```"):
                    lines = result_text.split("\n")
                    if len(lines) > 2:
                        result_text = "\n".join(lines[1:-1])
                        
                self.signal_finished.emit(result_text)
                
            else:
                self.signal_error.emit(f"暂未支持的 AI 引擎: {self.provider_type}")
                
        except Exception as e:
            self.signal_error.emit(f"{str(e)}")