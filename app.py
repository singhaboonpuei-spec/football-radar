import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Pro Quant Radar", layout="wide")

# UI ส่วนหัว
st.markdown("# 🎯 PRO QUANT RADAR V.1")
st.markdown("---")

# ฟังก์ชันดึงข้อมูลแบบสะอาด
@st.cache_data(ttl=3600)
def get_data():
    url = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
    df = pd.read_csv(url)
    # เลือกเฉพาะคอลัมน์ที่จำเป็น
    cols = ['HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A']
    df = df[cols].dropna()
    return df

# ฟังก์ชันคำนวณความน่าจะเป็น (Poisson)
def calculate_poisson_probs(home_xg, away_xg):
    home_win = 0
    draw = 0
    away_win = 0
    for i in range(0, 6): # สกอร์ 0-5
        for j in range(0, 6):
            prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)
            if i > j: home_win += prob
            elif i == j: draw += prob
            else: away_win += prob
    return home_win, draw, away_win

# ส่วนหลักของโปรแกรม
df = get_data()

st.sidebar.header("Settings")
min_edge = st.sidebar.slider("กรองค่าความได้เปรียบ (Edge %)", 0.0, 20.0, 5.0)

# ประมวลผล
results = []
for idx, row in df.tail(20).iterrows(): # เอาแค่ 20 คู่ล่าสุดเพื่อความเร็ว
    # สมมติฐานค่า xG (ในระบบจริง เราจะดึงจากสถิติเฉลี่ย)
    h_xg, a_xg = 1.6, 1.2 
    h_win, draw, a_win = calculate_poisson_probs(h_xg, a_xg)
    
    # คำนวณราคาที่ควรจะเป็น (Fair Odds)
    fair_odds = 1 / h_win
    actual_odds = float(row['B365H'])
    edge = (actual_odds / fair_odds - 1) * 100
    
    results.append({
        "Match": f"{row['HomeTeam']} vs {row['AwayTeam']}",
        "Bookie Odds": actual_odds,
        "AI Win %": round(h_win * 100, 1),
        "Edge %": round(edge, 1),
        "Signal": "🟢 VALUE" if edge >= min_edge else "⚪ PASS"
    })

res_df = pd.DataFrame(results)

# แสดงผลแบบตารางที่แต่งสีได้
st.dataframe(
    res_df.style.map(lambda x: 'background-color: #059669; color: white' if x == "🟢 VALUE" else '', subset=['Signal']),
    use_container_width=True
)

st.success(f"สแกนเรียบร้อย พบสัญญาณการลงทุน {len(res_df[res_df['Signal']=='🟢 VALUE'])} คู่")