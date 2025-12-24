# 나라장터 데이터 수집 시스템 운영 매뉴얼

## 1. 시스템 개요

### 1.1 목적
나라장터 공공조달 낙찰정보를 자동 수집하여 중소기업 입찰지원 서비스의 데이터 기반 구축

### 1.2 시스템 구성

| 구성요소 | 서비스 | 용도 |
|---------|--------|------|
| 스케줄러 | GitHub Actions | 자동 수집 실행 |
| 데이터베이스 | Neon PostgreSQL | 데이터 저장 |
| 대시보드 | GitHub Pages | 모니터링 |
| 소스코드 | GitHub Repository | 코드 관리 |

### 1.3 주요 URL

| 항목 | URL |
|------|-----|
| 대시보드 | https://cirrus0128.github.io/naramarket-collector/ |
| 저장소 | https://github.com/cirrus0128/naramarket-collector |
| Actions | https://github.com/cirrus0128/naramarket-collector/actions |
| 리포트 | https://github.com/cirrus0128/naramarket-collector/issues |

---

## 2. 일상 운영

### 2.1 자동 수집 스케줄

| 작업 | 실행 시간 (KST) | 설명 |
|------|----------------|------|
| 일일 수집 | 매일 00:00 | 전일 낙찰 데이터 수집 |
| 대시보드 업데이트 | 6시간마다 | 현황 데이터 갱신 |
| 일일 리포트 | 매일 09:00 | GitHub Issues에 리포트 생성 |

### 2.2 대시보드 확인

1. https://cirrus0128.github.io/naramarket-collector/ 접속
2. 확인 항목:
   - 총 데이터 건수
   - 사용 용량 (3GB 한도 대비)
   - 월별 수집 현황
   - 최근 수집 로그

### 2.3 수집 실패 확인

1. Actions 페이지 접속
2. 빨간색 X 표시 확인
3. 해당 워크플로우 클릭하여 에러 로그 확인

---

## 3. 수동 작업

### 3.1 월별 과거 데이터 수집

1. Actions → "Monthly Historical Collection" 클릭
2. "Run workflow" 클릭
3. 입력:
   - 수집 연도: 예) 2024
   - 수집 월: 예) 6
4. "Run workflow" 실행

### 3.2 현황 조회

1. Actions → "Data Management" 클릭
2. "Run workflow" 클릭
3. 작업 선택: "status (현황 조회)"
4. 실행 후 로그에서 결과 확인

### 3.3 월별 데이터 삭제

1. Actions → "Data Management" 클릭
2. "Run workflow" 클릭
3. 입력:
   - 작업 선택: "delete-month (월별 삭제)"
   - 연도: 예) 2024
   - 월: 예) 6
   - 삭제 확인: yes
4. 실행

### 3.4 전체 초기화 (주의)

1. Actions → "Data Management" 클릭
2. "Run workflow" 클릭
3. 입력:
   - 작업 선택: "reset-all (전체 초기화)"
   - 삭제 확인: yes
4. 실행

⚠️ **주의**: 전체 초기화 시 모든 데이터가 삭제됩니다.

---

## 4. 장애 대응

### 4.1 수집 실패 시

1. Actions에서 실패한 워크플로우 확인
2. 에러 로그 분석
3. 일반적인 원인:
   - API 서버 점검 중
   - API 호출 한도 초과
   - 네트워크 오류

4. 대응:
   - 1~2시간 후 수동 재실행
   - 지속 실패 시 공공데이터포털 공지사항 확인

### 4.2 용량 부족 시

1. 대시보드에서 용량 확인
2. 80% 초과 시:
   - 오래된 데이터 삭제 검토
   - Neon 유료 플랜 전환 검토

### 4.3 API 변경 대응

조달청 API 변경 시:
1. 공공데이터포털 공지사항 확인
2. API 문서 변경사항 파악
3. src/api_client.py 수정
4. 테스트 후 배포

---

## 5. 비용 관리

### 5.1 현재 비용 (1단계 MVP)

| 항목 | 서비스 | 비용 |
|------|--------|------|
| 스케줄러 | GitHub Actions | $0 (무료) |
| 데이터베이스 | Neon PostgreSQL | $0 (3GB 무료) |
| 대시보드 | GitHub Pages | $0 (무료) |
| **합계** | | **$0/월** |

### 5.2 확장 시 비용

| 단계 | 조건 | 예상 비용 |
|------|------|----------|
| 2단계 | 용량 50GB 필요 시 | $19/월 |
| 3단계 | AWS 전환 시 | $300~400/월 |

---

## 6. 연락처

### 6.1 API 관련 문의
- 공공데이터포털: 1566-0025
- 조달청 전자조달기획과: 042-724-7124

### 6.2 시스템 관련
- GitHub Issues에 등록
