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
