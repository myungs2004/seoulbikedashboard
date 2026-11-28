import pandas as pd
from DataFetcher import DataFetcher
from DataProcessor import DataProcessor

class StationFilter:

    #입력:df
    #출력:filtered_df
    def __init__(self, df):
        self.df = df
        # 원본 데이터를 보존하면서 연쇄 필터링을 수행하기 위해 복사본으로 초기화
        self.filtered_df = df.copy() if df is not None else pd.DataFrame()

    #대여소 이름/키워드 필터링
    def search(self, keyword):
        if keyword and keyword.strip():
            #검색어 유무를 T/F로 반환 후 True인 인덱스만 남고 filtered_df에 덮어쓰기(최신화)
            self.filtered_df = self.filtered_df[
                self.filtered_df["stationName"].astype(str).str.contains(keyword.strip(), case=False, na=False)
            ]
        return self.filtered_df

    #혼잡도 상태 필터링(부족/보통/여유)
    def by_status(self, status):
        if status and status != "전체":
            self.filtered_df = self.filtered_df[
                self.filtered_df["status"] == status
            ]
        return self.filtered_df

    #최소 자전거 수 필터링
    def bike_count(self, min_bikes):
        if min_bikes is not None and min_bikes > 0:
            bike_cnt = pd.to_numeric(self.filtered_df["parkingBikeTotCnt"], errors="coerce").fillna(0)
            self.filtered_df = self.filtered_df[bike_cnt >= min_bikes]
        return self.filtered_df

    #자전거 부족 대여소 추출
    def top_shortage(self, n=10):
        if self.filtered_df is None or self.filtered_df.empty:
            return pd.DataFrame()
        temp_df = self.filtered_df.copy()
        temp_df["parkingBikeTotCnt"] = pd.to_numeric(temp_df["parkingBikeTotCnt"], errors="coerce").fillna(0)
        return temp_df.sort_values(by="parkingBikeTotCnt", ascending=True).head(n)


    #사이드바 조건(검색어, 상태, 최소 자전거 수) 연쇄 필터링 실행
    def apply_filters(self, keyword="", status="전체", min_bikes=0, min_racks=0, region="전체"):
        self.search(keyword)
        self.by_status(status)
        self.bike_count(min_bikes)
        self.rack_count(min_racks)
        self.by_region(region)
        return self.filtered_df
    
    # 최소 거치대 수 필터링
    def rack_count(self, min_racks):
        if min_racks is not None and min_racks > 0:
            rack_cnt = pd.to_numeric(self.filtered_df["rackTotCnt"], errors="coerce").fillna(0)
            self.filtered_df = self.filtered_df[rack_cnt >= min_racks]
        return self.filtered_df

    # 권역 필터링
    def by_region(self, region):
       
        if region and region != "전체":
            region_keywords = {
                    "노원·강북": ["노원", "강북", "도봉", "중랑", "광운대", "석계", "공릉", "하계", "중계", "상계", "수유", "미아", "창동", "쌍문"],
                    "홍대·신촌": ["홍대", "신촌", "마포", "서대문", "연남", "합정", "망원", "상암", "이대", "아현", "공덕"],
                    "강남·서초": ["강남", "서초", "역삼", "선릉", "삼성", "논현", "신사", "교대", "양재", "반포", "방배", "사당"],
                    "잠실·송파": ["잠실", "송파", "석촌", "방이", "문정", "가락", "오금", "몽촌토성", "올림픽공원", "천호"],
                    "여의도·영등포": ["여의도", "영등포", "당산", "문래", "신길", "대림", "보라매", "국회의사당"],
                    "종로·광화문": ["종로", "광화문", "시청", "을지로", "안국", "혜화", "동대문", "명동", "충무로", "서울역"],
                }
            region_bounds = {
                    "노원·강북": (37.59, 37.70, 127.00, 127.10),
                    "홍대·신촌": (37.54, 37.59, 126.87, 126.96),
                    "강남·서초": (37.46, 37.53, 126.97, 127.08),
                    "잠실·송파": (37.47, 37.55, 127.07, 127.16),
                    "여의도·영등포": (37.48, 37.55, 126.88, 126.95),
                    "종로·광화문": (37.55, 37.61, 126.96, 127.02),
                }
            df_sub = self.filtered_df
            keywords = region_keywords.get(region, [])
            if keywords:
                pattern = "|".join(keywords)
                df_sub = df_sub[
                    df_sub["stationName"].astype(str).str.contains(pattern, case=False, na=False)
                ]
            if region in region_bounds and {"stationLatitude", "stationLongitude"}.issubset(df_sub.columns):
                min_lat, max_lat, min_lon, max_lon = region_bounds[region]
                df_sub = df_sub[
                    df_sub["stationLatitude"].between(min_lat, max_lat, inclusive="both")
                    & df_sub["stationLongitude"].between(min_lon, max_lon, inclusive="both")
                ]

            self.filtered_df = df_sub
           
        return self.filtered_df
    



#api로 받아오는 정보
#거치대개수
#대여소이름
#자전거주차총건수
#거치율
#위도
#경도
#대여소ID
#대여시간

