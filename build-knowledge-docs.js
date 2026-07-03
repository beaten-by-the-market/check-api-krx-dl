const fs = require("fs");
const path = require("path");

const root = process.cwd();
const docsDir = path.join(root, "docs");
const check = JSON.parse(fs.readFileSync(path.join(root, "checkapi-specs.json"), "utf8"));
const kq = JSON.parse(fs.readFileSync(path.join(root, "kquant-docs.json"), "utf8"));

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function write(rel, content) {
  const file = path.join(docsDir, rel);
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, `${content.trimEnd()}\n`, "utf8");
}

function csv(value) {
  return `"${String(value ?? "").replace(/"/g, '""')}"`;
}

function table(headers, rows) {
  return [
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
    ...rows.map((row) => `| ${row.map((v) => String(v ?? "").replace(/\n/g, "<br>")).join(" | ")} |`),
  ].join("\n");
}

function requiredParams(spec) {
  return (spec.param || []).filter((p) => p.req === "O").map((p) => p.name).join(", ");
}

function optionalParams(spec) {
  return (spec.param || []).filter((p) => p.req !== "O").map((p) => p.name).join(", ");
}

function domainOf(spec) {
  return spec.apiurl.split("/")[1] || "unknown";
}

function familyOf(spec) {
  return spec.apiurl.split("/")[2] || "unknown";
}

function titleOf(spec) {
  return (spec.title || "").replace(/^\[/, "").replace(/\]$/, "");
}

function routeDescription(apiurl) {
  const pieces = apiurl.split("/").filter(Boolean);
  const domain = pieces[0] || "";
  const family = pieces[1] || "";
  const action = pieces[2] || "";
  return { domain, family, action };
}

function groupBy(items, keyFn) {
  const out = {};
  for (const item of items) {
    const key = keyFn(item);
    out[key] ||= [];
    out[key].push(item);
  }
  return out;
}

function sampleFields(spec, limit = 12) {
  const fields = spec.res || [];
  const shown = fields.slice(0, limit).map((f) => `${f.name}(${f.desc})`).join(", ");
  return fields.length > limit ? `${shown}, ...` : shown;
}

function kqModule(fn) {
  return fn.path.split("/").slice(0, -1).join(".");
}

