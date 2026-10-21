# app.py
import asyncio
import streamlit as st
from agent.graph import build_agent

event_loop = asyncio.new_event_loop()

st.set_page_config(page_title="天气出行助手", page_icon="🌤️")
st.title("🌤️ 天气出行助手")
st.caption("查询天气，自动生成出行计划")


async def run_agent(messages):
    agent, _ = await build_agent()
    return await agent.ainvoke({"messages": messages})


def invoke_agent(messages):
    return event_loop.run_until_complete(run_agent(messages))

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
            result = invoke_agent(
                [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            answer = result["messages"][-1].content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
