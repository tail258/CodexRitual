import importlib
from PyQt6.QtCore import QThread, pyqtSignal

class AITaskWorker(QThread):
    """
    专门负责处理大模型请求的独立后台神经元。
    继承 QThread，确保长时间的网络请求不会阻塞主 UI 线程。
    """
    # 定义信号：当任务完成或报错时，通过信号向主窗口汇报
    signal_finished = pyqtSignal(str)
    signal_error = pyqtSignal(str)

    def __init__(self, provider_type: str, api_key: str, code: str, system_prompt: str):
        super().__init__()
        self.provider_type = provider_type
        self.api_key = api_key
        self.code = code
        self.system_prompt = system_prompt

    def run(self):
        """线程启动后执行的核心逻辑"""
        try:
            if self.provider_type == "deepseek":
                # 动态导入，避免无用开销
                openai = importlib.import_module("openai")
                
                # 配置 DeepSeek 兼容客户端
                client = openai.OpenAI(
                    api_key=self.api_key, 
                    base_url="[https://api.deepseek.com](https://api.deepseek.com)"
                )
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": self.code}
                    ],
                    stream=False,
                    temperature=0.3  # 较低的温度确保输出更稳定、更符合格式
                )
                
                result_code = response.choices[0].message.content
                
                # 清理可能被大模型误加的 Markdown 代码块标记 (兜底策略)
                if result_code.startswith("```"):
                    lines = result_code.split("\n")
                    if len(lines) > 2:
                        result_code = "\n".join(lines[1:-1])
                        
                self.signal_finished.emit(result_code)
                
            else:
                self.signal_error.emit(f"暂未支持的 AI 引擎: {self.provider_type}")
                
        except ImportError:
            self.signal_error.emit("环境缺失：请在终端运行 'pip install openai'")
        except Exception as e:
            self.signal_error.emit(f"AI 脑波连接失败: {str(e)}")