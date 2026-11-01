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
        if self.df is None:
            raise ValueError("clean()을 먼저 실행하세요.")

        valid = (
            (self.df["rackTotCnt"] > 0) & (self.df["parkingBikeTotCnt"] >= 0)
        ) # 거치대 수가 0보다 크고 자전거 수가 음수가 아닌 행을 valid로 설정

        capacity = self.df["rackTotCnt"].where(valid)
        rate = self.df["parkingBikeTotCnt"] / capacity * 100

        self.df["rate"] = rate
        self.df["status"] = None

        self.df.loc[rate < 20, "status"] = "부족"
        self.df.loc[(rate >= 20) & (rate < 60), "status"] = "보통"
        self.df.loc[rate >= 60, "status"] = "여유"

        return self.df

    #요약 통계 생성(전체 대여소, 총 자전거 수 같은 거 딕셔너리 이용해서 정리)
    def get_summary(self):
        if self.df is None or "rate" not in self.df.columns:
            raise ValueError("clean()과 add_rate()를 먼저 실행하세요.")

        self.summary_stats = {
            "total_stations": len(self.df),
            "total_bikes": int(self.df["parkingBikeTotCnt"].sum()),
            "total_racks": int(self.df["rackTotCnt"].sum()),
            "avg_rate": float(self.df["rate"].mean()),
        }

        return self.summary_stats

if __name__ == "__main__": # 테스트용 데이터
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
    processor.clean()
    df = processor.add_rate()
    summary = processor.get_summary()

    print(df)
    print(summary)


#api로 받아오는 정보
#거치대개수
#대여소이름
#자전거주차총건수
#거치율
#위도
#경도
#대여소ID
#대여시간