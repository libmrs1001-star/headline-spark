# ==============================================================================
#                      app.py (v2.4 - 最终抛光版)
# ==============================================================================
import streamlit as st
import time
import re
import os
import pandas as pd
import csv
import requests
from datetime import datetime
from typing import Tuple, List

# --- 页面配置 ---
st.set_page_config(page_title="Headline Spark", page_icon="✨", layout="wide")

# --- 后端函数 (已更新 Prompt) ---

def initialize_log_file():
    if not os.path.exists("event_log.csv"):
        pd.DataFrame(columns=["timestamp", "event_name", "title_analyzed", "score_given", "description_provided"]).to_csv("event_log.csv", index=False)

def log_event(event_name: str, title_analyzed: str = None, score_given: int = None, description_provided: bool = False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("event_log.csv", 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([timestamp, event_name, title_analyzed, score_given, description_provided])

def get_ai_response(prompt: str) -> str:
    try:
        api_key = st.secrets['DEEPSEEK_API_KEY']
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=body, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        log_event("ai_error", description_provided=str(e))
        return None

def get_ai_analysis(title: str) -> str:
    prompt = f'Act as a world-class copywriter reviewing a headline for Hacker News. The user\'s headline is: "{title}". Based on our core principle of "Stories over Topics", provide a brief, insightful analysis (max 50 words) covering one key strength and one key area for improvement. Your entire response must be in raw text, without any markdown formatting. Provide a Chinese version first, followed by the English version in parentheses.'
    result = get_ai_response(prompt)
    return result if result else "抱歉，AI 分析服务当前不可用，请稍后再试。"

def get_ai_ideas(description: str = None) -> List[str]:
    if description:
        prompt = f'Act as a viral headline generator for Hacker News. Based on the product description: "{description}", generate 3 headline ideas. For each of the 3 ideas, provide a Chinese version first, followed by the English version in parentheses on the next line. The final output should be 6 lines of raw text in total, with no extra formatting, numbering, or introductory sentences.'
    else:
        prompt = 'Act as a viral headline generator for Hacker News. Generate 3 generic but powerful "story-driven" headline templates that a startup founder could adapt. For each of the 3 ideas, provide a Chinese template first, followed by the English template in parentheses on the next line. The final output should be 6 lines of raw text in total, with no extra formatting, numbering, or introductory sentences.'
    
    result = get_ai_response(prompt)
    if result:
        return [line.strip() for line in result.split('\n') if line.strip()]
    return ["抱歉，AI 创意生成服务当前不可用", "请检查网络连接或稍后再试", "如需帮助，请联系技术支持"]


def analyze_title(title: str) -> Tuple[int, List[str]]:
    score = 5; feedback_list = []
    # (规则引擎逻辑保持不变)
    title = title.strip(); title_lower = title.lower()
    if not title: return 0, ["标题为空，无法分析"]
    if re.match(r'^(i|we)\\s+', title_lower): score += 2; feedback_list.append("✅ **第一人称开头:** 很好地引入了个人故事感。")
    if re.search(r'\\d', title_lower): score += 2; feedback_list.append("✅ **包含具体数字:** 让成果更可信、更具冲击力。")
    past_tense_verbs = ['built', 'launched', 'increased', 'saved', 'moved', 'created', 'grew', 'made', 'solved']
    if any(word in title_lower for word in past_tense_verbs): score += 1; feedback_list.append("✅ **使用结果导向动词:** 清晰地表明这是一个有结果的故事。")
    question_words = ['how', 'why', 'what', 'should i']
    if any(title_lower.startswith(word) for word in question_words): score -= 3; feedback_list.append("❌ **以疑问词开头:** 更像一个寻求帮助的话题，建议改写为陈述句。")
    speculative_verbs = ['think', 'believe', 'consider', 'hope', 'might', 'maybe']
    if any(word in title_lower for word in speculative_verbs): score -= 2; feedback_list.append("❌ **包含思辨性词汇:** 削弱了标题的结论性。")
    score = max(0, min(10, score))
    if not feedback_list: feedback_list.append("📝 标题结构较为中性。")
    if score >= 8: feedback_list.insert(0, "🌟 **总体评价:** 标题具有很强的故事性和说服力！")
    elif score >= 6: feedback_list.insert(0, "👍 **总体评价:** 标题具有较好的故事性，可以进一步优化。")
    else: feedback_list.insert(0, "⚠️ **总体评价:** 标题偏向话题性，建议增加故事性元素。")
    return score, feedback_list

# --- UI & 状态管理 ---
initialize_log_file()
if 'title_input' not in st.session_state: st.session_state.title_input = ""
if 'description_input' not in st.session_state: st.session_state.description_input = ""
if 'analysis_results' not in st.session_state: st.session_state.analysis_results = {}
if 'generated_ideas' not in st.session_state: st.session_state.generated_ideas = []

st.title("✨ Headline Spark & 标题火花 ✨")
st.write("一个由 Hacker News 数据洞察驱动的、帮助你“讲好产品故事”的智能标题分析器。")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📊 标题诊断分析器")
    st.text_input("输入你的标题:", key="title_input")
    if st.button("🔥 分析火花", use_container_width=True, type="primary"):
        if st.session_state.title_input:
            with st.spinner("AI 正在深度分析..."):
                score, feedback = analyze_title(st.session_state.title_input)
                ai_analysis = get_ai_analysis(st.session_state.title_input)
                st.session_state.analysis_results = {"score": score, "feedback": feedback, "ai_analysis": ai_analysis}
                log_event("analyze_clicked", st.session_state.title_input, score)
        else:
            st.warning("请输入标题进行分析。")
    
    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        st.metric("🔥 故事性评分", f"{res['score']} / 10")
        st.write("**📋 规则引擎分析:**")
        for item in res['feedback']: st.write(item)
        st.write("**🤖 AI 深度解读:**")
        st.info(res['ai_analysis'])

with col2:
    st.subheader("💡 灵感生成器")
    st.text_area("（可选）输入产品简介:", key="description_input", height=100)
    if st.button("✨ 生成灵感", use_container_width=True):
        with st.spinner("AI 正在构思创意..."):
            ideas = get_ai_ideas(st.session_state.description_input or None)
            st.session_state.generated_ideas = ideas
            log_event("generate_clicked", description_provided=bool(st.session_state.description_input))

    if st.session_state.generated_ideas:
        st.write("**🎯 生成的标题创意:**")
        # 将创意两两一组展示，中文在上，英文在下
        for i in range(0, len(st.session_state.generated_ideas), 2):
             st.markdown(f"**{i//2 + 1}. {st.session_state.generated_ideas[i]}**\n"
                         f"   *{st.session_state.generated_ideas[i+1]}*")

st.markdown("---")
st.caption("🚀 Built with Streamlit | Inspired by Hacker News data | Powered by DeepSeek AI")

# --- 侧边栏信息 ---
with st.sidebar:
    st.header("📈 使用统计")
    analysis_count = len([x for x in [st.session_state.analysis_results] if x])
    generate_count = len([x for x in [st.session_state.generated_ideas] if x])
    st.write("**今日分析次数：**", analysis_count)
    st.write("**今日生成次数：**", generate_count)
    
    st.markdown("---")
    st.header("💡 使用技巧")
    st.write("""
    **分析器使用技巧：**
    - 使用第一人称开头（I/We）
    - 包含具体数字和结果
    - 避免疑问句开头
    - 使用过去时动词
    
    **生成器使用技巧：**
    - 提供详细的产品描述
    - 描述产品的核心价值
    - 包含使用场景和效果
    """)
    
    st.markdown("---")
    st.header("🔧 技术信息")
    st.write("**版本：** V2.4")
    st.write("**AI 模型：** DeepSeek Chat")
    st.write("**分析引擎：** 规则 + AI 混合")
    
    # --- 开发者后台 ---
    st.markdown("---")
    st.header("🔧 开发者后台")
    
    if st.button("📊 查看用户行为日志", use_container_width=True):
        if os.path.exists("event_log.csv"):
            try:
                log_data = pd.read_csv("event_log.csv")
                if not log_data.empty:
                    st.write("**📋 用户行为日志：**")
                    st.dataframe(log_data, use_container_width=True)
                    
                    # 显示统计信息
                    st.write("**📊 日志统计：**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("总记录数", len(log_data))
                    with col2:
                        st.metric("分析事件", len(log_data[log_data['event_name'] == 'analyze_clicked']))
                else:
                    st.info("日志文件为空，暂无用户行为记录。")
            except Exception as e:
                st.error(f"读取日志文件时出错：{str(e)}")
        else:
            st.warning("日志文件暂不存在，请先使用应用功能生成日志。")