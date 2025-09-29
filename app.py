# ==============================================================================
#                      诊断脚本 2: test_connection.py
# ==============================================================================
import streamlit as st
import requests # 我们只使用最基础的 requests 库

st.title("🔍 AI 功能诊断 - 第二层：基础连接测试")

# 从 Secrets 中读取密钥，我们已经知道这步是成功的
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
    st.success("✅ 密钥读取成功！准备进行网络连接测试...")
except Exception as e:
    st.error(f"密钥读取环节意外失败: {e}")
    st.stop() # 如果这步失败，就没必要继续了

# --- DeepSeek API 的基础信息 ---
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
# 一个最简单的测试请求体
body = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello!"}]
}

st.write("---")
st.subheader(f"正在尝试向 DeepSeek API 端点发送一个基础的 POST 请求...")
st.code(f"POST {DEEPSEEK_API_ENDPOINT}", language="bash")

# --- 执行网络请求 ---
try:
    with st.spinner("等待 API 响应..."):
        response = requests.post(DEEPSEEK_API_ENDPOINT, headers=headers, json=body, timeout=20)

    st.write("---")
    st.subheader("API 响应结果：")

    # 检查 HTTP 状态码
    if response.status_code == 200:
        st.success(f"✅ 连接成功！HTTP 状态码: {response.status_code}")
        st.write("**API 返回的 JSON 内容：**")
        st.json(response.json())
        st.info("诊断结论：网络连接和 API 认证均正常！问题很可能出在 `deepseek` Python 库的内部实现或其依赖项上。")
    else:
        st.error(f"❌ 连接失败！HTTP 状态码: {response.status_code}")
        st.write("**API 返回的错误详情：**")
        st.json(response.json())
        st.warning("诊断结论：API 服务器返回了错误。请检查密钥权限或 DeepSeek 的服务状态。")

except Exception as e:
    st.error("❌ 在尝试连接时，发生了网络层面的异常！")
    st.write("**捕获到的异常信息：**")
    st.exception(e)
    st.warning("诊断结论：Streamlit Cloud 服务器可能无法访问 DeepSeek 的 API 地址。这可能是由于防火墙或网络策略限制。")