function writeRootReadme() {
  write(
    "README.md",
    `# CHECK API / kquant Knowledge Base

이 폴더는 CHECK API 공식 SPA 명세와 KOSCOM kquant 문서를 바탕으로 만든 작업용 지식 베이스입니다. 목적은 두 가지입니다.

1. 챗봇이 API/함수/파라미터 질문에 일관되게 답할 수 있게 한다.
2. 사용자의 CHECK API 인증 정보가 있을 때 데이터를 실제로 불러오는 코드를 빠르게 작성할 수 있게 한다.

## 폴더 구조

- \`checkapi/\`: 원천 CHECK API REST endpoint 문서
- \`kquant/\`: Python 패키지 \`kquant\` 사용 문서와 CHECK API 매핑
- \`chatbot/\`: 챗봇 답변 규칙, 조회 라우팅, 검색 인덱스
- \`catalogs/\`: CSV 형태의 endpoint/function catalog
- \`examples/python/\`: 바로 실행 가능한 Python 예제 클라이언트

## 빠른 판단

- Python에서 주식/지수/펀드/일부 채권/FX 데이터를 편하게 가져올 때는 먼저 \`kquant\`를 쓴다.
- kquant에 없는 endpoint, 파생/해외/뉴스/공시/기타 재무 endpoint는 CHECK API raw 호출을 쓴다.
- 실제 데이터 조회에는 CHECK API의 \`cust_id\`와 \`auth_key\`가 필요하다.
- 인증 정보가 없으면 명세 설명과 코드 예시는 가능하지만 실제 데이터는 받을 수 없다.

## 원천 산출물

- \`../checkapi-specs.json\`: CHECK API 전체 명세 747개
- \`../kquant-docs.json\`: kquant 문서 96개 함수/타입
- \`../checkapi-summary.md\`, \`../kquant-summary.md\`: 추출 요약
`
  );

  write(
    "FOLDER_STRUCTURE.md",
    `# Folder Structure

\`\`\`text
docs/
  README.md                         전체 지식 베이스 안내
  FOLDER_STRUCTURE.md               폴더/파일 역할 설명

  checkapi/
    README.md                       CHECK API 개요
    quickstart.md                   raw REST 호출 방법
    endpoint-catalog.md             747개 endpoint 전체 목록
    parameters.md                   공통/고유 입력 파라미터 사전
    errors.md                       에러 코드와 처리 가이드
    recipes.md                      목적별 조회 레시피
    domains/
      stock.md                      주식 250개 endpoint
      future.md                     파생 331개 endpoint
      bond.md                       채권 60개 endpoint
      ext.md                        해외 73개 endpoint
      news.md                       뉴스/공시 7개 endpoint
      etc.md                        경제/기업/재무 등 26개 endpoint

  kquant/
    README.md                       kquant 개요와 설치/인증
    function-catalog.md             96개 공개 함수/타입 목록
    checkapi-mapping.md             kquant 함수 -> CHECK API endpoint 매핑
    data-loading-recipes.md         kquant 데이터 로딩 예시
    backtest-analysis.md            백테스트/기술분석 함수 설명

  chatbot/
    README.md                       챗봇 운영 원칙
    answer-playbook.md              질문 유형별 답변 템플릿
    retrieval-index.md              챗봇 검색용 축약 인덱스

  catalogs/
    checkapi-endpoints.csv          endpoint 필터용 CSV
    checkapi-response-fields.csv    F-code 응답 필드 사전 CSV
    kquant-functions.csv            kquant 함수 필터용 CSV
    chatbot-retrieval-index.csv     챗봇 검색용 CSV

  examples/
    python/
      checkapi_raw_client.py        CHECK API 직접 호출 클라이언트
      kquant_data_loader.py         kquant 데이터 로더 예제
\`\`\`

## 사용 흐름

1. 무슨 데이터가 필요한지 정한다.
2. 먼저 \`kquant/checkapi-mapping.md\`에서 kquant 함수가 있는지 확인한다.
3. 있으면 \`kquant/data-loading-recipes.md\`와 \`examples/python/kquant_data_loader.py\`를 사용한다.
4. 없으면 \`checkapi/endpoint-catalog.md\`에서 endpoint를 찾고 \`examples/python/checkapi_raw_client.py\`를 사용한다.
5. 챗봇 답변 품질을 맞출 때는 \`chatbot/README.md\`와 \`chatbot/answer-playbook.md\`를 기준으로 한다.
`
  );
}

