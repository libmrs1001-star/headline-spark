import streamlit as st
import time
import re
import os
import pandas as pd
import csv
from datetime import datetime
from typing import Tuple, List

st.set_page_config(page_title="Headline Spark", page_icon="✨", layout="wide")

def initialize_log_file():
    """
    初始化日志文件，如果不存在则创建 event_log.csv 文件并写入表头
    只在应用启动时调用一次
    """
    log_file_path = "event_log.csv"
    
    # 检查文件是否存在
    if not os.path.exists(log_file_path):
        # 创建包含表头的 DataFrame
        headers = ["timestamp", "event_name", "title_analyzed", "score_given", "description_provided"]
        df = pd.DataFrame(columns=headers)
        
        # 保存到 CSV 文件
        df.to_csv(log_file_path, index=False, encoding='utf-8')
        print(f"已创建日志文件: {log_file_path}")

def log_event(event_name: str, title_analyzed: str = None, score_given: int = None, description_provided: str = None):
    """
    记录事件到日志文件
    
    参数:
    - event_name: 事件名称 (必需)
    - title_analyzed: 分析的标题 (可选)
    - score_given: 给出的分数 (可选)
    - description_provided: 提供的描述 (可选)
    """
    log_file_path = "event_log.csv"
    
    # 获取当前时间戳并格式化为字符串
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 准备要写入的数据行
    row_data = [timestamp, event_name, title_analyzed, score_given, description_provided]
    
    # 使用 csv 模块以追加模式打开文件并写入新行
    try:
        with open(log_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row_data)
        print(f"已记录事件: {event_name} at {timestamp}")
    except Exception as e:
        print(f"记录事件时出错: {e}")

def get_ai_analysis(title: str) -> str:
    """
    使用 DeepSeek API 分析标题
    
    参数:
    - title: 要分析的标题字符串
    
    返回:
    - AI 分析结果字符串，如果出错则返回错误信息
    """
    try:
        # 导入必要的模块
        from deepseek import DeepSeek
        
        # 安全地读取 API 密钥
        api_key = st.secrets['DEEPSEEK_API_KEY']
        
        # 初始化 DeepSeek 客户端
        client = DeepSeek(api_key=api_key)
        
        # 构建 Prompt
        prompt = f'Act as a world-class copywriter reviewing a headline for Hacker News. The user\'s headline is: "{title}". Based on our core principle of "Stories over Topics", provide a brief, insightful analysis (max 50 words) covering one key strength and one key area for improvement.'
        
        # 发送请求到 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # 提取并返回结果
        result = response.choices[0].message.content
        return result
        
    except Exception as e:
        # 记录错误到日志
        log_event("ai_analysis_error", title, description_provided=f"错误: {str(e)}")
        return "抱歉，AI 分析服务当前不可用，请稍后再试。"

def get_ai_ideas(description: str = None) -> List[str]:
    """
    使用 DeepSeek API 生成标题创意
    
    参数:
    - description: 产品描述（可选）
    
    返回:
    - 包含 3 个标题创意的字符串列表，如果出错则返回错误信息列表
    """
    try:
        # 导入必要的模块
        from deepseek import DeepSeek
        
        # 安全地读取 API 密钥
        api_key = st.secrets['DEEPSEEK_API_KEY']
        
        # 初始化 DeepSeek 客户端
        client = DeepSeek(api_key=api_key)
        
        # 根据是否有描述来选择不同的 Prompt
        if description:
            # 基于产品描述的 Prompt
            prompt = f'Act as a viral headline generator for Hacker News. Based on the product description: "{description}", generate 3 headline ideas. Each must be a "story" or a "surprising result".'
        else:
            # 通用标题模板的 Prompt
            prompt = 'Act as a viral headline generator for Hacker News. Generate 3 generic but powerful "story-driven" headline templates that a startup founder could adapt.'
        
        # 发送请求到 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # 提取并处理结果
        result = response.choices[0].message.content
        
        # 将返回的文本分割成列表
        ideas = [idea.strip() for idea in result.split('\n') if idea.strip()]
        
        # 确保返回 3 个创意，如果不够则补充
        while len(ideas) < 3:
            ideas.append("创意生成中...")
        
        # 如果超过 3 个，只取前 3 个
        ideas = ideas[:3]
        
        return ideas
        
    except Exception as e:
        # 记录错误到日志
        log_event("ai_ideas_error", description_provided=f"错误: {str(e)}")
        # 返回友好的错误信息列表
        return [
            "抱歉，AI 创意生成服务当前不可用",
            "请检查网络连接或稍后再试",
            "如需帮助，请联系技术支持"
        ]

