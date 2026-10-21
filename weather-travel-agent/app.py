# app.py
import asyncio
import nest_asyncio
import streamlit as st
from agent.graph import build_agent

nest_asyncio.apply()

st.set_page_config(page_title="天气出行助手", page_icon="🌤️")
st.title("🌤️ 天气出行助手")
st.caption("查询天气，自动生成出行计划")


@st.cache_resource
def get_agent():
    return asyncio.run(build_agent())


agent, tools = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("例如：杭州明天天气如何？适合去西湖吗？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("正在查询天气并规划出行..."):
            result = asyncio.run(
                agent.ainvoke(
                    {
                        "messages": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    }
                )
            )
            answer = result["messages"][-1].content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})