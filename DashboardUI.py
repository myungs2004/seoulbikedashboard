import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from datetime import datetime
from zoneinfo import ZoneInfo
from DataFetcher import DataFetcher
from DataProcessor import DataProcessor
from StationFilter import StationFilter


class DashboardUI:
    def __init__(self):
        self.colors = {"부족": "#e8333f", "보통": "#f59f00", "여유": "#0ca678"}

    #필터 초기화 버튼: 검색어/혼잡도/최소 자전거 수를 기본값으로 되돌림
    def reset_filters(self):
        st.session_state["search"] = ""
        st.session_state["status"] = "전체"
        st.session_state["min_bikes"] = 0    
        st.session_state["prev_summary"] = None        

    #검색 사이드바
    def render_sidebar(self):
        with st.sidebar.container(key="filter_card"):
            st.subheader("대여소 검색 및 필터")
            search_keyword = st.text_input("대여소 검색", placeholder="대여소 검색 (예: 광운대역)", key="search", label_visibility="collapsed", on_change=self.clear_snapshot)
            status_filter = st.pills("혼잡도 상태", ["전체", "부족", "보통", "여유"], default="전체", key="status", label_visibility="collapsed", on_change=self.clear_snapshot)
            min_bikes = st.slider("최소 잔여 자전거 수", 0, 30, 3, key="min_bikes", on_change=self.clear_snapshot)
            if st.button("필터 초기화", type="primary", width="stretch", on_click=self.reset_filters):
                st.rerun()
        return search_keyword, min_bikes, status_filter or "전체"
    
    #새로고침 직전 숫자를 저장 (변화 표시 비교용)
    def save_snapshot(self):
        st.session_state["prev_summary"] = st.session_state.get("cur_summary")

    #필터가 바뀌면 변화 표시를 지움
    def clear_snapshot(self):
        st.session_state["prev_summary"] = None

    #검색 필터 카드 (검색어, 혼잡도, 최소 자전거 수, 필터 초기화)
    def get_delta(self, summary, key):
        prev = st.session_state.get("prev_summary")
        if prev is None:
            return None
        diff = summary[key] - prev[key]
        if diff == 0:
            return None
        return diff    

    #통계영역 + 새로고침 대비 변화 표시
    def show_metrics(self, summary):
        bikes_delta = self.get_delta(summary, "total_bikes")
        rate_delta = self.get_delta(summary, "avg_rate")        
        with st.container(horizontal=True, key="metrics", width="content"):
            st.metric("전체 대여소", f"{summary['total_stations']:,}", border=True)
            st.metric("이용 가능 자전거", f"{summary['total_bikes']:,}", delta=None if bikes_delta is None else f"{bikes_delta:+,}", border=True)
            st.metric("총 거치대", f"{summary['total_racks']:,}", border=True)
            st.metric("평균 대여율", f"{summary['avg_rate']:.1f}%", delta=None if rate_delta is None else f"{rate_delta:+.1f}%p", border=True)
        st.session_state["cur_summary"] = summary

    #지도영역
    def show_map(self, df):
        if df is None or df.empty or 'stationLatitude' not in df.columns or 'stationLongitude' not in df.columns:
            st.info("조건에 일치하는 대여소가 없습니다")
            return
        map_df = df.dropna(subset=["stationLatitude", "stationLongitude"])
        if map_df.empty:
            st.info("유효한 위치 정보가 없습니다.")
            return

        center = [df["stationLatitude"].mean(), df["stationLongitude"].mean()]
        station_map = folium.Map(location=center, zoom_start=14, scroll_wheel_zoom="center")
        folium.TileLayer("OpenStreetMap", max_zoom=18).add_to(station_map)
        station_map.get_root().header.add_child(folium.Element("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
        <style>
        .leaflet-popup.flip{bottom:auto !important;top:14px;}
        .leaflet-popup.flip .leaflet-popup-tip-container{top:-20px;transform:rotate(180deg);}                                                               
        .leaflet-tile-pane{filter:saturate(0.8) brightness(1.12);opacity:0.6;}
        .leaflet-interactive{filter:drop-shadow(0 1px 2px rgba(0,0,0,0.35));}                                                           
        .leaflet-popup-content-wrapper{border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.12);}
        .leaflet-popup-content{margin:14px 18px;}
        .leaflet-popup.flip{bottom:auto !important;top:14px;}
        .leaflet-top.leaflet-left{top:auto;bottom:24px;}                                                               
        .leaflet-popup.flip .leaflet-popup-tip-container{top:-20px;transform:rotate(180deg);}
        </style>
        """))
        chip = {"부족": ("#fde7e8", "#c92a35"), "보통": ("#fff1d6", "#b36b00"), "여유": ("#dcf5ec", "#087f5b")}        
        for _, row in df.iterrows():
            bg, fg = chip[row["status"]]
            popup_html = f"""<div style="font-family:Pretendard, sans-serif;">
            <div style="font-size:16px;font-weight:700;color:#1c2420;margin:2px 0 6px;">{row['stationName']}</div>
            <span style="display:inline-block;padding:2px 8px;border-radius:6px;font-size:12px;background:{bg};color:{fg};">{row['status']}</span>
            <div style="font-size:12px;color:#1c2420;margin-top:8px;">잔여 {row['parkingBikeTotCnt']}대 · 거치대 {row['rackTotCnt']}개 · 대여율 {row['rate']}%</div>
            </div>"""
            folium.CircleMarker(
                location=[row["stationLatitude"], row["stationLongitude"]],
                radius=9,
                color="white",
                weight=1.5,
                fill=True,
                fill_color=self.colors[row["status"]],
                fill_opacity=1,
                popup=folium.Popup(popup_html, min_width=200, max_width=260, auto_pan=False),            
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
        station_map.get_root().script.add_child(folium.Element(f"""
        window.addEventListener("load", function () {{
            var map = {station_map.get_name()
            };
        map.on("popupopen", function (e) {{
            var box = e.popup.getElement();
            box.classList.remove("flip");
            var point = map.latLngToContainerPoint(e.popup.getLatLng());
            var size = map.getSize();
            var cardsLeft = size.x > 700 ? size.x - 650 : 0;
            var hitsCards = point.y - box.offsetHeight - 20 < 100 && point.x + box.offsetWidth / 2 > cardsLeft;
            var fitsBelow = point.y + box.offsetHeight + 20 < size.y;
            if (hitsCards && fitsBelow) {{
                box.classList.add("flip");
            }}
        }});
    }});
    """))                           
        st.iframe(station_map.get_root().render(), height=340)
        legend_items = "".join(
            f'<span><i style="background:{color};"></i>{status}</span>'
            for status, color in self.colors.items()
        )
        with st.container(key="legend"):
            st.html(f'<div class="legend">{legend_items}</div>')        


    # 테이블영역
    def show_table(self, df):
        table = df[["stationId","stationName", "rackTotCnt", "parkingBikeTotCnt", "rate", "status"]].copy()
        table["status"] = table["status"].apply(lambda s: [s])
        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
            height=210,
            column_config={
                "stationId": st.column_config.TextColumn("대여소 ID"),
                "stationName": st.column_config.TextColumn("대여소명"),
                "rackTotCnt": st.column_config.NumberColumn("거치대 수", format="%d개"),
                "parkingBikeTotCnt": st.column_config.NumberColumn("현재 자전거", format="%d대"),
                "rate": st.column_config.ProgressColumn("대여 가능률", format="%d%%", min_value=0, max_value=100, color="#1e7a46"),
                "status": st.column_config.MultiselectColumn("상태", options=["부족", "보통", "여유"], color=["#fde7e8", "#fff1d6", "#dcf5ec"]),
            },
        )

    #차트영역
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
                        showarrow=False, xanchor="left", xshift=-125,
                        font=dict(size=13, color="#1c2420"),
                    )                    
                    fig_bar.add_annotation(
                        x=1, xref="paper", y=row["stationName"],
                        text=str(row["parkingBikeTotCnt"]),
                        showarrow=False, xanchor="right", xshift=25,
                        font=dict(size=13, color="#1c2420"),
                    )
                fig_bar.update_layout(
                    height=220,
                    bargap=0.3,
                    barcornerradius="50%",
                    showlegend=False,
                    margin=dict(l=130, r=30, t=10, b=0),
                    xaxis=dict(range=[-8,20],visible=False, fixedrange=True),
                    yaxis=dict(autorange="reversed", visible=False, fixedrange=True),
                    dragmode=False,
                )
                fig_bar.update_traces(hovertemplate="%{y}<br>잔여 %{x}대<extra></extra>")
                st.plotly_chart(fig_bar, width="stretch", config={"displayModeBar": False})

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
                fig_pie.update_layout(height=220, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                fig_pie.update_traces(hovertemplate="%{label} %{value}곳 (%{percent:.0%})<extra></extra>")
                st.plotly_chart(fig_pie, width="stretch", config={"displayModeBar": False})

    
    #페이지 전체 디자인(CSS) 적용
    def apply_style(self):
        st.html(
            """<style>
            [data-testid="stMainBlockContainer"]{padding-top:2rem;padding-bottom:0;}
            [data-testid="stMetric"] > div {padding:8px 16px !important;}
            [data-testid="stMetric"] > div{display:flex;flex-wrap:wrap;align-items:center;column-gap:8px;}
            [data-testid="stMetricLabel"]{flex-basis:100%;}
            h1{font-size:1.75rem !important;padding-top:0 !important;}
            [data-testid="stMetricValue"]{font-size:1.6rem !important;font-weight:700 !important;line-height:1.2 !important;}
            [data-testid="stMetricLabel"] p{font-size:0.8rem !important;color:#5d6a62 !important;}
            [data-testid="stHeader"]{background:transparent;}
            .st-key-filter_card [data-testid="stSlider"] [role="group"] > div > div:first-child{height:5px !important;border-radius:999px;}
            .st-key-filter_card [data-testid="stSlider"] [role="group"] > div > div:nth-child(2){width:18px !important;height:18px !important;border:3px solid #ffffff;box-shadow:0 1px 4px rgba(0,0,0,0.3);}            
            .st-key-filter_card{background:#ffffff;border-radius:16px;padding:20px 14px;box-shadow:0 2px 12px rgba(0,0,0,0.08);}
            .st-key-filter_card [data-testid="stTextInputRootElement"]{border-radius:999px !important;background:#f4f7f4 !important;}
            .st-key-filter_card input{background:transparent !important;}
            .st-key-filter_card button[data-variant="pills"]{padding:4px 9px !important;min-width:0 !important;}
            .st-key-filter_card button[aria-checked="true"]{background:#1e7a46 !important;border-color:#1e7a46 !important;color:#ffffff !important;}
            .st-key-filter_card button[aria-checked="true"] p{color:#ffffff !important;}
            @media (min-width: 1001px) {
            [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"]{display:none !important;}
            [data-testid="stSidebar"]{transform:none !important;width:300px !important;min-width:300px !important;max-width:300px !important;}
            }
            [data-testid="stLayoutWrapper"]:has(> .st-key-metrics){height:0;margin-bottom:-1rem;margin-left:auto;z-index:10;}
            .st-key-metrics{position:relative;top:12px;right:12px;gap:8px;}
            .st-key-metrics [data-testid="stMetric"]{min-width:0;border:none !important;}
            .st-key-metrics > [data-testid="stElementContainer"]{flex:0 0 150px;width:150px;}            .st-key-metrics [data-testid="stMetric"] > div{background:#ffffff;border:none !important;border-radius:12px !important;box-shadow:0 4px 20px rgba(0,0,0,0.08);}
            [data-testid="stColumn"]:has([class*="st-key-card"]) > [data-testid="stVerticalBlock"],
            [data-testid="stLayoutWrapper"]:has(> [class*="st-key-card"]),
            [class*="st-key-card"] {height:100%;}
            [data-testid="stMainBlockContainer"]{container-type:inline-size;}
            @container (max-width: 700px) {
            [data-testid="stLayoutWrapper"]:has(> .st-key-metrics){margin-left:0;width:100%;}
            .st-key-metrics{left:8px;right:auto;top:8px;width:calc(100% - 16px) !important;gap:6px;align-items:stretch !important;}
            .st-key-metrics > [data-testid="stElementContainer"]{flex:1 1 0;min-width:0;}
            .st-key-metrics [data-testid="stMetric"]{min-width:0;}
            .st-key-metrics > [data-testid="stElementContainer"] > [data-testid="stMetric"], .st-key-metrics [data-testid="stMetric"] > div{height:100%;box-sizing:border-box;}
            .st-key-metrics [data-testid="stMetric"] > div{padding:6px 10px !important;}
            .st-key-metrics [data-testid="stMetricLabel"] p{font-size:0.7rem !important;white-space:normal;word-break:keep-all;line-height:1.2;}
            .st-key-metrics [data-testid="stMetricLabel"]{min-height:0 !important;}
            .st-key-metrics [data-testid="stMetricValue"]{font-size:1.15rem !important;}
            }
            @media (max-width: 1000px) {
            [data-testid="stHorizontalBlock"]:has([class*="st-key-card"]) {flex-direction:column;}
            [data-testid="stHorizontalBlock"]:has([class*="st-key-card"]) > [data-testid="stColumn"] {width:100% !important; flex:1 1 100% !important;}
            }
            @media (max-width: 640px) {
            [class*="st-key-card"] {background:#ffffff; border:none !important; border-radius:20px !important;}
            [data-testid="stMetric"] {flex:1 1 calc(50% - 8px) !important; min-width:calc(50% - 8px) !important;}
            iframe.stIFrame {border-radius:20px;}
            .st-key-metrics [data-testid="stMetricLabel"]{min-height:2.4em !important;align-content:start;}
            }
            [data-testid="stLayoutWrapper"]:has(> .st-key-legend){height:0;margin-bottom:-1rem;z-index:5;pointer-events:none;}
            .st-key-legend .legend{display:flex;justify-content:flex-end;gap:12px;padding-top:12px;font-size:12px;color:#5d6a62;}
            .st-key-legend .legend span{display:inline-flex;align-items:center;gap:5px;}
            .st-key-legend .legend i{width:9px;height:9px;border-radius:50%;}
            </style>"""
        )    
 
    
    def run(self):
        st.set_page_config(
            page_title="서울시 따릉이 대여정보 대시보드",
            page_icon="🚲",
            layout="wide"
        )
        self.apply_style()

        # API 데이터 가져오기
        with st.spinner("서울시 실시간 데이터를 불러오는 중"):
            fetcher = DataFetcher()
            raw_data = fetcher.get_data()

        if not raw_data:
            st.error("데이터를 불러오지 못했습니다.")
            return

        # 전처리 및 혼잡도/거치율 계산
        processor = DataProcessor(raw_data)
        df = processor.clean()
        df = processor.add_rate()

        # 사이드바 입력값 받기
        search_keyword, min_bikes, status_filter = self.render_sidebar()

        # StationFilter의 apply_filters로 통합 필터링 실행
        sf = StationFilter(df)
        filtered_df = sf.apply_filters(
            keyword=search_keyword,
            status=status_filter,
            min_bikes=min_bikes,

        )

        # 제목 + 마지막 갱신 시각 + 새로고침 버튼
        updated_at = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H:%M:%S")
        with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
            st.title("서울시 공공자전거 대여 현황")
            with st.container(horizontal=True, vertical_alignment="center", width="content", gap="small"):
                st.caption(f"마지막 갱신 {updated_at}", width="content")
                st.button("", icon=":material/refresh:", type="tertiary", on_click=self.save_snapshot)

        filtered_summary = {
            "total_stations": len(filtered_df),
            "total_bikes": int(filtered_df["parkingBikeTotCnt"].sum()) if not filtered_df.empty else 0,
            "total_racks": int(filtered_df["rackTotCnt"].sum()) if not filtered_df.empty else 0,
            "avg_rate": float(filtered_df["rate"].mean()) if not filtered_df.empty else 0.0,
        }
        
        self.show_metrics(filtered_summary)

        self.show_map(filtered_df)
        tab_chart, tab_table = st.tabs(["차트", "대여소 목록"])
        with tab_chart:
            self.show_chart(filtered_df)
        with tab_table:
            self.show_table(filtered_df)




if __name__ == "__main__":
    ui = DashboardUI()
    ui.run()