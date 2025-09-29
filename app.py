# ==============================================================================
#                      诊断脚本 1: test_secrets.py
# ==============================================================================
import streamlit as st

st.title("🔍 AI 功能诊断 - 第一层：密钥读取测试")

st.write("---")
st.subheader("正在尝试从 st.secrets 中读取 DEEPSEEK_API_KEY...")

try:
    # 尝试读取我们配置的密钥
    api_key = st.secrets["DEEPSEEK_API_KEY"]

    # 如果成功读取，就显示一些信息
    st.success("✅ 成功读取到 API 密钥！")
    
    st.write("**读取到的密钥内容 (为了安全，只显示前几位和后几位):**")
    
    # 为了安全，我们绝不完整显示密钥，只显示一个“面具”
    masked_key = f"{api_key[:5]}...{api_key[-4:]}"
    st.code(masked_key, language="text")

    st.info("诊断结论：Streamlit Cloud 的 Secrets 功能工作正常！问题不在于密钥的读取。")

except Exception as e:
    # 如果读取失败，就显示一个清晰的错误
    st.error("❌ 读取 API 密钥失败！")
    
    st.write("**捕获到的错误信息：**")
    st.exception(e)

    st.warning("诊断结论：问题很可能出在 Streamlit Cloud 的 Secrets 配置上。请检查你的密钥名称和内容是否完全正确。")