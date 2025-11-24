import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# yfinance 모듈 확인 및 설치 안내
try:
    import yfinance as yf
except ImportError:
    st.error("""
    **yfinance 모듈이 설치되어 있지 않습니다.**
    
    다음 명령어를 터미널에서 실행하여 설치해주세요:
    
    ```
    pip install yfinance
    ```
    
    또는 requirements.txt의 모든 패키지를 설치하려면:
    
    ```
    pip install -r requirements.txt
    ```
    """)
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="포스코 홀딩스 주가 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* 사이드바 헤더 스타일 */
    [data-testid="stSidebar"] [data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    /* 필터 섹션 스타일 */
    .filter-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    /* 라벨 스타일 */
    label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 컬럼 간격 조정 */
    [data-testid="column"] {
        padding: 0.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
st.markdown('<h1 class="main-header">📈 포스코 홀딩스 주가 대시보드</h1>', unsafe_allow_html=True)
st.markdown("---")

# 데이터 로드 함수
@st.cache_data(ttl=300)  # 5분마다 캐시 갱신
def load_stock_data(ticker, start_date, end_date):
    """주가 데이터를 가져오는 함수"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {str(e)}")
        return None

# 사이드바 설정
st.sidebar.markdown("""
    <div style='background: rgba(255, 255, 255, 0.15); padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem;'>
        <h2 style='color: white; text-align: center; margin: 0; font-size: 1.4rem;'>⚙️ 설정</h2>
    </div>
""", unsafe_allow_html=True)

# 티커 심볼
ticker = "005490.KS"  # 포스코 홀딩스
st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 0.8rem; border-radius: 10px; margin: 1rem 0;'>
        <p style='color: white; font-weight: bold; margin: 0; font-size: 1rem;'>🏢 종목 정보</p>
    </div>
""", unsafe_allow_html=True)
st.sidebar.info(f"**종목 코드:** {ticker}\n\n**회사명:** 포스코 홀딩스")

# 기간 선택
st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 0.8rem; border-radius: 10px; margin: 1rem 0;'>
        <p style='color: white; font-weight: bold; margin: 0; font-size: 1rem;'>📅 기간 선택</p>
    </div>
""", unsafe_allow_html=True)

# 빠른 선택 버튼
period_options = {
    "1개월": 30,
    "3개월": 90,
    "6개월": 180,
    "1년": 365,
    "2년": 730,
    "5년": 1825
}

selected_period = st.sidebar.selectbox(
    "기간 선택",
    options=list(period_options.keys()),
    index=2  # 기본값: 6개월
)

# 날짜 범위 계산
end_date = datetime.now()
start_date = end_date - timedelta(days=period_options[selected_period])

# 사용자 정의 날짜 선택
st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 0.8rem; border-radius: 10px; margin: 1rem 0;'>
        <p style='color: white; font-weight: bold; margin: 0; font-size: 1rem;'>📆 상세 기간 설정</p>
    </div>
""", unsafe_allow_html=True)

custom_date = st.sidebar.checkbox("사용자 정의 날짜 사용")
if custom_date:
    start_date = st.sidebar.date_input("시작 날짜", value=start_date)
    end_date = st.sidebar.date_input("종료 날짜", value=end_date)
    if start_date >= end_date:
        st.sidebar.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")
        st.stop()

# 기술적 지표 옵션
st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                padding: 0.8rem; border-radius: 10px; margin: 1rem 0;'>
        <p style='color: white; font-weight: bold; margin: 0; font-size: 1rem;'>📊 기술적 지표</p>
    </div>
