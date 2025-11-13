import streamlit as st
import os
from datetime import datetime, timedelta
import glob
import numpy as np
import random
import base64



# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-72997944466a4af2bcd52a068895f8cf",
    base_url="https://api.deepseek.com"
)

# 页面配置
st.set_page_config(
    page_title="八字塔罗运势",
    page_icon="🔮",
    layout="centered"
)

# -------------------- 背景视频功能 --------------------
def set_background_video(video_path):
    """设置背景视频"""
    try:
        # 读取视频文件并编码为base64
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()
        video_base64 = base64.b64encode(video_data).decode()
        
        # 创建背景视频的HTML/CSS - 修改为居中显示
        background_video_html = f"""
        <style>
        #bgVideo {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            min-width: 100%;
            min-height: 100%;
            width: auto;
            height: auto;
            z-index: -100;
            object-fit: cover;
        }}
        
        /* 确保Streamlit内容在视频之上 */
        .main {{
            position: relative;
            z-index: 1;
        }}
        
        .block-container {{
            position: relative;
            z-index: 2;
        }}
        
        /* 添加黑色背景层确保视频覆盖整个屏幕 */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000;
            z-index: -101;
        }}
        </style>
        <video id="bgVideo" autoplay muted loop playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            您的浏览器不支持视频标签。
        </video>
        """
        st.markdown(background_video_html, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.warning(f"背景视频加载失败: {e}")
        return False

def setup_background_video():
    """设置背景视频"""
    # 搜索视频文件 - 根据您的项目结构调整路径
    video_dirs = ["src/videos", "videos", "./src/videos", "./videos"]
    video_extensions = ("*.mp4", "*.MP4", "*.mov", "*.MOV")
    
    video_files = []
    for video_dir in video_dirs:
        if os.path.exists(video_dir):
            for ext in video_extensions:
                found_videos = glob.glob(os.path.join(video_dir, ext))
                video_files.extend(found_videos)
    
    # 如果找到视频文件，选择第一个
    if video_files:
        video_path = video_files[0]
        return set_background_video(video_path)
    else:
        # 如果没有找到视频，使用备用方案
        st.markdown("""
        <style>
        .main {
            background: linear-gradient(125deg, #0f0c29, #302b63, #24243e);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        </style>
        """, unsafe_allow_html=True)
        return False

# -------------------- 简化样式 --------------------
def set_simple_style():
    st.markdown("""
    <style>
        .main { 
            background-color: transparent;
        }
        
        .block-container {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem;
            backdrop-filter: blur(5px);
        }
        
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: bold;
            margin: 0.2rem;
        }
        
        .recommendation-button {
            background-color: #6c5ce7;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.8rem 1.5rem;
            font-weight: bold;
            margin: 0.3rem;
            width: 100%;
            text-align: center;
        }
        
        .active-button {
            background-color: #e17055 !important;
        }
        
        .disclaimer {
            background-color: rgba(255, 243, 205, 0.9);
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            font-style: italic;
            color: #856404;
        }
        
        .zodiac-section {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
        }
        
        .guardian-spirit {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.9) 0%, rgba(255, 165, 0, 0.9) 100%);
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
        }
        
        .recommendation-card {
            background-color: rgba(255, 255, 255, 0.95);
            border: 2px solid #6c5ce7;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            background-color: rgba(255, 255, 255, 0.9);
        }
        
        .user-message {
            background-color: rgba(227, 242, 253, 0.9);
            border-left: 4px solid #2196f3;
        }
        
        .assistant-message {
            background-color: rgba(243, 229, 245, 0.9);
            border-left: 4px solid #9c27b0;
        }
        
        .video-container {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

set_simple_style()

# -------------------- 会话状态初始化 --------------------
def init_session_state():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "birth_info" not in st.session_state:
        st.session_state.birth_info = None
    if "daily_fortune" not in st.session_state:
        st.session_state.daily_fortune = None
    if "media_indexed" not in st.session_state:
        st.session_state.media_indexed = False
    if "songs_meta" not in st.session_state:
        st.session_state.songs_meta = []
    if "all_images" not in st.session_state:
        st.session_state.all_images = []
    if "zodiac_videos" not in st.session_state:
        st.session_state.zodiac_videos = {}
    if "last_fortune_date" not in st.session_state:
        st.session_state.last_fortune_date = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""
    if "background_video" not in st.session_state:
        st.session_state.background_video = None
    # 个性推荐相关状态
    if "current_recommendation" not in st.session_state:
        st.session_state.current_recommendation = None
    if "recommendation_type" not in st.session_state:
        st.session_state.recommendation_type = None
    if "personal_recommendations" not in st.session_state:
        st.session_state.personal_recommendations = {}

init_session_state()

# -------------------- 核心工具函数 --------------------
ZODIAC = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
ZODIAC_EMOJIS = ["🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑", "🐵", "🐔", "🐶", "🐷"]
ZODIAC_DESCRIPTIONS = {
    "鼠": "聪明机智，适应力强", "牛": "勤奋踏实，稳重可靠", "虎": "勇敢果断，充满活力",
    "兔": "温和优雅，心思细腻", "龙": "自信强大，领导力强", "蛇": "智慧深沉，直觉敏锐",
    "马": "自由奔放，热情开朗", "羊": "温和善良，富有同情心", "猴": "聪明伶俐，善于交际",
    "鸡": "勤奋守时，注重细节", "狗": "忠诚可靠，正义感强", "猪": "真诚坦率，福气满满"
}

GUARDIAN_SPIRITS = {
    "鼠": "智慧守护灵 - 赐予你敏锐的洞察力和应变能力",
    "牛": "坚韧守护灵 - 赋予你持久的耐力和坚定的意志",
    "虎": "勇气守护灵 - 带给你无畏的勇气和行动力",
    "兔": "温柔守护灵 - 守护你的善良和细腻情感",
    "龙": "力量守护灵 - 赐予你强大的领导力和创造力",
    "蛇": "智慧守护灵 - 赋予你深刻的直觉和洞察力",
    "马": "自由守护灵 - 带给你奔放的活力和冒险精神",
    "羊": "和谐守护灵 - 守护你的温柔和艺术天赋",
    "猴": "机智守护灵 - 赐予你灵活的思维和沟通能力",
    "鸡": "精准守护灵 - 赋予你细致入微的观察力",
    "狗": "忠诚守护灵 - 守护你的真诚和正义感",
    "猪": "福气守护灵 - 带给你好运和丰盛的能量"
}

# 本地推荐数据（降级方案）
LOCAL_RECOMMENDATIONS = {
    "工作类型": {
        "鼠": "数据分析师、投资顾问、心理咨询师 - 发挥你的敏锐洞察力",
        "牛": "工程师、会计师、农业专家 - 适合踏实稳重的工作",
        "虎": "企业家、销售总监、运动员 - 发挥领导力和行动力",
        "兔": "教师、设计师、医护人员 - 适合温和细致的工作",
        "龙": "管理者、创意总监、政治家 - 发挥领导才能",
        "蛇": "研究员、策划师、分析师 - 适合深度思考的工作",
        "马": "旅行博主、销售、创业者 - 适合自由奔放的性格",
        "羊": "艺术家、社工、教育工作者 - 发挥艺术天赋和同情心",
        "猴": "公关、程序员、主持人 - 适合灵活多变的工作",
        "鸡": "编辑、质检员、律师 - 发挥细致入微的特点",
        "狗": "警察、教师、顾问 - 适合忠诚可靠的工作",
        "猪": "厨师、酒店管理、慈善工作 - 发挥真诚善良的特质"
    },
    "电影": {
        "鼠": "《肖申克的救赎》- 智慧与坚持的胜利\n《心灵捕手》- 发掘内在潜力",
        "牛": "《当幸福来敲门》- 勤奋终有回报\n《阿甘正传》- 单纯坚持的力量",
        "虎": "《勇敢的心》- 勇气与自由\n《国王的演讲》- 克服恐惧",
        "兔": "《海蒂和爷爷》- 温暖治愈\n《小森林》- 简单生活之美",
        "龙": "《指环王》- 领导与责任\n《盗梦空间》- 创意无限",
        "蛇": "《禁闭岛》- 深度心理探索\n《消失的爱人》- 复杂人性",
        "马": "《荒野求生》- 自由冒险精神\n《罗马假日》- 浪漫旅程",
        "羊": "《放牛班的春天》- 艺术与教育\n《天使爱美丽》- 温暖善良",
        "猴": "《猫鼠游戏》- 机智对决\n《王牌特工》- 优雅智慧",
        "鸡": "《穿普拉达的女王》- 职场成长\n《完美陌生人》- 细节洞察",
        "狗": "《忠犬八公的故事》- 忠诚守护\n《绿里奇迹》- 正义与善良",
        "猪": "《寻梦环游记》- 家庭温暖\n《美食总动员》- 美食与幸福"
    }
}

def year_to_zodiac(year: int):
    return ZODIAC[(year - 1900) % 12]

def get_zodiac_emoji(zodiac: str):
    index = ZODIAC.index(zodiac)
    return ZODIAC_EMOJIS[index]

def get_zodiac_description(zodiac: str):
    return ZODIAC_DESCRIPTIONS.get(zodiac, "")

def get_guardian_spirit(zodiac: str):
    return GUARDIAN_SPIRITS.get(zodiac, "")

def load_media_resources():
    """加载音乐和视频资源"""
    try:
        songs = []
        all_images = []
        zodiac_videos = {}

        # 加载音乐
        music_dirs = ["src/music", "./src/music", "music", "./music"]
        for music_dir in music_dirs:
            if os.path.exists(music_dir):
                for ext in ("*.mp3", "*.wav", "*.m4a"):
                    music_files = glob.glob(os.path.join(music_dir, ext))
                    for p in music_files:
                        if os.path.isfile(p):
                            fname = os.path.basename(p)
                            name_no_ext = os.path.splitext(fname)[0]
                            songs.append({
                                "filename": fname,
                                "title": name_no_ext,
                                "emotion": "中性",
                                "path": p
                            })

        # 加载图片和视频
        image_dirs = ["src/images", "./src/images", "images", "./images"]
        for image_dir in image_dirs:
            if os.path.exists(image_dir):
                # 加载静态图片
                for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                    image_files = glob.glob(os.path.join(image_dir, ext))
                    for p in image_files:
                        if os.path.isfile(p):
                            all_images.append(p)
                
                # 加载生肖动图
                for ext in ("*.mp4", "*.MP4"):
                    video_files = glob.glob(os.path.join(image_dir, ext))
                    for p in video_files:
                        if os.path.isfile(p):
                            filename = os.path.basename(p).lower()
                            for zodiac in ZODIAC:
                                if zodiac in filename:
                                    zodiac_videos[zodiac] = p
                                    break

        st.session_state.songs_meta = songs
        st.session_state.all_images = all_images
        st.session_state.zodiac_videos = zodiac_videos
        st.session_state.media_indexed = True
        
        st.success(f"✅ 加载了 {len(songs)} 首音乐, {len(all_images)} 张图片和 {len(zodiac_videos)} 个生肖动图")
        
    except Exception as e:
        st.error(f"加载媒体资源时出错: {e}")

def match_song_by_text(text: str, top_k=1):
    """简化版音乐匹配"""
    songs = st.session_state.songs_meta
    if not songs:
        return []

    text_lower = text.lower()
    matched_songs = []
    
    for song in songs:
        score = 0
        song_title = song['title'].lower()
        
        if any(word in text_lower for word in ["快乐", "开心", "喜悦"]):
            score += 2
        if any(word in text_lower for word in ["平静", "安宁", "放松"]):
            score += 1
            
        if score > 0:
            matched_songs.append((score, song))
    
    if not matched_songs and songs:
        matched_songs.append((1, random.choice(songs)))
    
    matched_songs.sort(key=lambda x: x[0], reverse=True)
    return matched_songs[:top_k]

def get_random_image():
    all_images = st.session_state.all_images
    if all_images:
        return random.choice(all_images)
    return None

def get_zodiac_video(zodiac):
    """获取生肖动图"""
    zodiac_videos = st.session_state.zodiac_videos
    return zodiac_videos.get(zodiac)

def display_media(song_meta, zodiac):
    """显示动图和音乐"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        zodiac_video = get_zodiac_video(zodiac)
        if zodiac_video and os.path.exists(zodiac_video):
            st.markdown("<div class='video-container'>", unsafe_allow_html=True)
            st.video(zodiac_video)
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption(f"今日守护生肖：{zodiac}")
        else:
            random_image = get_random_image()
            if random_image and os.path.exists(random_image):
                st.image(random_image, caption=f"今日守护生肖：{zodiac}", use_container_width=True)
            else:
                st.info("📷 暂无生肖动图资源")
    
    with col2:
        st.subheader(f"🎵 {song_meta['title']}")
        st.write(f"**情感标签：** {song_meta['emotion']}")
        
        if os.path.exists(song_meta["path"]):
            try:
                st.audio(song_meta["path"])
            except Exception as e:
                st.error(f"播放音乐失败: {e}")
        else:
            st.error("音乐文件不存在")

def generate_specific_recommendation(recommendation_type, zodiac, birth_year, place, birth_hour, gender):
    """生成特定类型的推荐"""
    prompts = {
        "工作类型": f"基于生肖{zodiac}、{birth_year}年出生、{place}人、{gender}性的特点，推荐3个最适合的工作类型，并说明理由",
        "车型": f"根据生肖{zodiac}的性格特点和命理，推荐2款最适合的汽车类型，说明为什么适合",
        "工作方位": f"基于八字命理，为生肖{zodiac}的{gender}性推荐2个最吉利的工作和发展方位",
        "饮食": f"根据生肖{zodiac}的体质特点，推荐适合的饮食习惯和3种有益食物",
        "家具布局": f"为生肖{zodiac}的{gender}性提供3条家居风水布局建议",
        "运动": f"推荐3种最适合生肖{zodiac}的{gender}性参与的运动锻炼方式",
        "花草绿植": f"推荐3种最适合生肖{zodiac}养护的植物，说明其风水作用",
        "电影": f"推荐2部最适合生肖{zodiac}的{gender}性观看的电影，并说明推荐理由"
    }
    
    prompt = prompts.get(recommendation_type, "")
    if not prompt:
        return "暂无该类型的推荐信息"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # 如果API调用失败，使用本地数据
        local_data = LOCAL_RECOMMENDATIONS.get(recommendation_type, {})
        return local_data.get(zodiac, f"暂时无法生成{recommendation_type}推荐，请稍后再试。")

def should_regenerate_fortune():
    """检查是否需要重新生成运势"""
    today = datetime.now().date()
    if st.session_state.last_fortune_date != today:
        st.session_state.last_fortune_date = today
        st.session_state.daily_fortune = None
        return True
    return False

def generate_daily_fortune(zodiac, birth_info):
    """生成今日运势"""
    try:
        prompt = f"""
        用户生肖：{zodiac}
        出生年份：{birth_info['year']}
        性别：{birth_info['gender']}
        当前日期：{datetime.now().strftime('%Y年%m月%d日')}
        
        生成简短精准的今日运势（60字左右），语言温暖、简洁。
        """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "今日运势平稳，保持积极心态，好事自然来。注意与人沟通，避免小误会。"

def chat_with_ai(user_message, birth_info, zodiac):
    """与AI聊天"""
    if not birth_info:
        return "请先在主页输入您的八字信息。"
    
    prompt = f"""
    用户信息：
    - 生肖：{zodiac}
    - 出生年份：{birth_info['year']}
    
    用户问题：{user_message}
    
    请基于用户的八字信息和生肖特点，给出专业、温暖的回答。
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "抱歉，我现在无法回答您的问题。请稍后再试。"

def render_chat_interface():
    """显示聊天界面"""
    st.subheader("💬 您还有什么想了解的吗？")
    
    # 显示聊天历史
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**👤 您：** {message['content']}")
        else:
            st.markdown(f"**🔮 运势助手：** {message['content']}")
    
    user_question = st.text_input("输入您的问题...", key="chat_input")
    if st.button("发送") and user_question.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        with st.spinner("🔮 正在思考..."):
            birth_info = st.session_state.birth_info
            zodiac = year_to_zodiac(birth_info['year']) if birth_info else "未知"
            ai_response = chat_with_ai(user_question, birth_info, zodiac)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        st.rerun()

# -------------------- 页面组件 --------------------
def render_home_page():
    st.title("🔮 八字塔罗运势")
    st.subheader("✨ 输入您的八字信息，探索专属运势")

    if not st.session_state.media_indexed:
        with st.spinner("📂 加载媒体资源..."):
            load_media_resources()

    with st.form("birth_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            birth_year = st.number_input("出生年份", min_value=1900, max_value=datetime.now().year, value=2000)
            birth_month = st.number_input("出生月份", min_value=1, max_value=12, value=1)
        with col2:
            birth_day = st.number_input("出生日期", min_value=1, max_value=31, value=1)
            birth_hour = st.selectbox("出生时辰", [
                "子时(23-1)", "丑时(1-3)", "寅时(3-5)", "卯时(5-7)", 
                "辰时(7-9)", "巳时(9-11)", "午时(11-13)", "未时(13-15)",
                "申时(15-17)", "酉时(17-19)", "戌时(19-21)", "亥时(21-23)"
            ])
        
        birth_place = st.text_input("出生地点", placeholder="例如：北京、上海")
        gender = st.selectbox("性别", options=["男", "女"])
        
        if st.form_submit_button("🚀 保存八字信息"):
            if birth_place.strip():
                st.session_state.birth_info = {
                    "year": birth_year, "month": birth_month, "day": birth_day,
                    "hour": birth_hour, "place": birth_place, "gender": gender
                }
                st.success("✅ 八字信息已保存！")
                st.session_state.daily_fortune = None
                st.session_state.personal_recommendations = {}
                st.session_state.chat_history = []
            else:
                st.warning("请输入出生地点")

    if st.session_state.birth_info:
        zodiac = year_to_zodiac(st.session_state.birth_info['year'])
        st.markdown(f"""
        <div class="zodiac-section">
            <h1>{get_zodiac_emoji(zodiac)} {zodiac}</h1>
            <h3>{get_zodiac_description(zodiac)}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 查看今日运势", use_container_width=True):
                st.session_state.current_page = "daily"
                st.rerun()
        with col2:
            if st.button("🌟 查看个性推荐", use_container_width=True):
                st.session_state.current_page = "personal"
                st.rerun()

def render_daily_fortune():
    st.title("📅 今日运势")
    
    if not st.session_state.birth_info:
        st.warning("请先在主页面输入八字信息")
        if st.button("返回主页"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    birth_info = st.session_state.birth_info
    zodiac = year_to_zodiac(birth_info['year'])
    
    # 个人生肖守护灵
    st.subheader("✨ 个人生肖守护灵")
    guardian_spirit = get_guardian_spirit(zodiac)
    st.markdown(f"""
    <div class="guardian-spirit">
        <h3>🌟 {guardian_spirit.split(' - ')[0]} 🌟</h3>
        <p>{guardian_spirit.split(' - ')[1]}</p>
    </div>
    """, unsafe_allow_html=True)

    # 今日运势
    st.subheader("🎯 今日运势")
    should_regenerate_fortune()
    
    if st.session_state.daily_fortune is None:
        with st.spinner("🔮 正在占卜今日运势..."):
            st.session_state.daily_fortune = generate_daily_fortune(zodiac, birth_info)

    st.info(st.session_state.daily_fortune)

    # 音乐推荐
    st.subheader("🎶 今日守护音乐")
    if st.session_state.songs_meta:
        matched_songs = match_song_by_text(st.session_state.daily_fortune, 1)
        if matched_songs:
            display_media(matched_songs[0][1], zodiac)

    render_chat_interface()
    
    if st.button("🔙 返回主页"):
        st.session_state.current_page = "home"
        st.rerun()

def render_personal_recommendation():
    st.title("🌟 个性推荐")
    
    if not st.session_state.birth_info:
        st.warning("请先在主页面输入八字信息")
        if st.button("返回主页"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    birth_info = st.session_state.birth_info
    zodiac = year_to_zodiac(birth_info['year'])
    
    # 推荐类型按钮
    st.subheader("🎯 选择推荐类型")
    
    recommendation_types = {
        "💼 工作类型": "工作类型",
        "🚗 车型推荐": "车型", 
        "🧭 工作方位": "工作方位",
        "🍽️ 饮食建议": "饮食",
        "🏠 家具布局": "家具布局",
        "🏃 运动推荐": "运动",
        "🌿 花草绿植": "花草绿植",
        "🎬 电影推荐": "电影"
    }
    
    # 创建按钮网格
    cols = st.columns(4)
    for idx, (display_name, rec_type) in enumerate(recommendation_types.items()):
        with cols[idx % 4]:
            if st.button(display_name, use_container_width=True, key=f"btn_{rec_type}"):
                st.session_state.recommendation_type = rec_type
                st.rerun()
    
    # 显示选中的推荐内容
    if st.session_state.recommendation_type:
        st.subheader(f"📋 {[k for k, v in recommendation_types.items() if v == st.session_state.recommendation_type][0]}")
        
        if st.session_state.recommendation_type in st.session_state.personal_recommendations:
            recommendation_content = st.session_state.personal_recommendations[st.session_state.recommendation_type]
        else:
            with st.spinner("🔮 正在生成推荐..."):
                recommendation_content = generate_specific_recommendation(
                    st.session_state.recommendation_type,
                    zodiac, birth_info['year'], birth_info['place'], 
                    birth_info['hour'], birth_info['gender']
                )
                st.session_state.personal_recommendations[st.session_state.recommendation_type] = recommendation_content
        
        st.markdown(f"""
        <div class="recommendation-card">
            {recommendation_content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👆 请选择上方的推荐类型来查看具体建议")

    render_chat_interface()
    
    if st.button("🔙 返回主页"):
        st.session_state.current_page = "home"
        st.rerun()

# -------------------- 主程序入口 --------------------
def main():
    # 设置背景视频
    if st.session_state.background_video is None:
        setup_background_video()
    
    # 页面路由
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "daily":
        render_daily_fortune()
    elif st.session_state.current_page == "personal":
        render_personal_recommendation()

if __name__ == "__main__":
    main()
