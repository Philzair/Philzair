🌤️ 天气出行智能助手 (Weather-Travel Agent)
一个基于 Python、LangGraph 和 Model Context Protocol (MCP) 构建的智能体（Agent）。它能够听懂用户的自然语言需求，自动调用外部天气 API 获取实时数据，并根据天气状况智能生成出行建议。

✨ 核心特性
会说（自然语言交互）：理解用户意图，支持多轮对话，能像朋友一样自然交流。

会做（工具调用）：基于 MCP 协议，能够自主调用“天气查询”和“出行规划”两个外部工具。

多轮记忆：通过 Streamlit 的 session_state 保存上下文（例如先问“北京”，再问“那上海呢？”）。

外部 API 交互：接入 Open-Meteo 免费天气 API，获取真实可靠的天气数据。

简洁的前端界面：使用 Streamlit 构建，开箱即用。

🛠️ 技术架构
前端界面：Streamlit

智能体框架：LangGraph (ReAct 模式)

工具协议：Model Context Protocol (MCP) - FastMCP & langchain-mcp-adapters

大语言模型：兼容 OpenAI 接口的任意模型（推荐 OpenRouter 免费模型或 DeepSeek）

天气数据源：Open-Meteo API（免费且无需注册）

🚀 快速开始
1. 环境准备
确保你的电脑上安装了 Python 3.10 或更高版本。

在 PyCharm 或终端中，创建并激活虚拟环境（如果在 PyCharm 中，请确保右下角解释器选择的是 .venv）：

bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
2. 安装依赖
在项目根目录的终端中执行：

bash
pip install -r requirements.txt
3. 配置环境变量
在项目根目录新建一个名为 .env 的文件（注意：不要有 .txt 后缀），填入你的大模型 API 配置。

方案 A：使用 OpenRouter 免费模型（推荐，零成本）

env
LLM_API_KEY=sk-or-v1-你的OpenRouter密钥
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/free
方案 B：使用 DeepSeek 官方 API

env
LLM_API_KEY=sk-你的DeepSeek密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
4. 启动应用
务必在项目根目录（包含 app.py 的那一层） 运行以下命令：

bash
streamlit run app.py
浏览器会自动打开 http://localhost:8501。

💡 功能演示（如何使用）
在输入框中输入自然语言，智能体会自动决定调用哪些工具并给出回答。以下是几个典型的使用场景：

场景一：单城市天气 + 出行建议
你输入：

杭州明天天气怎么样？适合去西湖吗？

智能体行为： 自动调用 get_forecast 获取杭州天气，然后调用 suggest_travel_plan 生成建议。
预期回答：

杭州明天温度 18–26°C，降水概率 15%... 适合去西湖。建议上午或傍晚沿湖步行，中午紫外线较强时可以在咖啡馆休息...

场景二：多轮对话记忆测试
你输入：

北京周末天气呢？
(智能体回答北京周末天气及建议)
你接着输入：
那上海呢？

智能体行为： 结合上下文，明白你是在问“上海周末的天气及建议”，自动查询上海的数据。
预期回答：

上海周末温度 20–27°C，周六降水概率 65%。周六不太适合长时间户外活动，建议安排室内展览...

场景三：带特定偏好出行
你输入：

成都明天适合带娃出去玩吗？

智能体行为： 识别出“带娃”偏好，调用 suggest_travel_plan 时传入 preference="带娃"。
预期回答：

成都明天天气... 带娃出行建议优先选择亲子友好场所，并预留室内备选，避免长时间暴晒...

📂 项目结构
text
weather-travel-agent/
├── app.py                  # Streamlit 前端入口，负责多轮对话状态管理
├── requirements.txt        # 项目依赖清单
├── .env                    # 环境变量（需自行创建，勿提交到 Git）
├── agent/                  # 智能体核心逻辑
│   ├── __init__.py
│   ├── graph.py            # LangGraph 构建 Agent，连接 MCP 客户端
│   └── prompts.py          # 系统提示词（System Prompt）
└── servers/                # MCP 工具服务器（独立进程）
    ├── weather_server.py   # 天气查询服务（对接 Open-Meteo API）
    └── travel_server.py    # 出行规划服务（本地规则引擎）
❓ 常见问题排错 (FAQ)
Q1: 报错 File does not exist: app.py
A: 说明终端不在项目根目录。请执行 cd .. 退回到外层，确认当前路径下有 app.py，再执行 streamlit run app.py。

Q2: 报错 Missing credentials 或 api_key 为空
A: 没有读取到 .env 文件。检查 .env 是否在根目录，以及是否在修改后重启了 Streamlit（Ctrl+C 停止后重新运行）。

Q3: 报错 UnicodeEncodeError: 'ascii' codec can't encode...
A: .env 里的 API Key 混入了中文或非法空格。确保 Key 是纯英文字母和数字。

Q4: 运行后对话一直转圈或报 MCP 连接错误
A: 在 PyCharm 终端手动运行 python servers/weather_server.py。如果进程卡住不报错（光标闪烁），说明服务正常，可以 Ctrl+C 停止。这通常能解决首次加载慢的问题。