function writeCheckApiDocs() {
  write(
    "checkapi/README.md",
    `# CHECK API

CHECK API는 \`https://checkapi.koscom.co.kr\`를 base URL로 사용하는 금융 데이터 REST API입니다.

## 규모

- 전체 endpoint: ${check.counts.specs}
- 도메인: ${Object.keys(check.by_domain).join(", ")}
- 고유 입력 파라미터: ${check.counts.unique_params}
- 고유 응답 필드: ${check.counts.unique_response_fields}
- 고유 에러 코드: ${check.counts.unique_errors}

## 기본 호출 형태

\`\`\`text
POST https://checkapi.koscom.co.kr{apiurl}
Content-Type: application/x-www-form-urlencoded

cust_id=...&auth_key=...&jcode=...
\`\`\`

**반드시 \`POST\`로 호출하고 파라미터는 요청 본문(body)에 담아야 합니다.** \`GET\`으로 보내거나, \`POST\`라도 파라미터를 URL 쿼리스트링에 넣으면 자격증명이 맞아도 \`{"success": false, "message": "cust_id 또는 auth_key가 정확하지 않습니다."}\`로 거부됩니다. 본문 형식은 form-urlencoded와 JSON 둘 다 동작합니다.

**접근 IP 제한:** CHECK API는 발급 시 등록한 IP에서의 호출만 허용합니다. 자격증명이 정확해도 등록되지 않은 IP(사내 프록시, 클라우드/컨테이너, 샌드박스 등 다른 경로)로 나가면 위와 동일한 \`success: false\` 인증 실패 메시지로 거부됩니다. 즉 이 메시지는 "키가 틀렸다"만이 아니라 "IP가 등록 대상이 아니다"일 수도 있습니다. MCP 서버·배치·스케줄러는 반드시 **등록 IP 호스트에서 직접 실행**해야 합니다.

대부분 endpoint는 \`cust_id\`, \`auth_key\`가 필수입니다. 일부 조회는 \`jcode\`, \`sdate\`, \`edate\`, \`term\`, \`codelist\`, \`data_list\` 등을 추가로 받습니다.

## 자주 쓰는 공통 파라미터

${table(
  ["이름", "필수", "설명"],
  ["cust_id", "auth_key", "data_list", "jcode", "codelist", "sdate", "edate", "term", "up_code", "criteria_code", "dcnt"].map((name) => {
    const p = check.dictionaries.params[name] || {};
    return [name, p.req || "", p.desc || ""];
  })
)}

## 문서 읽는 순서

1. [quickstart.md](quickstart.md): raw API 호출 방식
2. [endpoint-catalog.md](endpoint-catalog.md): 전체 endpoint 한눈에 보기
3. [domains/](domains/): 도메인별 상세 목록
4. [recipes.md](recipes.md): 데이터 조회 목적별 예시
5. [errors.md](errors.md): 에러 처리
`
  );

  write(
    "checkapi/quickstart.md",
    `# CHECK API Quickstart

## 인증 정보

- \`cust_id\`: CHECK 단말 고객번호 10자리
- \`auth_key\`: API 인증키

인증이 틀리면 일반적으로 다음 형태가 내려옵니다.

\`\`\`json
{"success": false, "message": "cust_id 또는 auth_key가 정확하지 않습니다."}
\`\`\`

## curl 예시

\`\`\`bash
# 파라미터는 -d (요청 본문)로 전달. GET/쿼리스트링은 인증 거부됨.
curl -X POST "https://checkapi.koscom.co.kr/stock/m001/hist_info" \\
  -d "cust_id=$CHECK_CUST_ID" \\
  -d "auth_key=$CHECK_AUTH_KEY" \\
  -d "jcode=005930" \\
  -d "sdate=20250101" \\
  -d "edate=20250131"
\`\`\`

## Python requests 예시

\`\`\`python
import os
import requests

BASE_URL = "https://checkapi.koscom.co.kr"

params = {
    "cust_id": os.environ["CHECK_CUST_ID"],
    "auth_key": os.environ["CHECK_AUTH_KEY"],
    "jcode": "005930",
    "sdate": "20250101",
    "edate": "20250131",
}

# 파라미터는 params(쿼리스트링)가 아니라 data(요청 본문)로 전달해야 합니다.
response = requests.post(f"{BASE_URL}/stock/m001/hist_info", data=params, timeout=60)
response.raise_for_status()
data = response.json()
print(data)
\`\`\`

## 응답 처리 원칙

- \`success: true\`이면 \`results\`를 pandas DataFrame으로 변환한다.
- \`success: false\`이면 \`message\` 또는 \`errmsg\`를 사용자에게 그대로 보여준다.
- \`data_list\`를 비우면 전체 필드를 조회한다. 네트워크/응답 크기를 줄이고 싶으면 필요한 F-code만 쉼표로 넘긴다.

## 응답 필드는 F-code다

\`results\`의 각 행은 컬럼명이 한글이 아니라 **F-code**입니다. 예를 들어 \`/stock/m001/hist_info\` 응답은 이렇게 내려옵니다.

\`\`\`json
{"F12506": 20250605, "F16013": "005930", "F15001": "59100", "F15010": "59900", "F15011": "57900"}
\`\`\`

| F-code | 의미 |
| --- | --- |
| F12506 | 입회일 |
| F16013 | 단축코드 |
| F15001 | 현재가 |
| F15010 | 고가 |
| F15011 | 저가 |

사람이 읽는 컬럼명으로 바꾸려면 \`../catalogs/checkapi-response-fields.csv\`(전체 F-code 사전) 또는 \`../../checkapi-specs.json\`의 \`specs[].res\`로 **F-code → 설명**을 매핑하세요. endpoint마다 내려오는 F-code 집합이 다르므로, 클라이언트/MCP에서는 해당 endpoint의 \`res\` 정의를 기준으로 디코딩하는 것이 안전합니다.
`
  );

  write(
    "checkapi/errors.md",
    `# CHECK API Errors

${table(
  ["errmsg", "영문 설명", "한글 설명"],
  Object.values(check.dictionaries.errors).map((e) => [e.errmsg, e.desc, e.detail])
)}

## 처리 가이드

- \`access_denied\`: \`cust_id\`, \`auth_key\` 재확인. 값이 맞는데도 거부되면 **호출 IP가 발급 시 등록한 IP인지** 확인 (등록 외 IP도 같은 인증 실패로 응답)
- \`jcode_denied\`: 종목코드/업종코드 시장 구분 재확인
- \`date_denied\`: \`YYYYMMDD\` 형식 및 조회 가능 기간 확인
- \`term_denied\`: \`daily\`, \`weekly\`, \`monthly\`, \`quarterly\`, \`YTD\`, \`yearly\` 등 endpoint 설명에 맞는 값 사용
- \`criteria_code_denied\`: 순위 조회 기준 필드가 해당 endpoint의 Data Set에 있는지 확인
`
  );

  const catalogRows = check.specs.map((s) => [
    s.apiurl,
    domainOf(s),
    familyOf(s),
    titleOf(s),
    requiredParams(s),
    optionalParams(s),
    (s.res || []).length,
    sampleFields(s, 8),
  ]);
  write(
    "checkapi/endpoint-catalog.md",
    `# CHECK API Endpoint Catalog

전체 ${check.specs.length}개 endpoint 목록입니다. 응답 필드 전체는 \`../../checkapi-specs.json\`의 \`specs[].res\`를 보세요.

${table(["API URL", "도메인", "패밀리", "제목", "필수 파라미터", "선택 파라미터", "응답 필드 수", "대표 필드"], catalogRows)}
`
  );

  const paramRows = Object.values(check.dictionaries.params)
    .filter((p) => p.name)
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((p) => [p.name, p.type || "", p.req || "", p.desc || ""]);
  write(
    "checkapi/parameters.md",
    `# CHECK API Parameter Dictionary

${table(["이름", "타입", "필수", "설명"], paramRows)}
`
  );

  const fieldCsv = ["name,type,description,detail"];
  for (const f of Object.values(check.dictionaries.response_fields).sort((a, b) => a.name.localeCompare(b.name))) {
    fieldCsv.push([f.name, f.type, f.desc, f.detail].map(csv).join(","));
  }
  write("catalogs/checkapi-response-fields.csv", fieldCsv.join("\n"));

  const endpointCsv = ["apiurl,domain,family,title,required_params,optional_params,response_field_count"];
  for (const s of check.specs) {
    endpointCsv.push([s.apiurl, domainOf(s), familyOf(s), titleOf(s), requiredParams(s), optionalParams(s), (s.res || []).length].map(csv).join(","));
  }
  write("catalogs/checkapi-endpoints.csv", endpointCsv.join("\n"));

  const byDomain = groupBy(check.specs, domainOf);
  for (const [domain, specs] of Object.entries(byDomain).sort()) {
    const byFamily = groupBy(specs, familyOf);
    const lines = [`# CHECK API Domain: ${domain}`, "", `Endpoint count: ${specs.length}`, ""];
    for (const [family, familySpecs] of Object.entries(byFamily).sort()) {
      lines.push(`## ${family}`, "");
      lines.push(
        table(
          ["API URL", "제목", "필수 파라미터", "선택 파라미터", "응답 필드 수"],
          familySpecs.map((s) => [s.apiurl, titleOf(s), requiredParams(s), optionalParams(s), (s.res || []).length])
        )
      );
      lines.push("");
    }
    write(`checkapi/domains/${domain}.md`, lines.join("\n"));
  }

  write(
    "checkapi/recipes.md",
    `# CHECK API Recipes

## 주식 종목 코드 목록

- KOSPI: \`/stock/m001/code_info\`
- KOSDAQ: \`/stock/m003/code_info\`
- 주요 파라미터: \`cust_id\`, \`auth_key\`

## 삼성전자 일봉

- endpoint: \`/stock/m001/hist_info\`
- 필수: \`cust_id\`, \`auth_key\`, \`jcode=005930\`, \`sdate=YYYYMMDD\`, \`edate=YYYYMMDD\`
- 대표 응답: 날짜(\`F12506\`), 단축코드(\`F16013\`), 현재가/시고저/거래량/거래대금

## 코스닥 종목 일봉

- endpoint: \`/stock/m003/hist_info\`
- 필수 파라미터는 KOSPI와 동일하고 시장 endpoint만 다르다.

## 호가/체결

- 호가: \`/stock/m001/hoga_info\`, \`/stock/m003/hoga_info\`
- 체결: \`/stock/m001/tick_info\`, \`/stock/m003/tick_info\`
- 일자별 체결: \`/stock/m001/tick_date\`, \`/stock/m003/tick_date\`

## 기간봉

- 주식: \`/stock/m001/term_hist_info\`, \`/stock/m003/term_hist_info\`
- \`term\`: \`daily\`, \`weekly\`, \`monthly\`, \`quarterly\`, \`YTD\`, \`yearly\`

## kquant에 없는 도메인

파생(\`future\`), 해외(\`ext\`), 뉴스/공시(\`news\`), 기타 재무/경제(\`etc\`)는 raw CHECK API 호출을 기본으로 한다. endpoint는 [endpoint-catalog.md](endpoint-catalog.md)에서 검색한다.
`
  );
}

