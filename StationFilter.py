import pandas as pd
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
    def apply_filters(self, keyword="", status="전체", min_bikes=0):
        self.search(keyword)
        self.by_status(status)
        self.bike_count(min_bikes)
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
