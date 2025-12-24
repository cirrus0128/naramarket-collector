import os
import psycopg2
from datetime import datetime, timedelta

class ReportGenerator:
    def __init__(self):
        self.conn_string = os.environ.get('DATABASE_URL', '')
    
    def get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def generate_daily_report(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print("=" * 50)
        print(f"나라장터 데이터 수집 일일 리포트")
        print(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # 총 현황
        cursor.execute("SELECT COUNT(*) FROM bid_results")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('bid_results'))")
        size = cursor.fetchone()[0]
        
        print(f"\n[전체 현황]")
        print(f"  총 데이터: {total:,}건")
        print(f"  사용 용량: {size} / 3GB")
        
        # 어제 수집 현황
        cursor.execute("""
            SELECT COUNT(*) FROM bid_results 
            WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
        """)
        yesterday_count = cursor.fetchone()[0]
        
        print(f"\n[어제 수집]")
        print(f"  수집 건수: {yesterday_count:,}건")
        
        # 최근 수집 로그
        cursor.execute("""
            SELECT collection_type, collected_count, status, created_at
            FROM collection_logs 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        logs = cursor.fetchall()
        
        print(f"\n[최근 수집 로그]")
        for log in logs:
            status_icon = "✓" if log[2] == 'success' else "✗"
            print(f"  {status_icon} {log[0]} | {log[1]}건 | {log[3].strftime('%m-%d %H:%M')}")
        
        # 월별 현황 (최근 3개월)
        cursor.execute("""
            SELECT TO_CHAR(rgst_dt, 'YYYY-MM') as month, COUNT(*) 
            FROM bid_results 
            WHERE rgst_dt IS NOT NULL
            GROUP BY TO_CHAR(rgst_dt, 'YYYY-MM')
            ORDER BY month DESC
            LIMIT 5
        """)
        monthly = cursor.fetchall()
        
        print(f"\n[월별 현황]")
        for month, count in monthly:
            print(f"  {month}: {count:,}건")
        
        # 용량 경고
        cursor.execute("SELECT pg_total_relation_size('bid_results')")
        size_bytes = cursor.fetchone()[0]
        usage_percent = (size_bytes / (3 * 1024 * 1024 * 1024)) * 100
        
        print(f"\n[용량 상태]")
        if usage_percent > 80:
            print(f"  ⚠️ 경고: 용량 {usage_percent:.1f}% 사용 중!")
        elif usage_percent > 50:
            print(f"  주의: 용량 {usage_percent:.1f}% 사용 중")
        else:
            print(f"  정상: 용량 {usage_percent:.1f}% 사용 중")
        
        print("\n" + "=" * 50)
        
        cursor.close()
        conn.close()


if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_daily_report()
