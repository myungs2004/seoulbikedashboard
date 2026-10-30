import pandas as pd
from DataFetcher import DataFetcher

class DataProcessor:

    #입력:raw_data
    #출력:df
    def __init__(self,raw_data):
        self.raw_data = raw_data
        self.df = None
        self.summary_stats = {}

    #데이터 타입 변환 함수
    # Pandas DataFrame으로 변환 
    def clean(self):
        pass

    #자전거 대여 혼잡 상태 판단(여유,보통,부족)
    def add_rate(self): 
        pass

    #요약 통계 생성(전체 대여소, 총 자전거 수 같은 거 딕셔너리 이용해서 정리)
    def get_summary(self): 
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