function writeKquantDocs() {
  write(
    "kquant/README.md",
    `# kquant

\`kquant\`는 KOSCOM이 배포한 Python 패키지입니다. CHECK API 일부 endpoint를 pandas DataFrame/Series 중심 함수로 감싸고, 차트/백테스트/기술 분석 유틸을 제공합니다.

## 패키지 정보

- 최신 확인 버전: 0.3.6
- Python: >=3.9
- 라이선스: Commercial
- PyPI: https://pypi.org/project/kquant/0.3.6/
- GitHub 문서 저장소: https://github.com/koscom/kquant

## 문서 기준 규모

- 공개 함수/타입 문서: ${kq.counts.functions}
- 데이터 조회 함수: ${kq.functions.filter((f) => f.path.startsWith("data/")).length}
- CHECK API endpoint를 직접 감싸는 함수: ${kq.counts.functions_with_check_api_urls}
- 연결된 CHECK API endpoint: ${kq.counts.unique_check_api_urls}

## 설치

\`\`\`bash
pip install kquant
\`\`\`

## 기본 사용

\`\`\`python
import kquant as kq

kq.set_api("발급받은 API ID", "발급받은 API KEY")
df = kq.daily_stock("005930")
print(df.tail())
\`\`\`

## 언제 kquant를 쓰나

- 주식/지수/펀드/일부 채권/FX 데이터를 pandas로 바로 받고 싶을 때
- 백테스트/차트/기술 지표 계산까지 이어갈 때
- CHECK API F-code를 직접 다루기보다 표준 컬럼명(\`OPEN\`, \`HIGH\`, \`LOW\`, \`CLOSE\`, \`VOLUME\`)을 쓰고 싶을 때
`
  );

  const byModule = groupBy(kq.functions, kqModule);
  const lines = ["# kquant Function Catalog", ""];
  for (const [moduleName, fns] of Object.entries(byModule).sort()) {
    lines.push(`## ${moduleName}`, "");
    lines.push(table(["함수", "설명", "시그니처"], fns.map((f) => [f.name, f.description, `\`${f.signature || ""}\``])));
    lines.push("");
  }
  write("kquant/function-catalog.md", lines.join("\n"));

  const mappingRows = kq.functions
    .filter((f) => f.api_urls.length)
    .map((f) => [f.name, kqModule(f), f.description, f.api_urls.join("<br>")]);
  write(
    "kquant/checkapi-mapping.md",
    `# kquant to CHECK API Mapping

kquant 함수가 내부적으로 사용하는 CHECK API endpoint 목록입니다.

${table(["kquant 함수", "모듈", "설명", "CHECK API"], mappingRows)}
`
  );

  const fnCsv = ["path,module,name,description,signature,check_api_urls"];
  for (const f of kq.functions) {
    fnCsv.push([f.path, kqModule(f), f.name, f.description, f.signature, f.api_urls.join(" ")].map(csv).join(","));
  }
  write("catalogs/kquant-functions.csv", fnCsv.join("\n"));

  write(
    "kquant/data-loading-recipes.md",
    `# kquant Data Loading Recipes

## 인증 정보 설정

\`\`\`python
import kquant as kq

kq.set_api("API_ID", "API_KEY")
api_id, api_key = kq.get_api()
\`\`\`

\`get_api()\`는 설정 파일이 없으면 \`FileNotFoundError\`를 낼 수 있습니다.

## 종목 목록

\`\`\`python
import kquant as kq

stocks = kq.symbol_stock()
kospi = kq.symbol_kospi_stock()
kosdaq = kq.symbol_kosdaq_stock()
funds = kq.symbol_fund()
\`\`\`

## 일봉

\`\`\`python
df = kq.daily_stock("005930", start_date="20250101", end_date="20250131")
fund = kq.daily_fund("069500")
kospi_index = kq.daily_kospi_index("001")
\`\`\`

## 일중/체결/호가

\`\`\`python
minute = kq.intra_stock("005930", interval="1M")
tick = kq.trade_stock("005930", count=100, loc="last")
quote = kq.quote_stock("005930")
\`\`\`

## 투자자/공매도/대차/신용/대량매매

\`\`\`python
investor = kq.sum_investor_stocks(start_date="20250101", end_date="20250131")
short = kq.daily_short_stock("005930")
lend = kq.daily_lend_stock("005930")
margin = kq.daily_margin_stock("005930")
block = kq.daily_block_stock("005930")
\`\`\`

## kquant에 없는 데이터

kquant mapping에 없는 endpoint는 \`examples/python/checkapi_raw_client.py\`의 \`CheckApiClient\`를 사용한다.
`
  );

  write(
    "kquant/backtest-analysis.md",
    `# kquant Backtest / Analysis

## 백테스트 핵심 함수

${table(
  ["함수", "설명", "시그니처"],
  kq.functions
    .filter((f) => f.path.startsWith("analysis/stock/backtest"))
    .map((f) => [f.name, f.description, `\`${f.signature}\``])
)}

