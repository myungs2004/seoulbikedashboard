import requests
import streamlit as st

class DataFetcher:

    def __init__(self,api_key= "6f424346616d736a383371627a5a55",base_url = None):
        self.api_key = api_key
        self.base_url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/bikeList/1/1000/"
        self.raw_data = None

    #서울시 공공데이터 받아오는 함수
    @st.cache_data(ttl=300)
    def get_data(_self):
         
            all_rows = []
        
            # 1부터 3000까지 1000개씩 구간을 나누어 반복
            for start in range(1, 3001, 1000):
                end = start + 999
            # 기존에 정의된 base_url의 '1/1000' 부분을 현재 구간 숫자로 교체
                target_url = _self.base_url.replace("1/1000", f"{start}/{end}")
            
                try:
                    response = requests.get(target_url, timeout=5)
                    res_json = response.json()
                    rows = res_json.get("rentBikeStatus", {}).get("row", [])
                    if rows:
                        all_rows.extend(rows)
                    else:
                        break
                except Exception as e:
                    print(f"데이터 조회 중 에러 발생: {e}")
                    break
                
            _self.raw_data = {"rentBikeStatus": {"row": all_rows}}
            return _self.raw_data

    #API 상태 점검 / 예외처리 
    def check_api(self):
        test_url = self.base_url.replace("1/1000", "1/5")
        try:
            response = requests.get(test_url, timeout=5)
            response.raise_for_status()
            res_json = response.json()
            
            # 서울시 오픈API 표준 응답 결과 코드 확인
            rent_status = res_json.get("rentBikeStatus", {})
            result_code = rent_status.get("RESULT", {}).get("CODE")
            result_message = rent_status.get("RESULT", {}).get("MESSAGE")
            
            if result_code == "INFO-000":
                return {"status": True, "code": result_code, "message": "API가 정상적으로 작동 중입니다."}
            else:
                return {"status": False, "code": result_code, "message": f"API 오류 응답: {result_message}"}
                
        except requests.exceptions.Timeout:
            return {"status": False, "code": "TIMEOUT", "message": "서버 응답 시간이 초과되었습니다."}
        except requests.exceptions.RequestException as e:
            return {"status": False, "code": "NETWORK_ERR", "message": f"네트워크 통신 에러: {e}"}
        except Exception as e:
            return {"status": False, "code": "UNKNOWN_ERR", "message": f"예기치 못한 에러 발생: {e}"}




#공공데이터 제대로 받아오는지 테스트
if __name__ == "__main__":
    fetcher = DataFetcher()
    
    # 1. API 상태 사전 점검 테스트
    check_result = fetcher.check_api()
    print(f"API 점검 결과: {check_result['message']} (코드: {check_result['code']})")
    
    if check_result["status"]:
        # 2. 데이터 수집 테스트
        data = fetcher.get_data()
        station_list = data.get("rentBikeStatus", {}).get("row", [])
        
        print(f"대여소 총 개수: {len(station_list):,}개")
        if len(station_list) > 0:
            print("첫 번째 대여소 샘플:", station_list[0])
    else:
        print("API 점검에 실패하여 데이터를 불러오지 않습니다.")