def analyze_title(title: str) -> Tuple[int, List[str]]:
    score = 5; feedback_list = []
    title = title.strip(); title_lower = title.lower()
    if not title: return 0, ["请选择一个案例进行分析"]
    if re.match(r'^(i|we)\s+', title_lower): score += 2; feedback_list.append("✅ **第一人称开头:** 很好地引入了个人故事感。")
    if re.search(r'\d', title_lower): score += 2; feedback_list.append("✅ **包含具体数字:** 让成果更可信、更具冲击力。")
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

# 初始化日志文件（只在应用启动时调用一次）
initialize_log_file()

# 初始化 session state
if 'title_input' not in st.session_state:
    st.session_state.title_input = ""
if 'description_input' not in st.session_state:
    st.session_state.description_input = ""
if 'analysis_score' not in st.session_state:
    st.session_state.analysis_score = None
if 'analysis_feedback' not in st.session_state:
    st.session_state.analysis_feedback = []
if 'ai_analysis_result' not in st.session_state:
    st.session_state.ai_analysis_result = None
if 'generated_ideas' not in st.session_state:
    st.session_state.generated_ideas = []

st.title("✨ Headline Spark & 标题火花 ✨")
st.write("一个由 Hacker News 数据洞察驱动的、帮助你""讲好产品故事""的智能标题分析器。")
st.markdown("---")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 标题分析器")
    st.write("输入你的标题，获得专业的分析和建议：")
    
    # 标题输入框
    title_input = st.text_input(
        "输入标题：",
        value=st.session_state.title_input,
        placeholder="例如：I built a note app with Rust, and it's 50% faster than Obsidian.",
        key="title_input_widget"
    )
    
    # 更新 session state
    st.session_state.title_input = title_input
    
    # 分析按钮
    if st.button("🔥 分析火花", use_container_width=True, type="primary"):
        if title_input.strip():
            with st.spinner("正在分析中..."):
                # 1. 调用规则引擎分析
                score, feedback = analyze_title(title_input)
                
                # 2. 调用 AI 深度分析
                ai_analysis = get_ai_analysis(title_input)
                
                # 3. 更新 session state
                st.session_state.analysis_score = score
                st.session_state.analysis_feedback = feedback
                st.session_state.ai_analysis_result = ai_analysis
                
                # 4. 记录事件到日志
                log_event("analyze_button_clicked", title_input, score, "用户点击了分析按钮")
                
                st.success("分析完成！")
        else:
            st.warning("请输入一个标题进行分析。")
    
    # 显示分析结果
    if st.session_state.analysis_score is not None:
        st.markdown("---")
        st.metric("🔥 故事性评分 (Narrative Score)", f"{st.session_state.analysis_score} / 10")
        
        # 显示规则引擎反馈
        st.write("**📋 规则引擎分析：**")
        for item in st.session_state.analysis_feedback:
            st.write(item)
        
        # 显示 AI 深度分析
        if st.session_state.ai_analysis_result:
            st.write("**🤖 AI 深度解读：**")
            st.info(st.session_state.ai_analysis_result)

with col2:
    st.subheader("💡 标题生成器")
    st.write("输入产品描述，获得 3 个故事性标题创意：")
    
    # 产品描述输入框
    description_input = st.text_area(
        "产品描述（可选）：",
        value=st.session_state.description_input,
        placeholder="例如：一个帮助开发者快速构建 API 的工具，支持多种编程语言...",
        height=100,
        key="description_input_widget"
    )
    
    # 更新 session state
    st.session_state.description_input = description_input
    
    # 生成按钮
    if st.button("✨ 生成灵感", use_container_width=True, type="secondary"):
        with st.spinner("正在生成创意中..."):
            # 1. 调用 AI 创意生成
            ideas = get_ai_ideas(description_input if description_input.strip() else None)
            
            # 2. 更新 session state
            st.session_state.generated_ideas = ideas
            
            # 3. 记录事件到日志
            has_description = bool(description_input.strip())
            log_event("generate_button_clicked", description_provided=f"用户点击了生成按钮，是否提供描述: {has_description}")
            
            st.success("创意生成完成！")
    
    # 显示生成的创意
    if st.session_state.generated_ideas:
        st.markdown("---")
        st.write("**🎯 生成的标题创意：**")
        for i, idea in enumerate(st.session_state.generated_ideas, 1):
            st.write(f"**{i}.** {idea}")
            st.write("")  # 添加空行

# 底部信息
st.markdown("---")
st.caption("🚀 Built with Streamlit | Inspired by Hacker News data | Powered by DeepSeek AI")

# 侧边栏信息
with st.sidebar:
    st.header("📈 使用统计")
    st.write("**今日分析次数：**", len([x for x in [st.session_state.analysis_score] if x is not None]))
    st.write("**今日生成次数：**", len([x for x in [st.session_state.generated_ideas] if x]))
    
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
    st.write("**版本：** V2.0")
    st.write("**AI 模型：** DeepSeek Chat")
    st.write("**分析引擎：** 规则 + AI 混合")