""", unsafe_allow_html=True)

show_ma = st.sidebar.checkbox("이동평균선 표시", value=True)
ma_periods = []
if show_ma:
    ma_5 = st.sidebar.checkbox("5일 이동평균", value=False)
    ma_20 = st.sidebar.checkbox("20일 이동평균", value=True)
    ma_60 = st.sidebar.checkbox("60일 이동평균", value=False)
    ma_120 = st.sidebar.checkbox("120일 이동평균", value=False)
    
    if ma_5:
        ma_periods.append(5)
    if ma_20:
        ma_periods.append(20)
    if ma_60:
        ma_periods.append(60)
    if ma_120:
        ma_periods.append(120)

show_volume = st.sidebar.checkbox("거래량 표시", value=True)
chart_type = st.sidebar.radio("차트 유형", ["캔들스틱", "라인"], index=0)

# 데이터 로드
with st.spinner("주가 데이터를 불러오는 중..."):
    df = load_stock_data(ticker, start_date, end_date)

if df is None or df.empty:
    st.error("데이터를 불러올 수 없습니다. 인터넷 연결을 확인하거나 나중에 다시 시도해주세요.")
    st.stop()

# 데이터 전처리
df = df.sort_index()
df['MA_5'] = df['Close'].rolling(window=5).mean()
df['MA_20'] = df['Close'].rolling(window=20).mean()
df['MA_60'] = df['Close'].rolling(window=60).mean()
df['MA_120'] = df['Close'].rolling(window=120).mean()

# 기술적 지표 계산 함수
def calculate_rsi(prices, period=14):
    """RSI (Relative Strength Index) 계산"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """MACD (Moving Average Convergence Divergence) 계산"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

# 기술적 지표 계산
df['RSI'] = calculate_rsi(df['Close'], period=14)
df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df['Close'])

