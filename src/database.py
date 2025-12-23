import psycopg2
import os

class Database:
    def __init__(self):
        self.conn_string = os.environ.get('DATABASE_URL', '')
    
    def get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def safe_int(self, value):
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except:
            return None
    
    def safe_float(self, value):
        if value is None or value == '':
            return None
        try:
            return float(value)
        except:
            return None
    
    def save_bid_results(self, items, bid_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        saved_count = 0
        for item in items:
            try:
                cursor.execute("""
                    INSERT INTO bid_results (
                        bid_ntce_no, bid_ntce_ord, bid_clsfc_no, rbid_no,
                        bid_ntce_nm, bid_type, prtcpt_cnum, bidwinnr_nm,
                        bidwinnr_bizno, bidwinnr_ceo_nm, bidwinnr_adrs,
                        bidwinnr_tel_no, sucsf_bid_amt, sucsf_bid_rate,
                        rl_openg_dt, dminstt_cd, dminstt_nm, rgst_dt, fnl_sucsf_date
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (bid_ntce_no, bid_ntce_ord, bid_clsfc_no) 
                    DO UPDATE SET
                        bidwinnr_nm = EXCLUDED.bidwinnr_nm,
                        sucsf_bid_amt = EXCLUDED.sucsf_bid_amt,
                        sucsf_bid_rate = EXCLUDED.sucsf_bid_rate
                """, (
                    item.get('bidNtceNo'),
                    item.get('bidNtceOrd'),
                    item.get('bidClsfcNo'),
                    item.get('rbidNo'),
                    item.get('bidNtceNm'),
                    bid_type,
                    self.safe_int(item.get('prtcptCnum')),
                    item.get('bidwinnrNm'),
                    item.get('bidwinnrBizno'),
                    item.get('bidwinnrCeoNm'),
                    item.get('bidwinnrAdrs'),
                    item.get('bidwinnrTelNo'),
                    self.safe_int(item.get('sucsfbidAmt')),
                    self.safe_float(item.get('sucsfbidRate')),
                    item.get('rlOpengDt') or None,
                    item.get('dminsttCd'),
                    item.get('dminsttNm'),
                    item.get('rgstDt') or None,
                    item.get('fnlSucsfDate') or None
                ))
                saved_count += 1
            except Exception as e:
                print(f"저장 오류: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        return saved_count
    
    def save_collection_log(self, collection_type, start_date, end_date, api_name, total_count, collected_count, status, error_message=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO collection_logs 
            (collection_type, start_date, end_date, api_name, total_count, collected_count, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (collection_type, start_date, end_date, api_name, total_count, collected_count, status, error_message))
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT bid_type, COUNT(*) FROM bid_results GROUP BY bid_type")
        stats = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM bid_results")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {'by_type': dict(stats), 'total': total}
