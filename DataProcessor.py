import pandas as pd

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
        rows = self.raw_data["rentBikeStatus"]["row"]
        self.df = pd.DataFrame(rows)

        numeric_columns = [
            "rackTotCnt",  # 거치대 수
            "parkingBikeTotCnt",  # 현재 자전거 수
            "stationLatitude",  # 위도
            "stationLongitude",  # 경도
        ]

        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        self.df = self.df.dropna(
            subset=["rackTotCnt", "parkingBikeTotCnt"]
        )

        return self.df

    #자전거 대여 혼잡 상태 판단(여유,보통,부족)
    def add_rate(self): 
        pass

    #요약 통계 생성(전체 대여소, 총 자전거 수 같은 거 딕셔너리 이용해서 정리)
    def get_summary(self): 
        pass

if __name__ == "__main__":
    sample_data = {
        "rentBikeStatus": {
            "row": [
                {
                    "stationName": "연습 대여소 A",
                    "rackTotCnt": "10",
                    "parkingBikeTotCnt": "2",
                    "stationLatitude": "37.60",
                    "stationLongitude": "127.05",
                },
                {
                    "stationName": "연습 대여소 B",
                    "rackTotCnt": "20",
                    "parkingBikeTotCnt": "10",
                    "stationLatitude": "37.61",
                    "stationLongitude": "127.06",
                },
            ]
        }
    }

    processor = DataProcessor(sample_data)
    df = processor.clean()

    print(df)
    print(df.dtypes)
    print("총 자전거 수:", df["parkingBikeTotCnt"].sum())


#api로 받아오는 정보
#거치대개수
#대여소이름
#자전거주차총건수
#거치율
#위도
#경도
#대여소ID
#대여시간