# 스토캐스틱 오실레이터 계산
def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """스토캐스틱 오실레이터 계산"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=d_period).mean()
    return k_percent, d_percent

df['Stoch_K'], df['Stoch_D'] = calculate_stochastic(df['High'], df['Low'], df['Close'])

# OBV (On-Balance Volume) 계산
df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

# 상승/하락 확률 계산 함수
def calculate_probability(df, lookback_period=20):
    """기술적 지표와 거래량을 기반으로 상승/하락 확률 계산"""
    if len(df) < lookback_period:
        lookback_period = len(df)
    
    # 최근 N일 데이터만 사용
    recent_df = df.tail(lookback_period).copy()
    
    # 각 지표별 상승 신호 점수 계산 (0-100)
    signals = {}
    
    # 1. RSI 신호 (30 이하: 강한 상승 신호, 70 이상: 강한 하락 신호)
    latest_rsi = recent_df['RSI'].iloc[-1]
    if pd.notna(latest_rsi):
        if latest_rsi < 30:
            signals['RSI'] = 80  # 강한 상승 신호
        elif latest_rsi < 40:
            signals['RSI'] = 65  # 상승 신호
        elif latest_rsi < 50:
            signals['RSI'] = 55  # 약한 상승 신호
        elif latest_rsi < 60:
            signals['RSI'] = 45  # 약한 하락 신호
        elif latest_rsi < 70:
            signals['RSI'] = 35  # 하락 신호
        else:
            signals['RSI'] = 20  # 강한 하락 신호
    else:
        signals['RSI'] = 50  # 중립
    
    # 2. MACD 신호
    latest_macd = recent_df['MACD'].iloc[-1]
    latest_signal = recent_df['MACD_Signal'].iloc[-1]
    latest_hist = recent_df['MACD_Hist'].iloc[-1]
    prev_hist = recent_df['MACD_Hist'].iloc[-2] if len(recent_df) > 1 else latest_hist
    
    if pd.notna(latest_macd) and pd.notna(latest_signal):
        if latest_macd > latest_signal and latest_hist > prev_hist:
            signals['MACD'] = 75  # 강한 상승 신호
        elif latest_macd > latest_signal:
            signals['MACD'] = 60  # 상승 신호
        elif latest_macd < latest_signal and latest_hist < prev_hist:
            signals['MACD'] = 25  # 강한 하락 신호
        elif latest_macd < latest_signal:
            signals['MACD'] = 40  # 하락 신호
        else:
            signals['MACD'] = 50  # 중립
    else:
        signals['MACD'] = 50
    
    # 3. 스토캐스틱 신호
    latest_stoch_k = recent_df['Stoch_K'].iloc[-1]
    latest_stoch_d = recent_df['Stoch_D'].iloc[-1]
    if pd.notna(latest_stoch_k) and pd.notna(latest_stoch_d):
        if latest_stoch_k < 20 and latest_stoch_k > latest_stoch_d:
            signals['Stochastic'] = 75  # 강한 상승 신호
        elif latest_stoch_k < 30:
            signals['Stochastic'] = 60  # 상승 신호
        elif latest_stoch_k > 80 and latest_stoch_k < latest_stoch_d:
            signals['Stochastic'] = 25  # 강한 하락 신호
        elif latest_stoch_k > 70:
            signals['Stochastic'] = 40  # 하락 신호
        else:
            signals['Stochastic'] = 50  # 중립
    else:
        signals['Stochastic'] = 50
    
    # 4. 이동평균선 신호
    latest_price = recent_df['Close'].iloc[-1]
    ma5 = recent_df['MA_5'].iloc[-1] if 'MA_5' in recent_df.columns else None
    ma20 = recent_df['MA_20'].iloc[-1] if 'MA_20' in recent_df.columns else None
    
    ma_score = 50
    if pd.notna(ma5) and pd.notna(ma20):
        if latest_price > ma5 > ma20:
            ma_score = 70  # 강한 상승 신호
        elif latest_price > ma5:
            ma_score = 60  # 상승 신호
        elif latest_price < ma5 < ma20:
            ma_score = 30  # 강한 하락 신호
        elif latest_price < ma5:
            ma_score = 40  # 하락 신호
    
    signals['MA'] = ma_score
    
    # 5. OBV 신호 (거래량 추세)
    if len(recent_df) > 1:
        obv_trend = recent_df['OBV'].iloc[-1] - recent_df['OBV'].iloc[-min(5, len(recent_df)-1)]
        price_trend = recent_df['Close'].iloc[-1] - recent_df['Close'].iloc[-min(5, len(recent_df)-1)]
        
        if obv_trend > 0 and price_trend > 0:
            signals['OBV'] = 70  # 상승 확인
        elif obv_trend < 0 and price_trend < 0:
            signals['OBV'] = 30  # 하락 확인
        elif obv_trend > 0 and price_trend < 0:
            signals['OBV'] = 45  # 약한 하락 (거래량은 증가)
        else:
            signals['OBV'] = 55  # 약한 상승
    else:
        signals['OBV'] = 50
    
    # 거래량 가중치 계산 (최근 거래량이 평균보다 높을수록 가중치 증가)
    recent_volumes = recent_df['Volume'].tail(5)
    avg_volume = recent_df['Volume'].mean()
    volume_weights = (recent_volumes / avg_volume).fillna(1.0).clip(0.5, 2.0).values
    
    # 각 지표별 가중치 (거래량이 높은 날의 신호에 더 높은 가중치)
    indicator_weights = {
        'RSI': 0.25,
        'MACD': 0.25,
        'Stochastic': 0.15,
        'MA': 0.20,
        'OBV': 0.15
    }
    
    # 거래량 가중 평균 계산
    weighted_scores = []
    total_weight = 0
    
    for indicator, base_weight in indicator_weights.items():
        if indicator in signals:
            # 최근 5일의 거래량 가중치 평균 적용
            volume_weight = np.mean(volume_weights) if len(volume_weights) > 0 else 1.0
            adjusted_weight = base_weight * volume_weight
            weighted_scores.append(signals[indicator] * adjusted_weight)
            total_weight += adjusted_weight
    
    if total_weight > 0:
        final_score = sum(weighted_scores) / total_weight
    else:
        final_score = 50
    
    # 확률로 변환 (0-100% 범위로 정규화)
    up_probability = max(0, min(100, final_score))
    down_probability = 100 - up_probability
    
    return up_probability, down_probability, signals

# 상승/하락 확률 계산
up_prob, down_prob, indicator_signals = calculate_probability(df, lookback_period=20)

# 현재가 및 주요 지표 계산
latest_price = df['Close'].iloc[-1]
previous_price = df['Close'].iloc[-2] if len(df) > 1 else latest_price
price_change = latest_price - previous_price
price_change_pct = (price_change / previous_price * 100) if previous_price != 0 else 0

# 추가 통계
max_price = df['High'].max()
min_price = df['Low'].min()
avg_volume = df['Volume'].mean()
latest_volume = df['Volume'].iloc[-1]

# 메인 대시보드
# KPI 지표
st.subheader("📊 주요 지표")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    change_color = "normal" if price_change >= 0 else "inverse"
    st.metric(
        "현재가",
        f"{latest_price:,.0f}원",
        f"{price_change:+,.0f}원 ({price_change_pct:+.2f}%)"
    )

with col2:
    st.metric("기간 최고가", f"{max_price:,.0f}원")

with col3:
    st.metric("기간 최저가", f"{min_price:,.0f}원")

with col4:
    st.metric("평균 거래량", f"{avg_volume:,.0f}")

with col5:
    st.metric("최근 거래량", f"{latest_volume:,.0f}")

st.markdown("---")

# 주가 차트
st.subheader("📈 주가 차트")

if chart_type == "캔들스틱":
    # 캔들스틱 차트
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('주가 (캔들스틱)', '거래량'),
        row_width=[0.7, 0.3]
    )
    
    # 캔들스틱
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="주가"
        ),
        row=1, col=1
    )
    
    # 이동평균선 추가
    ma_colors = {5: '#FF6B6B', 20: '#4ECDC4', 60: '#45B7D1', 120: '#FFA07A'}
    for period in ma_periods:
        if f'MA_{period}' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f'MA_{period}'],
                    name=f'{period}일 이동평균',
                    line=dict(color=ma_colors.get(period, '#999999'), width=2)
                ),
                row=1, col=1
            )
    
    # 거래량 (Area 차트로 변경)
    if show_volume:
        colors = ['rgba(255, 0, 0, 0.3)' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'rgba(0, 255, 0, 0.3)' 
                 for i in range(len(df))]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Volume'],
                name="거래량",
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(color='rgba(102, 126, 234, 0.8)', width=1),
                mode='lines'
            ),
            row=2, col=1
        )
    
    # 가격 범위 계산
    price_min = df['Low'].min()
    price_max = df['High'].max()
    price_range = price_max - price_min
    # 가격 범위의 약 2% 간격으로 눈금 설정
    tick_interval = max(price_range * 0.02, 1000)  # 최소 1000원 간격
    
    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="날짜", row=2, col=1)
    fig.update_yaxes(
        title_text="가격 (원)", 
        row=1, col=1,
        tickformat=',.0f',
        dtick=tick_interval,
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)'
    )
    fig.update_yaxes(title_text="거래량", row=2, col=1, tickformat=',.0f')
    
else:
    # 라인 차트
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('주가 (라인)', '거래량'),
        row_width=[0.7, 0.3]
    )
    
    # 종가 라인
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            name="종가",
            line=dict(color='#1f77b4', width=2)
        ),
        row=1, col=1
    )
    
    # 이동평균선 추가
    ma_colors = {5: '#FF6B6B', 20: '#4ECDC4', 60: '#45B7D1', 120: '#FFA07A'}
    for period in ma_periods:
        if f'MA_{period}' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f'MA_{period}'],
                    name=f'{period}일 이동평균',
                    line=dict(color=ma_colors.get(period, '#999999'), width=2)
                ),
                row=1, col=1
            )
    
    # 거래량 (Area 차트로 변경)
    if show_volume:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Volume'],
                name="거래량",
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)',
                line=dict(color='rgba(102, 126, 234, 0.8)', width=1),
                mode='lines'
            ),
            row=2, col=1
        )
    
    # 가격 범위 계산
    price_min = df['Low'].min()
    price_max = df['High'].max()
    price_range = price_max - price_min
    # 가격 범위의 약 2% 간격으로 눈금 설정
    tick_interval = max(price_range * 0.02, 1000)  # 최소 1000원 간격
    
    fig.update_layout(
        height=700,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="날짜", row=2, col=1)
    fig.update_yaxes(
        title_text="가격 (원)", 
        row=1, col=1,
        tickformat=',.0f',
        dtick=tick_interval,
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)'
    )
    fig.update_yaxes(title_text="거래량", row=2, col=1, tickformat=',.0f')

st.plotly_chart(fig, use_container_width=True)

# 추가 통계 및 분석
st.markdown("---")
st.subheader("📊 상세 통계")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 일일 수익률 분포")
    daily_returns = df['Close'].pct_change().dropna() * 100
    
    fig_returns = go.Figure()
    fig_returns.add_trace(
        go.Histogram(
            x=daily_returns,
            nbinsx=50,
            name="일일 수익률",
            marker_color='rgba(102, 126, 234, 0.7)'
        )
    )
    fig_returns.add_vline(
        x=daily_returns.mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"평균: {daily_returns.mean():.2f}%"
    )
    fig_returns.update_layout(
        title="",
        xaxis_title="일일 수익률 (%)",
        yaxis_title="빈도",
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig_returns, use_container_width=True)

with col2:
    st.markdown("#### 가격 변동성 (볼린저 밴드)")
    # 볼린저 밴드 계산
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
    
    fig_bb = go.Figure()
    
    # 볼린저 밴드
    fig_bb.add_trace(
        go.Scatter(
            x=df.index,
            y=df['BB_Upper'],
            name="상단 밴드",
            line=dict(color='rgba(255, 0, 0, 0.3)', width=1),
            showlegend=False
        )
    )
    fig_bb.add_trace(
        go.Scatter(
            x=df.index,
            y=df['BB_Lower'],
            name="하단 밴드",
            line=dict(color='rgba(255, 0, 0, 0.3)', width=1),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.1)',
            showlegend=False
        )
    )
    fig_bb.add_trace(
        go.Scatter(
            x=df.index,
            y=df['BB_Middle'],
            name="중간선 (20일 이동평균)",
            line=dict(color='blue', width=2)
        )
    )
    fig_bb.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            name="종가",
            line=dict(color='black', width=2)
        )
    )
    
    fig_bb.update_layout(
        title="",
        xaxis_title="날짜",
        yaxis_title="가격 (원)",
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig_bb, use_container_width=True)

# 통계 테이블
st.markdown("---")
st.subheader("📋 통계 요약")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 기본 통계")
    stats_df = pd.DataFrame({
        '지표': ['평균 종가', '표준편차', '최고가', '최저가', '평균 거래량'],
        '값': [
            f"{df['Close'].mean():,.0f}원",
            f"{df['Close'].std():,.0f}원",
            f"{df['High'].max():,.0f}원",
            f"{df['Low'].min():,.0f}원",
            f"{df['Volume'].mean():,.0f}"
        ]
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

with col2:
    st.markdown("#### 수익률 통계")
    returns_stats = pd.DataFrame({
        '지표': ['평균 일일 수익률', '수익률 표준편차', '최대 상승률', '최대 하락률', '총 수익률'],
        '값': [
            f"{daily_returns.mean():.2f}%",
            f"{daily_returns.std():.2f}%",
            f"{daily_returns.max():.2f}%",
            f"{daily_returns.min():.2f}%",
            f"{((df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100):.2f}%"
        ]
    })
    st.dataframe(returns_stats, use_container_width=True, hide_index=True)

# 데이터 테이블
st.markdown("---")
st.subheader("📋 주가 데이터")

show_data = st.checkbox("데이터 테이블 보기")
if show_data:
    # 한글 컬럼명으로 변환
    display_df = df.copy()
    
    # 컬럼명 매핑 딕셔너리
    column_mapping = {
        'Open': '시가',
        'High': '고가',
        'Low': '저가',
        'Close': '종가',
        'Volume': '거래량',
        'Dividends': '배당금',
        'Stock Splits': '주식분할',
        'MA_5': '5일 이동평균',
        'MA_20': '20일 이동평균',
        'MA_60': '60일 이동평균',
        'MA_120': '120일 이동평균',
        'BB_Middle': '볼린저 밴드 중간선',
        'BB_Std': '볼린저 밴드 표준편차',
        'BB_Upper': '볼린저 밴드 상단',
        'BB_Lower': '볼린저 밴드 하단'
    }
    
    # 존재하는 컬럼만 매핑
    display_df = display_df.rename(columns={col: column_mapping[col] 
                                            for col in display_df.columns 
                                            if col in column_mapping})
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # 데이터 다운로드 버튼
    csv = df.to_csv().encode('utf-8-sig')
    st.download_button(
        label="📥 주가 데이터 CSV 다운로드",
        data=csv,
        file_name=f"posco_holding_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; padding: 1rem;'>"
    "포스코 홀딩스 주가 대시보드 | Streamlit & yfinance로 제작 | 데이터는 Yahoo Finance에서 제공됩니다."
    "</div>",
    unsafe_allow_html=True
)

