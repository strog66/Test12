import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar
from pyecharts import options as opts
from matplotlib import pyplot as plt
import plotly.express as px
import pandas as pd
# 配置 Streamlit 页面
st.set_page_config(page_title="文章词频分析与可视化", layout="wide")

# 定义函数：抓取网页文本内容
def fetch_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        body_text = soup.body.get_text(separator="\n", strip=True)
        return body_text
    except Exception as e:
        st.error(f"抓取内容失败: {e}")
        return ""

# 定义函数：分词与词频统计
def analyze_text(text, min_freq=1):
    words = jieba.lcut(text)
    filtered_words = [word for word in words if len(word) > 1]
    word_counts = Counter(filtered_words)
    filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
    return filtered_word_counts

# 定义函数：使用 Pyecharts 绘制词云图
def create_pyecharts_wordcloud(word_counts):
    wordcloud = (
        WordCloud()
        .add("", [list(item) for item in word_counts.items()], word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    )
    return wordcloud

# 定义函数：使用 Pyecharts 绘制柱状图
def create_pyecharts_bar_chart(word_counts):
    bar = (
        Bar()
        .add_xaxis(list(word_counts.keys()))
        .add_yaxis("词频", list(word_counts.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
    )
    return bar
# 定义函数：使用 Matplotlib 绘制折线图
def create_matplotlib_line_chart(word_counts):
    plt.figure(figsize=(10, 6))
    words = list(word_counts.keys())
    counts = list(word_counts.values())
    plt.plot(words, counts, marker='o', linestyle='-', color='b')
    plt.xlabel("词汇")  # 设置 x 轴标签
    plt.ylabel("词频")  # 设置 y 轴标签
    plt.title("词频折线图", fontsize=16)  # 设置标题，增加字体大小
    plt.xticks(rotation=45)  # 旋转 x 轴标签，避免重叠
    plt.tight_layout()  # 调整布局，防止标题或标签被遮挡
    st.pyplot(plt)  # 将绘制的图表嵌入到 Streamlit 应用中

# 定义函数：使用 Matplotlib 绘制散点图
def create_matplotlib_scatter_chart(word_counts):
    plt.figure(figsize=(10, 6))
    words = list(word_counts.keys())
    counts = list(word_counts.values())
    plt.scatter(words, counts, color='green')
    plt.xlabel("词汇")
    plt.ylabel("词频")
    plt.title("词频散点图")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
# 定义函数：使用 Plotly 绘制饼图
def create_plotly_pie_chart(word_counts):
    words = list(word_counts.keys())
    counts = list(word_counts.values())
    fig = px.pie(values=counts, names=words, title="词频饼图")
    st.plotly_chart(fig)

# 定义函数：使用 Plotly 绘制漏斗图
def create_plotly_funnel_chart(word_counts):
    data = pd.DataFrame({"词汇": list(word_counts.keys()), "词频": list(word_counts.values())})
    fig = px.funnel(data, x='词频', y='词汇', title="词频漏斗图")
    st.plotly_chart(fig)

# 定义函数：使用 Plotly 绘制雷达图
def create_plotly_radar_chart(word_counts):
    words = list(word_counts.keys())[:7]
    counts = list(word_counts.values())[:7]
    data = pd.DataFrame({"指标": words, "值": counts})
    fig = px.line_polar(data, r='值', theta='指标', line_close=True, title="词频雷达图")
    st.plotly_chart(fig)

# Streamlit 应用主体
st.title("文章词频分析与可视化")

# 用户输入文章 URL
url = st.text_input("请输入文章 URL:", value="")
# 词频最低过滤值
min_freq = st.sidebar.slider("设置最低词频过滤值:", min_value=1, max_value=100, value=1, step=1)

# 图表类型选择
chart_type = st.sidebar.selectbox(
    "选择图表类型:",
    ["词云图", "柱状图", "折线图",
     "散点图", "饼图", "漏斗图", "雷达图"]
)

# 抓取和分析文本
if url:
    st.write(f"正在分析 URL: {url}")
    text = fetch_text_from_url(url)
    if text:
        word_counts = analyze_text(text, min_freq)
        top_20_words = dict(Counter(word_counts).most_common(20))
        st.write("词频排名前 20 的词汇:")
        st.write(top_20_words)

        # 根据选择绘制图表
        if chart_type == "词云图":
            from streamlit_echarts import st_pyecharts
            chart = create_pyecharts_wordcloud(top_20_words)
            st_pyecharts(chart)
        elif chart_type == "柱状图":
            from streamlit_echarts import st_pyecharts
            chart = create_pyecharts_bar_chart(top_20_words)
            st_pyecharts(chart)
        elif chart_type == "折线图":
            create_matplotlib_line_chart(top_20_words)
        elif chart_type == "散点图":
            create_matplotlib_scatter_chart(top_20_words)
        elif chart_type == "饼图":
            create_plotly_pie_chart(top_20_words)
        elif chart_type == "漏斗图":
            create_plotly_funnel_chart(top_20_words)
        elif chart_type == "雷达图":
            create_plotly_radar_chart(top_20_words)
    else:
        st.error("未能成功抓取文章内容。")
