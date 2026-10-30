import pandas as pd
from DataProcessor import DataProcessor

class StationFilter:

    #입력:df
    #출력:filtered_df
    def __init__(self,df):
        self.df = df
        self.filtered_df = None

    #대여소 이름/키워드 필터링
    def search(self,keyword):
        pass

    #혼잡도 상태 필터링(부족/보통/여유)
    def by_status(self,status): 
        pass

    #최소 자전거 수 필터링
    def bike_count(self,min_bikes): 
        pass

    #자전거 부족 대여소 추출
    def top_shortage(self,n):
        pass



#api로 받아오는 정보
#거치대개수
#대여소이름
#자전거주차총건수
#거치율
#위도
#경도
#대여소ID
#대여시간