# 데이터베이스 접근 및 가공 지침서

## 1. 데이터베이스 개요

### 1.1 접속 정보

| 항목 | 값 |
|------|-----|
| 서비스 | Neon PostgreSQL |
| 호스트 | ep-aged-flower-a1hu9z98-pooler.ap-southeast-1.aws.neon.tech |
| 데이터베이스 | neondb |
| 사용자 | neondb_owner |
| SSL | 필수 (sslmode=require) |

### 1.2 접속 방법

**Python (psycopg2)**
```python
import psycopg2

conn = psycopg2.connect(
    "postgresql://neondb_owner:비밀번호@ep-aged-flower-a1hu9z98-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)
cursor = conn.cursor()
DBeaver / pgAdmin 등 GUI 도구

새 연결 생성
PostgreSQL 선택
접속 정보 입력
SSL 모드: require 설정
2. 테이블 구조
2.1 bid_results (낙찰 정보)
컬럼명	타입	설명	예시
id	SERIAL	자동 증가 PK	1, 2, 3...
bid_ntce_no	VARCHAR(40)	입찰공고번호	R25BK01158137
bid_ntce_ord	VARCHAR(3)	입찰공고차수	000, 001
bid_clsfc_no	VARCHAR(5)	입찰분류번호	1
rbid_no	VARCHAR(3)	재입찰번호	000
bid_ntce_nm	VARCHAR(1000)	공고명	사무용품 구매
bid_type	VARCHAR(20)	입찰유형	goods
prtcpt_cnum	INTEGER	참가업체수	15
bidwinnr_nm	VARCHAR(200)	낙찰업체명	(주)OO상사
bidwinnr_bizno	VARCHAR(10)	사업자번호	1234567890
bidwinnr_ceo_nm	VARCHAR(35)	대표자명	홍길동
bidwinnr_adrs	VARCHAR(200)	업체주소	서울시 강남구...
bidwinnr_tel_no	VARCHAR(25)	전화번호	02-1234-5678
sucsf_bid_amt	BIGINT	낙찰금액 (원)	15000000
sucsf_bid_rate	DECIMAL(10,3)	낙찰률 (%)	87.5
rl_openg_dt	TIMESTAMP	개찰일시	2024-12-01 10:00:00
dminstt_cd	VARCHAR(7)	수요기관코드	1320000
dminstt_nm	VARCHAR(200)	수요기관명	경찰청
rgst_dt	TIMESTAMP	등록일시	2024-12-01 15:30:00
fnl_sucsf_date	DATE	최종낙찰일	2024-12-01
created_at	TIMESTAMP	수집일시	2024-12-01 16:00:00
인덱스

idx_bid_results_rgst_dt: 등록일시 기준 조회 최적화
idx_bid_results_bid_type: 입찰유형 필터링
idx_bid_results_bidwinnr_bizno: 업체별 조회
UNIQUE 제약조건

(bid_ntce_no, bid_ntce_ord, bid_clsfc_no): 중복 데이터 방지
2.2 collection_logs (수집 로그)
컬럼명	타입	설명
id	SERIAL	자동 증가 PK
collection_type	VARCHAR(50)	수집유형 (daily, monthly, historical)
start_date	VARCHAR(20)	수집 시작일
end_date	VARCHAR(20)	수집 종료일
api_name	VARCHAR(100)	API 이름
total_count	INTEGER	전체 건수
collected_count	INTEGER	수집 건수
status	VARCHAR(20)	상태 (success, fail)
error_message	TEXT	에러 메시지
created_at	TIMESTAMP	로그 생성일시
3. 데이터 조회
3.1 기본 조회
전체 건수 확인

CopySELECT COUNT(*) FROM bid_results;
월별 건수 확인

CopySELECT 
    TO_CHAR(rgst_dt, 'YYYY-MM') as month,
    COUNT(*) as count
FROM bid_results
WHERE rgst_dt IS NOT NULL
GROUP BY TO_CHAR(rgst_dt, 'YYYY-MM')
ORDER BY month DESC;
용량 확인

CopySELECT pg_size_pretty(pg_total_relation_size('bid_results'));
3.2 조건별 조회
특정 기간 조회

CopySELECT * FROM bid_results
WHERE rgst_dt BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY rgst_dt DESC;
특정 업체 낙찰 이력

CopySELECT 
    bid_ntce_nm,
    sucsf_bid_amt,
    sucsf_bid_rate,
    dminstt_nm,
    rgst_dt
FROM bid_results
WHERE bidwinnr_bizno = '1234567890'
ORDER BY rgst_dt DESC;
특정 기관 발주 내역

CopySELECT 
    bid_ntce_nm,
    bidwinnr_nm,
    sucsf_bid_amt,
    rgst_dt
FROM bid_results
WHERE dminstt_nm LIKE '%경찰청%'
ORDER BY rgst_dt DESC;
금액 범위 조회

CopySELECT * FROM bid_results
WHERE sucsf_bid_amt BETWEEN 10000000 AND 100000000
ORDER BY sucsf_bid_amt DESC;
낙찰률 범위 조회

CopySELECT * FROM bid_results
WHERE sucsf_bid_rate BETWEEN 85 AND 90
ORDER BY sucsf_bid_rate;
3.3 통계 조회
업체별 낙찰 건수 TOP 10

CopySELECT 
    bidwinnr_nm,
    bidwinnr_bizno,
    COUNT(*) as win_count,
    SUM(sucsf_bid_amt) as total_amount,
    AVG(sucsf_bid_rate) as avg_rate
FROM bid_results
WHERE bidwinnr_nm IS NOT NULL
GROUP BY bidwinnr_nm, bidwinnr_bizno
ORDER BY win_count DESC
LIMIT 10;
기관별 발주 금액 TOP 10

CopySELECT 
    dminstt_nm,
    COUNT(*) as order_count,
    SUM(sucsf_bid_amt) as total_amount
FROM bid_results
WHERE dminstt_nm IS NOT NULL
GROUP BY dminstt_nm
ORDER BY total_amount DESC
LIMIT 10;
월별 평균 낙찰률 추이

CopySELECT 
    TO_CHAR(rgst_dt, 'YYYY-MM') as month,
    COUNT(*) as count,
    ROUND(AVG(sucsf_bid_rate), 2) as avg_rate,
    ROUND(AVG(sucsf_bid_amt), 0) as avg_amount
FROM bid_results
WHERE rgst_dt IS NOT NULL AND sucsf_bid_rate IS NOT NULL
GROUP BY TO_CHAR(rgst_dt, 'YYYY-MM')
ORDER BY month;
참가업체수별 낙찰률 분석

CopySELECT 
    CASE 
        WHEN prtcpt_cnum <= 5 THEN '1~5'
        WHEN prtcpt_cnum <= 10 THEN '6~10'
        WHEN prtcpt_cnum <= 20 THEN '11~20'
        ELSE '20+'
    END as participant_range,
    COUNT(*) as count,
    ROUND(AVG(sucsf_bid_rate), 2) as avg_rate
FROM bid_results
WHERE prtcpt_cnum IS NOT NULL
GROUP BY 
    CASE 
        WHEN prtcpt_cnum <= 5 THEN '1~5'
        WHEN prtcpt_cnum <= 10 THEN '6~10'
        WHEN prtcpt_cnum <= 20 THEN '11~20'
        ELSE '20+'
    END
ORDER BY avg_rate;
4. 데이터 가공
4.1 Python 활용
기본 연결 및 조회

Copyimport psycopg2
import pandas as pd

# 연결
conn = psycopg2.connect("postgresql://...")

# DataFrame으로 조회
df = pd.read_sql("""
    SELECT * FROM bid_results
    WHERE rgst_dt >= '2024-01-01'
""", conn)

print(df.head())
print(f"총 {len(df)}건")

conn.close()
업체별 분석

Copy# 업체별 낙찰 통계
company_stats = df.groupby('bidwinnr_nm').agg({
    'id': 'count',
    'sucsf_bid_amt': ['sum', 'mean'],
    'sucsf_bid_rate': 'mean'
}).round(2)

company_stats.columns = ['낙찰건수', '총금액', '평균금액', '평균낙찰률']
company_stats = company_stats.sort_values('낙찰건수', ascending=False)
print(company_stats.head(10))
월별 추이 시각화

Copyimport matplotlib.pyplot as plt

monthly = df.groupby(df['rgst_dt'].dt.to_period('M')).agg({
    'id': 'count',
    'sucsf_bid_amt': 'sum'
})

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.bar(monthly.index.astype(str), monthly['id'], alpha=0.7)
ax1.set_ylabel('건수')

ax2 = ax1.twinx()
ax2.plot(monthly.index.astype(str), monthly['sucsf_bid_amt'], 'r-o')
ax2.set_ylabel('금액')

plt.title('월별 낙찰 현황')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
CSV 내보내기

Copy# 전체 데이터 내보내기
df.to_csv('bid_results.csv', index=False, encoding='utf-8-sig')

# 특정 조건 데이터만 내보내기
filtered = df[df['sucsf_bid_amt'] >= 10000000]
filtered.to_csv('large_bids.csv', index=False, encoding='utf-8-sig')
4.2 Excel 연동
Excel Power Query 연결

Excel → 데이터 → 데이터 가져오기 → 데이터베이스에서
PostgreSQL 선택
서버/DB 정보 입력
원하는 테이블/쿼리 선택
4.3 Google Colab 활용
Copy# 패키지 설치
!pip install psycopg2-binary pandas

import psycopg2
import pandas as pd

# 연결 (Colab에서)
import os
os.environ['DATABASE_URL'] = 'postgresql://...'

conn = psycopg2.connect(os.environ['DATABASE_URL'])
df = pd.read_sql("SELECT * FROM bid_results LIMIT 1000", conn)
df.head()
5. 데이터 수정/삭제
5.1 주의사항
⚠️ 직접 수정/삭제는 권장하지 않습니다.

GitHub Actions의 Data Management 워크플로우 사용 권장
직접 수정 시 반드시 백업 후 진행
트랜잭션 사용 권장
5.2 백업
전체 백업

CopyCREATE TABLE bid_results_backup AS 
SELECT * FROM bid_results;
특정 월 백업

CopyCREATE TABLE bid_results_202412 AS 
SELECT * FROM bid_results
WHERE TO_CHAR(rgst_dt, 'YYYY-MM') = '2024-12';
5.3 삭제
특정 월 삭제

CopyBEGIN;
DELETE FROM bid_results
WHERE TO_CHAR(rgst_dt, 'YYYY-MM') = '2024-12';
COMMIT;
중복 제거

CopyDELETE FROM bid_results a
USING bid_results b
WHERE a.id > b.id
AND a.bid_ntce_no = b.bid_ntce_no
AND a.bid_ntce_ord = b.bid_ntce_ord
AND a.bid_clsfc_no = b.bid_clsfc_no;
6. 성능 최적화
6.1 인덱스 활용
자주 사용하는 조회 조건에 인덱스 추가:

Copy-- 업체명 검색용
CREATE INDEX idx_bidwinnr_nm ON bid_results(bidwinnr_nm);

-- 기관명 검색용
CREATE INDEX idx_dminstt_nm ON bid_results(dminstt_nm);

-- 금액 범위 검색용
CREATE INDEX idx_sucsf_bid_amt ON bid_results(sucsf_bid_amt);
6.2 쿼리 최적화
LIMIT 사용

Copy-- 전체 조회 대신
SELECT * FROM bid_results LIMIT 1000;
필요한 컬럼만 조회

Copy-- SELECT * 대신
SELECT bid_ntce_nm, bidwinnr_nm, sucsf_bid_amt
FROM bid_results;
EXPLAIN으로 실행계획 확인

CopyEXPLAIN ANALYZE
SELECT * FROM bid_results
WHERE rgst_dt >= '2024-01-01';
7. 보안 주의사항
접속 정보 관리

연결 문자열을 코드에 직접 작성하지 않기
환경변수 또는 설정 파일 사용
GitHub에 비밀번호 업로드 금지
접근 권한

읽기 전용 사용자 생성 검토
필요시 IP 제한 설정
데이터 보호

개인정보(전화번호 등) 처리 주의
외부 공유 시 민감정보 마스킹
