import os
import json
import psycopg2
from datetime import datetime

class DashboardAPI:
    def __init__(self):
        self.conn_string = os.environ.get('DATABASE_URL', '')
    
    def get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def get_dashboard_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data = {}
        
        # 총 건수
        cursor.execute("SELECT COUNT(*) FROM bid_results")
        data['total_count'] = cursor.fetchone()[0]
        
        # 용량
        cursor.execute("SELECT pg_total_relation_size('bid_results')")
        size_bytes = cursor.fetchone()[0]
        data['size_mb'] = round(size_bytes / 1024 / 1024, 2)
        data['size_percent'] = round((size_bytes / (3 * 1024 * 1024 * 1024)) * 100, 2)
        
        # 월별 현황
        cursor.execute("""
            SELECT TO_CHAR(rgst_dt, 'YYYY-MM') as month, COUNT(*) 
            FROM bid_results 
            WHERE rgst_dt IS NOT NULL
            GROUP BY TO_CHAR(rgst_dt, 'YYYY-MM')
            ORDER BY month DESC
        """)
        data['monthly'] = [{'month': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # 최근 수집 로그
        cursor.execute("""
            SELECT collection_type, start_date, end_date, 
                   collected_count, status, created_at
            FROM collection_logs 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        data['logs'] = [{
            'type': row[0],
            'start': row[1],
            'end': row[2],
            'count': row[3],
            'status': row[4],
            'date': row[5].strftime('%Y-%m-%d %H:%M')
        } for row in cursor.fetchall()]
        
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return data


if __name__ == "__main__":
    api = DashboardAPI()
    data = api.get_dashboard_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
