# 天气出行智能助手（Weather-Travel Agent）

用户通过中文提出天气或出行需求，Agent 调用天气 API 获取数据，再调用出行建议工具生成回答。界面使用 Streamlit，Agent 使用 LangGraph，工具通过 MCP stdio 协议连接。

## 作业要求与项目功能

- **自然语言对话**：使用支持工具调用的模型理解城市、时间和出行需求，并生成中文回答。
- **执行操作**：通过 MCP 调用真实天气接口和本地出行建议工具。
- **MCP 框架**：使用 FastMCP 提供工具，使用 `langchain-mcp-adapters` 连接工具服务。
- **对话上下文**：使用 `st.session_state` 保存当前会话中的用户输入和助手回答，并在后续请求中传入历史消息。

小组需要另外提供真实的成员分工。可以按照界面与会话、Agent 与提示词、MCP 与天气接口、测试与展示材料分配职责，并在提交材料中填写成员姓名和实际完成内容。

## 工具说明

两个 MCP 服务提供三个工具：

- `get_current_weather(city)`：查询城市当前温度、湿度、风速和天气代码。
- `get_forecast(city, days=3)`：查询从当天开始的天气预报，支持 1～7 天，返回日期、最低与最高温度、降水概率、最大风速和紫外线指数。
- `suggest_travel_plan(...)`：根据天气数值和用户需求生成出行建议，包括雨具、衣着、防晒及室内或户外活动建议。

查询明天需要取得包含当天在内的两天预报，并使用第二个日期的数据；查询后天需要取得三天预报，并使用第三个日期的数据。系统提示词要求回答写出实际日期。

出行建议工具使用本地规则生成活动建议。具体景点的开放时间、门票和交通信息需要另外查询。

## 环境准备

本项目使用 Python 3.12.10 完成运行检查。模型需要支持兼容 OpenAI Chat Completions 的接口和工具调用。天气查询和模型调用均需要网络连接。

以下命令使用 Windows PowerShell。终端工作目录必须是包含 `app.py` 的 `weather-travel-agent` 目录。

### 创建本机环境并安装依赖

从 `vier` 目录进入项目目录：

```powershell
Set-Location weather-travel-agent
python -m venv .venv-local
$env:PATH = (Resolve-Path .venv-local/Scripts).Path + ';' + $env:PATH
python -m pip install -r requirements.txt
python -m pip check
```

`.venv-local` 用于存放本机创建的运行环境。项目附带的 `.venv` 引用了其他电脑的解释器路径，当前电脑需要使用本机环境。

每次打开新的 PowerShell 窗口后，在项目目录执行下面的命令，让应用及 MCP 子进程使用同一个 Python：

```powershell
$env:PATH = (Resolve-Path .venv-local/Scripts).Path + ';' + $env:PATH
python -c "import sys; print(sys.executable)"
```

输出应指向 `.venv-local\Scripts\python.exe`。

### 配置模型

在项目目录创建或编辑 `.env`，填写模型服务提供的配置：

```dotenv
LLM_API_KEY=YOUR_API_KEY
LLM_BASE_URL=YOUR_API_BASE_URL
LLM_MODEL=YOUR_MODEL_NAME
```

三个值需要替换为实际配置。已有可用 `.env` 时，可以直接使用。模型服务的调用费用和额度由服务商决定；配置文件中包含密钥，不应随作业公开提交。

### 启动应用

```powershell
python -m streamlit run app.py
```

打开终端显示的本地页面地址，在输入框提交问题。应用会自动启动 MCP 子进程。结束运行时，在终端按 `Ctrl+C`。

### 使用当前工作区已安装的环境

当前 `vier/.run-check/venv` 已安装项目依赖。在 `vier` 目录可以执行：

```powershell
$env:PATH = (Resolve-Path .run-check/venv/Scripts).Path + ';' + $env:PATH
Set-Location weather-travel-agent
python -m streamlit run app.py
```

`.run-check` 是当前工作区的运行检查目录。将项目复制到其他电脑后，需要按照环境准备步骤创建本机环境。

## 演示输入

1. 输入“杭州明天天气怎么样？适合带娃去西湖吗？”，观察回答中的日期、天气数据和出行建议。
2. 接着输入“那上海呢？”，检查是否继续查询相同日期和出行需求。
3. 输入“成都未来三天天气怎么样？”，检查回答中的日期和预报范围。

天气数值随实际查询结果变化。工具调用记录可以在运行终端中查看。

## 文件说明

- `app.py`：Streamlit 页面、会话消息和 Agent 调用。
- `agent/graph.py`：模型配置、MCP 客户端和 LangGraph Agent 构建。
- `agent/prompts.py`：系统提示词与日期选择要求。
- `servers/weather_server.py`：地理查询、当前天气和天气预报服务。
- `servers/travel_server.py`：本地出行建议服务。
- `requirements.txt`：Python 依赖清单。
- `.env`：本地模型配置。

## 验证状态

已完成真实 MCP 调用检查，三个工具均成功返回结果。Streamlit HTTP 服务启动检查通过，单轮对话能够返回天气和出行建议；最近一次测试中的“明天”回答使用了第二个日期的数据。

连续两轮对话尚未通过完整验证：最近一次检查中，第二轮模型请求在等待期间没有返回，测试已终止。当前不能将连续对话标记为验证通过。运行记录见上级目录的 [log.md](../log.md)。

## 运行问题检查

- **找不到 `app.py`**：确认当前目录包含 `app.py`，再执行启动命令。
- **缺少依赖或 MCP 子进程无法导入模块**：检查 `python` 指向的解释器，在同一个环境中执行 `python -m pip install -r requirements.txt` 和 `python -m pip check`。
- **模型认证失败**：核对 `.env` 中的密钥、接口地址、模型名称及服务额度，修改配置后重新启动应用。
- **请求长时间没有返回**：查看终端输出，确认请求停留在模型服务、地理查询还是天气查询阶段。页面启动成功和完整对话成功需要分别验证。
- **手动运行 MCP 服务后等待输入**：stdio 服务需要 MCP 客户端发送协议消息；仅凭进程持续运行，无法确认工具调用成功。