## 기술 분석 문서 노출 함수

${table(
  ["함수", "설명", "시그니처"],
  kq.functions
    .filter((f) => f.path.startsWith("analysis/stock/ta"))
    .map((f) => [f.name, f.description, `\`${f.signature}\``])
)}

## 주의

- wheel 내부에는 더 많은 \`.pyd\` 모듈이 있지만 공식 문서 링크에 노출된 함수만 위 목록에 포함했다.
- 백테스트는 상한가/하한가/공매도/미수 허용 여부에 따라 사용자 경고 타입을 낼 수 있다.
- 실전 매매 체결 모델이 아니라 일봉 기준 검증용으로 보는 것이 안전하다.
`
  );
}

function writeChatbotDocs() {
  const retrievalRows = [];
  for (const s of check.specs) {
    retrievalRows.push(["checkapi", s.apiurl, `${domainOf(s)} ${familyOf(s)} ${titleOf(s)}`, requiredParams(s), optionalParams(s)]);
  }
  for (const f of kq.functions) {
    retrievalRows.push(["kquant", f.name, `${kqModule(f)} ${f.description}`, "", f.api_urls.join(" ")]);
  }

  write(
    "chatbot/README.md",
    `# Chatbot Guide

이 문서는 CHECK API/kquant 질의에 답하는 챗봇을 위한 운영 규칙입니다.

## 기본 원칙

1. 사용자가 Python/pandas 중심으로 데이터를 원하면 kquant 함수를 먼저 찾는다.
2. kquant에 없는 endpoint는 CHECK API raw 호출로 안내한다.
3. 실제 데이터 호출에는 \`cust_id\`/\`auth_key\` 또는 kquant \`set_api\`가 필요하다고 명확히 말한다.
4. 인증키 없이 실제 값을 만들어내지 않는다.
5. 날짜는 \`YYYYMMDD\` 또는 kquant가 받는 날짜 입력 형식으로 구체화한다.
6. 사용자가 시장을 말하지 않으면 종목 코드로 KOSPI/KOSDAQ 구분이 필요할 수 있다고 설명한다.

## 우선 참조 파일

- kquant 함수 찾기: \`../kquant/function-catalog.md\`
- kquant와 CHECK API 매핑: \`../kquant/checkapi-mapping.md\`
- raw endpoint 찾기: \`../checkapi/endpoint-catalog.md\`
- response F-code 찾기: \`../catalogs/checkapi-response-fields.csv\`
- 에러 처리: \`../checkapi/errors.md\`
`
  );

  write(
    "chatbot/answer-playbook.md",
    `# Answer Playbook

## 질문 유형별 라우팅

### "삼성전자 일봉 가져와줘"

추천 답변:

1. kquant 사용 가능 여부 확인
2. \`kq.daily_stock("005930", start_date="YYYYMMDD", end_date="YYYYMMDD")\` 제시
3. 인증이 없으면 \`kq.set_api(...)\` 먼저 안내

### "CHECK API endpoint 알려줘"

추천 답변:

1. endpoint URL
2. 필수/선택 파라미터
3. 주요 응답 필드
4. curl/Python raw 예시

### "kquant에 있나?"

추천 답변:

1. \`kquant/checkapi-mapping.md\`에서 함수 검색
2. 있으면 함수명/시그니처/연결 endpoint 제시
3. 없으면 raw CHECK API endpoint로 대체

### "실제로 데이터를 불러와줘"

추천 답변:

1. 로컬/환경 변수에 인증 정보가 있는지 확인
2. 있으면 \`examples/python\`의 클라이언트 패턴으로 호출
3. 없으면 필요한 인증 변수 이름과 실행 코드를 제공

## 답변 템플릿

\`\`\`text
가능합니다. 이 데이터는 [kquant 함수명 또는 CHECK API endpoint]로 조회합니다.

필수 입력:
- ...

Python 예시:
\`\`\`python
...
\`\`\`

주의:
- ...
\`\`\`
`
  );

  write(
    "chatbot/retrieval-index.md",
    `# Retrieval Index

챗봇 검색용 축약 인덱스입니다.

${table(["종류", "키", "검색어/설명", "필수", "보조"], retrievalRows)}
`
  );

  const csvLines = ["kind,key,description,required,extra"];
  for (const row of retrievalRows) csvLines.push(row.map(csv).join(","));
  write("catalogs/chatbot-retrieval-index.csv", csvLines.join("\n"));
}

