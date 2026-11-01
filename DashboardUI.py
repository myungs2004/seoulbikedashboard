import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium

class DashboardUI:
    def __init__(self):
        self.colors = {"부족": "#e8333f", "보통": "#f59f00", "여유": "#0ca678"}

    #검색 사이드바
    def render_sidebar(self): 
        st.sidebar.header("대여소 검색")
        search_keyword = st.sidebar.text_input("대여소 이름 검색", placeholder="예: 광운대역")
        min_bikes = st.sidebar.slider("최소 잔여 자전거 수", 0, 20, 5)
        status_filter = st.sidebar.selectbox("혼잡도 상태", ["전체", "여유", "보통", "부족"])
        if st.sidebar.button("새로고침"):
            st.rerun()
        return search_keyword, min_bikes, status_filter

    #통계영역
    #todo - 더미 데이터라 api 받아오면 삭제
    def show_metrics(self, summary):
        with st.container(horizontal=True):
            st.metric("전체 대여소", f"{summary['total_stations']:,}개", border=True)
            st.metric("이용 가능 자전거", f"{summary['total_bikes']:,}대", border=True)
            st.metric("총 거치대", f"{summary['total_racks']:,}개", border=True)
            st.metric("평균 대여율", f"{summary['avg_rate']:.1f}%", border=True)
        
    #지도영역
    #todo - Folium map으로 개선 가능
    def show_map(self, df):
        #st.subheader("한눈에 보는 대여소")
        center = [df["stationLatitude"].mean(), df["stationLongitude"].mean()]
        station_map = folium.Map(location=center, zoom_start=14, scroll_wheel_zoom="center")
        folium.TileLayer("OpenStreetMap", max_zoom=18).add_to(station_map)
        station_map.get_root().header.add_child(folium.Element(
        "<style>.leaflet-tile-pane { filter: saturate(0.8) brightness(1.12); opacity: 0.6; } .leaflet-interactive { filter: drop-shadow(0 1px 2px rgba(0,0,0,0.35)); }</style>"
        ))        
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["stationLatitude"], row["stationLongitude"]],
                radius=9,
                color="white",
                weight=1.5,
                fill=True,
                fill_color=self.colors[row["status"]],
                fill_opacity=1,
                popup=folium.Popup(
                    f"""
                    <div style="font-size:13px; line-height:1.6;">
                        <b style="font-size:15px;">{row['stationName']}</b><br>
                        자전거 {row['parkingBikeTotCnt']}대 / 거치대 {row['rackTotCnt']}개<br>
                        상태: {row['status']}
                    </div>
                    """,
                    min_width=180,
                    max_width=250,
                ),            
                ).add_to(station_map)
        station_map.get_root().script.add_child(folium.Element(
            f"""
            window.addEventListener("load", function () {{
                var map = {station_map.get_name()};
                function resize() {{
                    var r = Math.max(3, Math.min(11, map.getZoom() - 5));
                    map.eachLayer(function (layer) {{
                        if (layer instanceof L.CircleMarker) {{ layer.setRadius(r); }}
                    }});
                }}
                map.on("zoomend", resize);
                resize();
            }});
        """))            
        st.iframe(station_map.get_root().render(), height=260)


    # 테이블영역
     #todo - 더미 데이터라 api 받아오면 삭제
    def show_table(self, df):
        table = df[["stationName", "rackTotCnt", "parkingBikeTotCnt", "rate", "status"]]
        table = table.rename(columns={
            "stationName": "대여소",
            "rackTotCnt": "거치대",
            "parkingBikeTotCnt": "자전거",
            "rate": "대여율(%)",
            "status": "상태",
        })
        st.dataframe(table, width="stretch", hide_index=True, height=210)

    #차트영역
    #todo - api 연동되면 더미데이터 삭제
    def show_chart(self, df):
       
        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True, key="card_bar"):
                st.markdown("##### 자전거 부족 대여소")
                
                top_shortage_df = df.nsmallest(10, "parkingBikeTotCnt")
                
                fig_bar = px.bar(
                    top_shortage_df,
                    color="status",
                    color_discrete_map=self.colors,
                    x="parkingBikeTotCnt",
                    y="stationName",
                    orientation="h",
                    labels={"parkingBikeTotCnt": "잔여 자전거 수", "stationName": ""},
                    template="plotly_white",
                )
                for _, row in top_shortage_df.iterrows():
                    fig_bar.add_annotation(
                        x=0, xref="paper", y=row["stationName"],
                        text=row["stationName"],
                        showarrow=False, xanchor="left", xshift=-130,
                        font=dict(size=14, color="#1c2420"),
                    )                    
                    fig_bar.add_annotation(
                        x=1, xref="paper", y=row["stationName"],
                        text=str(row["parkingBikeTotCnt"]),
                        showarrow=False, xanchor="right", xshift=30,
                        font=dict(size=14, color="#1c2420"),
                    )
                fig_bar.update_layout(
                    height=135,
                    bargap=0.72,
                    barcornerradius="50%",
                    showlegend=False,
                    margin=dict(l=130, r=30, t=10, b=0),
                    xaxis=dict(visible=False),
                    yaxis=dict(autorange="reversed", visible=False),
                )
                st.plotly_chart(fig_bar, width="stretch")

        with col_right:
            with st.container(border=True, key="card_pie"):
                st.markdown("##### 혼잡도 비율")
                status_df = df["status"].value_counts().reindex(["부족", "보통", "여유"], fill_value=0).reset_index()
                total = status_df["count"].sum()
                fig_pie = px.pie(
                    status_df,
                    names="status",
                    values="count",
                    hole=0.7, 
                    template="plotly_white",
                    color="status",
                    color_discrete_map=self.colors,
                )
                fig_pie.update_traces(sort=False, textinfo="none", direction="clockwise")
                fig_pie.update_traces(sort=False, textinfo="none", direction="clockwise", domain=dict(x=[0, 0.5]))
                for i, (s, c) in enumerate(zip(status_df["status"], status_df["count"])):
                    fig_pie.add_annotation(
                        x=0.55, y=0.75 - i * 0.25, xref="paper", yref="paper",
                        text=f"<span style='color:{self.colors[s]}'>●</span> {s} {c / total * 100:.0f}%",
                        showarrow=False, xanchor="left",
                        font=dict(size=15, color="#1c2420"),
                    )                
                fig_pie.update_layout(height=135, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_pie, width="stretch")
                
    def get_dummy_data(self):
        return pd.DataFrame({
            "stationName": ["광운대역 3번출구", "석계역 1번출구", "월계이마트", "공릉역 2번출구", "태릉입구역"],
            "stationLatitude": [37.6243, 37.6152, 37.6268, 37.6255, 37.6176],
            "stationLongitude": [127.0612, 127.0659, 127.0552, 127.0729, 127.0749],
            "rackTotCnt": [15, 20, 10, 25, 15],
            "parkingBikeTotCnt": [2, 14, 1, 18, 5],
            "rate": [13, 70, 10, 72, 33],
            "status": ["부족", "여유", "부족", "여유", "보통"],
        })
    
    def get_dummy_summary(self, df):
        return {
            "total_stations": len(df),
            "total_bikes": int(df["parkingBikeTotCnt"].sum()),
            "total_racks": int(df["rackTotCnt"].sum()),
            "avg_rate": float(df["rate"].mean()),
        }
    
    def apply_style(self):
        st.html(
            """<style>
            [data-testid="stMainBlockContainer"]{padding-top:2rem;padding-bottom:0;}
            [data-testid="stMetric"] > div {padding:8px 16px !important;}
            h1{font-size:1.75rem !important;padding-top:0 !important;}
            [data-testid="stMetricValue"]{font-size:1.6rem !important;font-weight:700 !important;line-height:1.2 !important;}
            [data-testid="stMetricLabel"] p{font-size:0.8rem !important;color:#5d6a62 !important;}            [data-testid="stHeader"]{background:transparent;}
            [data-testid="stColumn"]:has([class*="st-key-card"]) > [data-testid="stVerticalBlock"],
            [data-testid="stLayoutWrapper"]:has(> [class*="st-key-card"]),
            [class*="st-key-card"] {height:100%;}
            @media (max-width: 1000px) {
            [data-testid="stHorizontalBlock"]:has([class*="st-key-card"]) {flex-direction:column;}
            [data-testid="stHorizontalBlock"]:has([class*="st-key-card"]) > [data-testid="stColumn"] {width:100% !important; flex:1 1 100% !important;}
            }
            @media (max-width: 640px) {
            .stApp {background:#f4f7f4;}
            [data-testid="stMainBlockContainer"] {padding-top:4rem;}
            h1 {font-size:1.6rem !important;}
            [data-testid="stMetric"], [class*="st-key-card"] {background:#ffffff; border:none !important; border-radius:20px !important;}
            [data-testid="stMetric"] {flex:1 1 calc(50% - 8px) !important; min-width:calc(50% - 8px) !important;}
            iframe.stIFrame {border-radius:20px;}
            }
            </style>"""
        )    
    
    def run(self):
        # 페이지 기본 설정
        st.set_page_config(
            page_title="서울시 따릉이 대여정보 대시보드",
            page_icon="🚲",
            layout="wide"
        )
        self.apply_style()

        st.title("서울시 공공자전거 대여 현황")

        # 각 메서드 호출 실행
        self.render_sidebar()
        df = self.get_dummy_data()
        self.show_metrics(self.get_dummy_summary(df))

        # todo - 도표나 그래프 추가!
        self.show_map(df)
        tab_chart, tab_table = st.tabs(["차트", "대여소 목록"])
        with tab_chart:
                self.show_chart(df)
        with tab_table:
                self.show_table(df)

if __name__ == "__main__":
    ui = DashboardUI()
    ui.run()
