import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import NaramarketAPI
from database import Database
from datetime import datetime, timedelta
import calendar

class DataCollector:
    def __init__(self):
        self.api = NaramarketAPI()
        self.db = Database()
    
    def collect_all_pages(self, start_date, end_date):
        page = 1
        rows_per_page = 100
        total_saved = 0
        
        result = self.api.get_sucbid_goods(start_date, end_date, page=1, rows=rows_per_page)
        total_count = result['response']['body']['totalCount']
        total_pages = (total_count // rows_per_page) + 1
        
        print(f"  전체: {total_count}건, {total_pages}페이지")
        
        while page <= total_pages:
            try:
                result = self.api.get_sucbid_goods(start_date, end_date, page=page, rows=rows_per_page)
                items = result['response']['body'].get('items', [])
                
                if not items:
                    break
                
                saved = self.db.save_bid_results(items, 'goods')
                total_saved += saved
                print(f"    페이지 {page}/{total_pages}: {saved}건")
                page += 1
                
            except Exception as e:
                print(f"    페이지 {page} 오류: {e}")
                break
        
        return total_saved, total_count
    
    def collect_daily(self):
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime('%Y%m%d') + '0000'
        end_date = yesterday.strftime('%Y%m%d') + '2359'
        
        print(f"\n📅 일일 수집: {yesterday.strftime('%Y-%m-%d')}")
        print("=" * 40)
        
        saved, total = self.collect_all_pages(start_date, end_date)
        
        self.db.save_collection_log(
            'daily', start_date, end_date,
            'getScsbidListSttusThng', total, saved, 'success'
        )
        
        print(f"\n✅ 완료: {saved}건 저장")
        print(f"📡 API 호출: {self.api.call_count}회")
        
        return saved
    
    def collect_month(self, year, month):
        start_date = f"{year}{month:02d}010000"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}{month:02d}{last_day}2359"
        
        print(f"\n📅 {year}년 {month}월 수집")
        print("=" * 40)
        
        saved, total = self.collect_all_pages(start_date, end_date)
        
        self.db.save_collection_log(
            'monthly', start_date, end_date,
            'getScsbidListSttusThng', total, saved, 'success'
        )
        
        print(f"\n✅ 완료: {saved}건 저장")
        print(f"📡 API 호출: {self.api.call_count}회")
        
        return saved

if __name__ == "__main__":
    collector = DataCollector()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'daily':
            collector.collect_daily()
        elif sys.argv[1] == 'month' and len(sys.argv) == 4:
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            collector.collect_month(year, month)
    else:
        collector.collect_daily()
