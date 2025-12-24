import os
import sys
import psycopg2

print = __builtins__.print
import functools
print = functools.partial(print, flush=True)

class DataManager:
    def __init__(self):
        self.conn_string = os.environ.get('DATABASE_URL', '')
    
    def get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def show_status(self):
        """현황 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("=" * 50)
        print("📊 데이터베이스 현황")
        print("=" * 50)
        
        # 총 건수
        cursor.execute("SELECT COUNT(*) FROM bid_results")
        total = cursor.fetchone()[0]
        print(f"\n총 데이터: {total:,}건")
        
        # 용량
        cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('bid_results'))")
        size = cursor.fetchone()[0]
        print(f"사용 용량: {size} / 3GB")
        
        # 월별 현황
        cursor.execute("""
            SELECT TO_CHAR(rgst_dt, 'YYYY-MM') as month, COUNT(*) 
            FROM bid_results 
            WHERE rgst_dt IS NOT NULL
            GROUP BY TO_CHAR(rgst_dt, 'YYYY-MM')
            ORDER BY month DESC
        """)
        monthly = cursor.fetchall()
        
        print(f"\n📅 월별 현황:")
        for month, count in monthly:
            print(f"  {month}: {count:,}건")
        
        # 최근 수집 로그
        cursor.execute("""
            SELECT collection_type, start_date, end_date, 
                   collected_count, status, created_at
            FROM collection_logs 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        logs = cursor.fetchall()
        
        print(f"\n📋 최근 수집 로그:")
        for log in logs:
            print(f"  [{log[4]}] {log[0]} | {log[1][:8]}~{log[2][:8]} | {log[3]}건 | {log[5]}")
        
        cursor.close()
        conn.close()
        print("\n" + "=" * 50)
    
    def delete_month(self, year, month, confirm):
        """월별 데이터 삭제"""
        if confirm != 'yes':
            print("❌ 삭제 취소: confirm에 'yes'를 입력해야 합니다.")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 삭제 전 건수 확인
        cursor.execute("""
            SELECT COUNT(*) FROM bid_results 
            WHERE TO_CHAR(rgst_dt, 'YYYY-MM') = %s
        """, (f"{year}-{month:02d}" if isinstance(month, int) else f"{year}-{month.zfill(2)}",))
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"⚠️ {year}년 {month}월 데이터가 없습니다.")
            cursor.close()
            conn.close()
            return
        
        # 삭제 실행
        month_str = f"{year}-{month.zfill(2)}" if isinstance(month, str) else f"{year}-{month:02d}"
        cursor.execute("""
            DELETE FROM bid_results 
            WHERE TO_CHAR(rgst_dt, 'YYYY-MM') = %s
        """, (month_str,))
        
        conn.commit()
        print(f"✅ {year}년 {month}월 데이터 {count:,}건 삭제 완료")
        
        cursor.close()
        conn.close()
    
    def cleanup_duplicates(self):
        """중복 데이터 제거"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 중복 건수 확인
        cursor.execute("""
            SELECT COUNT(*) - COUNT(DISTINCT (bid_ntce_no, bid_ntce_ord, bid_clsfc_no))
            FROM bid_results
        """)
        dup_count = cursor.fetchone()[0]
        
        if dup_count == 0:
            print("✅ 중복 데이터가 없습니다.")
        else:
            print(f"⚠️ 중복 데이터 {dup_count}건 발견 (UNIQUE 제약조건으로 자동 방지됨)")
        
        cursor.close()
        conn.close()
    
    def reset_all(self, confirm):
        """전체 데이터 초기화"""
        if confirm != 'yes':
            print("❌ 초기화 취소: confirm에 'yes'를 입력해야 합니다.")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM bid_results")
        count = cursor.fetchone()[0]
        
        cursor.execute("TRUNCATE TABLE bid_results RESTART IDENTITY")
        cursor.execute("TRUNCATE TABLE collection_logs RESTART IDENTITY")
        
        conn.commit()
        print(f"✅ 전체 데이터 {count:,}건 삭제 완료")
        print("✅ 수집 로그 초기화 완료")
        
        cursor.close()
        conn.close()


if __name__ == "__main__":
    manager = DataManager()
    
    action = os.environ.get('ACTION', 'status (현황 조회)')
    year = os.environ.get('YEAR', '')
    month = os.environ.get('MONTH', '')
    confirm = os.environ.get('CONFIRM', '')
    
    if 'status' in action:
        manager.show_status()
    elif 'delete-month' in action:
        if not year or not month:
            print("❌ 연도와 월을 입력해야 합니다.")
        else:
            manager.delete_month(year, month, confirm)
    elif 'cleanup-duplicates' in action:
        manager.cleanup_duplicates()
    elif 'reset-all' in action:
        manager.reset_all(confirm)
    else:
        print(f"❌ 알 수 없는 작업: {action}")
