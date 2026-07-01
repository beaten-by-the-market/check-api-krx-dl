# CHECK API Domain: news

Endpoint count: 7

## gongsi

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /news/gongsi/gongsi_basic | 공시-제목-전체-일별 구간 | cust_id, auth_key, sdate, edate | dcnt | 15 |
| /news/gongsi/gongsi_body | 공시-본문 | cust_id, auth_key, ndate, ncode |  | 4 |
| /news/gongsi/gongsi_jong | 공시-제목-종목별-일별 구간 | cust_id, auth_key, jcode, sdate, edate | dcnt | 14 |

## news

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /news/news/news_basic | 뉴스-제목-전체-일별 구간 | cust_id, auth_key, sdate, edate | dcnt | 14 |
| /news/news/news_body | 뉴스-본문 | cust_id, auth_key, ndate, ncode |  | 4 |
| /news/news/news_jong | 뉴스-제목-종목별-일별 구간 | cust_id, auth_key, jcode, sdate, edate | dcnt | 14 |
| /news/news/news_mtvcd | 뉴스-뉴스원 | cust_id, auth_key |  | 2 |
