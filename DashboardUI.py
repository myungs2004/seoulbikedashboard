import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

class DashboardUI:
    def __init__(self):
        pass

    #검색 사이드바
    def render_sidebar(self): 
        st.sidebar.header("🔍 대여소 검색 및 필터")
        search_keyword = st.sidebar.text_input("대여소 이름 검색", placeholder="예: 광운대역")
        min_bikes = st.sidebar.slider("최소 잔여 자전거 수", 0, 20, 5)
        status_filter = st.sidebar.selectbox("혼잡도 상태", ["전체", "여유", "보통", "부족"])
        if st.sidebar.button("새로고침"):
            st.rerun()
        return search_keyword, min_bikes, status_filter

    #통계영역
    #todo - 더미 데이터라 api 받아오면 삭제
    def show_metrics(self): 
        col1, col2, col3= st.columns(3)
        with col1:
            st.metric(label="전체 대여소 수", value="2,150개")
        with col2:
            st.metric(label="총 가동 자전거", value="14,820대")
        with col3:
            st.metric(label="평균 대여율", value="68.5%")

    #지도영역
    #todo - Folium map으로 개선 가능
    def show_map(self): 
        st.subheader("서울시 대여소 현황 지도 (Prototype)")
        map_data = pd.DataFrame(
            np.random.randn(50, 2) / [50, 50] + [37.5665, 126.9780],
            columns=['lat', 'lon']
        )
        st.map(map_data)


    # 테이블영역
     #todo - 더미 데이터라 api 받아오면 삭제
    def show_table(self): 
        st.subheader("대여소 상세 정보 목록")
        dummy_df = pd.DataFrame({
            "대여소 ID": [101, 102, 103, 104, 105],
            "대여소명": ["광운대역 3번출구", "석계역 1번출구", "월계이마트", "공릉역 2번출구", "태릉입구역"],
            "거치대 수": [15, 20, 10, 25, 15],
            "현재 자전거": [2, 14, 1, 18, 5],
            "상태": ["부족", "여유", "부족", "여유", "보통"]
        })
        st.dataframe(dummy_df, use_container_width=True)

    #차트영역
    #todo - api 연동되면 더미데이터 삭제
    def show_chart(self):
       
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("⚠️ 자전거 부족 대여소 TOP 10")
            
            top_shortage_df = pd.DataFrame({
                "stationName": ["광운대역 2번출구", "공릉역 1번출구", "월계역 3번출구", "석계역 2번출구", "태릉입구역 4번출구"],
                "parkingBikeTotCnt": [1, 2, 2, 3, 4]
            })

            fig_bar = px.bar(
                top_shortage_df,
                x="parkingBikeTotCnt",
                y="stationName",
                orientation="h",
                labels={"parkingBikeTotCnt": "잔여 자전거 수", "stationName": "대여소명"},
                template="plotly_white",
            )
            fig_bar.update_traces(marker_color="#ef4444") 
            fig_bar.update_layout(
                bargap=0.4,
                margin=dict(l=10, r=10, t=20, b=20),
                yaxis=dict(autorange="reversed") 
            )
            st.plotly_chart(fig_bar, width="stretch")

        with col_right:
            st.subheader("📊 대여소 혼잡도 상태 비율")

            status_df = pd.DataFrame({
                "status": ["여유", "보통", "부족"],
                "count": [45, 35, 20]
            })

            fig_pie = px.pie(
                status_df,
                names="status",
                values="count",
                hole=0.5, 
                template="plotly_white",
                color="status",
                color_discrete_map={
                    "여유": "#10b981", 
                    "보통": "#f59e0b", 
                    "부족": "#ef4444"
                }
            )
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, width="stretch")

    def run(self):
        # 페이지 기본 설정
        st.set_page_config(
            page_title="서울시 따릉이 대여정보 대시보드",
            page_icon="🚲",
            layout="wide"
        )
        
        st.title("🚲 서울시 공공자전거 따릉이 대여정보 대시보드")
        st.markdown("---")

        # 각 메서드 호출 실행
        self.render_sidebar()
        self.show_metrics()
        st.markdown("---")

        # todo - 도표나 그래프 추가!
        tab1, tab2,tab3 = st.tabs(["🗺️ 대여소 지도", "📊 데이터 테이블", "📈 차트"])
        with tab1:
            self.show_map()
        with tab2:
            self.show_table()
        with tab3:
            self.show_chart()


if __name__ == "__main__":
    ui = DashboardUI()
    ui.run()