function writeExamples() {
  write(
    "examples/python/checkapi_raw_client.py",
    `"""Small CHECK API raw client.

Environment variables:
    CHECK_CUST_ID: CHECK terminal customer id
    CHECK_AUTH_KEY: CHECK API auth key
"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests


class CheckApiClient:
    def __init__(
        self,
        cust_id: str | None = None,
        auth_key: str | None = None,
        base_url: str = "https://checkapi.koscom.co.kr",
        timeout: int = 60,
    ) -> None:
        self.cust_id = cust_id or os.environ["CHECK_CUST_ID"]
        self.auth_key = auth_key or os.environ["CHECK_AUTH_KEY"]
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, apiurl: str, **params: Any) -> dict[str, Any]:
        payload = {
            "cust_id": self.cust_id,
            "auth_key": self.auth_key,
            **{k: v for k, v in params.items() if v is not None},
        }
        # CHECK API는 파라미터를 요청 본문(body)으로 받는 POST만 허용합니다.
        response = requests.post(f"{self.base_url}{apiurl}", data=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if data.get("success") is False:
            raise RuntimeError(data.get("message") or data.get("errmsg") or data)
        return data

    def dataframe(self, apiurl: str, **params: Any) -> pd.DataFrame:
        data = self.request(apiurl, **params)
        results = data.get("results", data)
        return pd.DataFrame(results if isinstance(results, list) else [results])


if __name__ == "__main__":
    client = CheckApiClient()
    df = client.dataframe(
        "/stock/m001/hist_info",
        jcode="005930",
        sdate="20250101",
        edate="20250131",
    )
    print(df.tail())
`
  );

  write(
    "examples/python/kquant_data_loader.py",
    `"""kquant data loading examples.

Run:
    pip install kquant

Before use, either call kq.set_api(...) once or provide credentials in your
environment and call set_api from those values.
"""

from __future__ import annotations

import os

import kquant as kq


def configure_from_env() -> None:
    api_id = os.environ.get("CHECK_API_ID") or os.environ.get("CHECK_CUST_ID")
    api_key = os.environ.get("CHECK_API_KEY") or os.environ.get("CHECK_AUTH_KEY")
    if not api_id or not api_key:
        raise RuntimeError("Set CHECK_API_ID/CHECK_API_KEY or CHECK_CUST_ID/CHECK_AUTH_KEY.")
    kq.set_api(api_id, api_key)


def load_samsung_daily():
    return kq.daily_stock("005930", start_date="20250101", end_date="20250131")


def load_stock_universe():
    return kq.symbol_stock()


def load_intraday(symbol: str = "005930"):
    return kq.intra_stock(symbol, interval="1M")


if __name__ == "__main__":
    configure_from_env()
    print(load_samsung_daily().tail())
`
  );
}

function main() {
  ensureDir(docsDir);
  writeRootReadme();
  writeCheckApiDocs();
  writeKquantDocs();
  writeChatbotDocs();
  writeExamples();
  console.log(`Wrote knowledge docs to ${docsDir}`);
}

main();
