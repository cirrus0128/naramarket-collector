import requests
import os
from urllib.parse import quote
import time

class NaramarketAPI:
    def __init__(self):
        self.api_key = os.environ.get('API_SERVICE_KEY', '')
        self.base_url = "http://apis.data.go.kr/1230000/as/ScsbidInfoService"
        self.call_count = 0
        self.daily_limit = 1000
    
    def call_api(self, endpoint, params):
        if self.call_count >= self.daily_limit:
            raise Exception("일일 API 호출 한도 초과")
        
        encoded_key = quote(self.api_key, safe='')
        url = f"{self.base_url}/{endpoint}?serviceKey={encoded_key}"
        
        for key, value in params.items():
            url += f"&{key}={value}"
        
        time.sleep(0.1)
        
        response = requests.get(url, timeout=30)
        self.call_count += 1
        response.raise_for_status()
        
        return response.json()
    
    def get_sucbid_goods(self, start_date, end_date, page=1, rows=100):
        params = {
            'pageNo': page,
            'numOfRows': rows,
            'inqryDiv': '1',
            'inqryBgnDt': start_date,
            'inqryEndDt': end_date,
            'type': 'json'
        }
        return self.call_api('getScsbidListSttusThng', params)
