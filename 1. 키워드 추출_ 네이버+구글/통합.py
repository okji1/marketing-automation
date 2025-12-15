# 통합 키워드 수집 및 검색량 기반 필터링 프로그램

import requests
import json
import time
import base64
import hmac
import hashlib
import pandas as pd
import re

from bs4 import BeautifulSoup


def fetch_keyword_info_via_ui(keyword):
    url = "http://220.95.52.164/crawling/keyword_api.php"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'keyword': keyword}
    try:
        res = requests.post(url, data=data, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('table tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if cols and keyword in cols[0].text:
                    return {
                        '키워드': cols[0].text.strip(),
                        'PC검색량': int(cols[1].text.replace(',', '').strip()),
                        '모바일검색량': int(cols[2].text.replace(',', '').strip()),
                        '경쟁도': '-'  # 경쟁도는 제공되지 않으므로 대체값
                    }
    except Exception as e:
        print(f"⚠️ '{keyword}' 요청 실패: {e}")
    return None


# =======================
# 1. 구글 자동완성 수집
# =======================


def google_autocomplete(query):
    url = "https://suggestqueries.google.com/complete/search"
    params = {
        "client": "firefox",
        "hl": "ko",
        "q": query
    }
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            return res.json()[1]
    except:
        pass
    return []


def google_collect(seed, max_keywords=100):
    collected = set()

    def recursive_collect(query):
        if len(collected) >= max_keywords:
            return
        suggestions = google_autocomplete(query)
        for kw in suggestions:
            if len(collected) >= max_keywords:
                break
            if kw not in collected:
                collected.add(kw)
                time.sleep(0.3)
                recursive_collect(kw)

    recursive_collect(seed)
    return collected

# =======================
# 2. 네이버 자동완성 수집
# =======================


def get_naver_keywords(keyword):
    url = f'https://ac.search.naver.com/nx/ac?q={keyword}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&st=100&_callback=_jsonp_4'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://search.naver.com/"
    }

    try:
        res = requests.get(url, headers=headers).text
        ret = res.replace("_jsonp_4(", "").rstrip(")")
        jsonData = json.loads(ret)
        items = jsonData['items'][0]
        return [i[0] for i in items if i]
    except Exception as e:
        print(f"\n❌ 네이버 오류: {e}")
        return []


def naver_collect(seed):
    all_keywords = set()
    first_level = get_naver_keywords(seed)
    all_keywords.update(first_level)

    for kw in first_level:
        time.sleep(1.0)
        second_level = get_naver_keywords(kw)
        all_keywords.update(second_level)

    return all_keywords


# =======================
# 3. 네이버 검색광고 API 연결
# =======================
BASE_URL = 'https://api.searchad.naver.com'
API_KEY = '<API_KEY>'
SECRET_KEY = '<SECRET_KEY>'
CUSTOMER_ID = '<CUSTOMER_ID>'


def generate_signature(timestamp, method, uri, secret_key):
    message = f"{timestamp}.{method}.{uri}"
    hash = hmac.new(bytes(secret_key, "utf-8"),
                    bytes(message, "utf-8"), hashlib.sha256)
    return base64.b64encode(hash.digest())


def get_header(method, uri):
    timestamp = str(round(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri, SECRET_KEY)
    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': API_KEY,
        'X-Customer': str(CUSTOMER_ID),
        'X-Signature': signature
    }


def fetch_keyword_info(keyword):
    uri = '/keywordstool'
    request_url = f"{BASE_URL}{uri}?hintKeywords={keyword}&showDetail=1"
    headers = get_header('GET', uri)
    res = requests.get(request_url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        if data.get('keywordList'):
            return data['keywordList'][0]
    return None


# =======================
# 4. 실행 흐름
# =======================
if __name__ == "__main__":
    seed = input("\n🔑 키워드 입력: ").strip()

    google_keywords = google_collect(seed)
    naver_keywords = naver_collect(seed)

    print(f"\n✅ Google 키워드 수집: {len(google_keywords)}개")
    print(f"✅ Naver 키워드 수집: {len(naver_keywords)}개")

    # 통합 및 중복 제거
    total_keywords = list(google_keywords | naver_keywords)
    print(f"📦 통합 키워드 수: {len(total_keywords)}개\n")

    # 검색량 정보 추가
    enriched_keywords = []
    for kw in total_keywords:
        info = fetch_keyword_info_via_ui(kw)
        if info:
            enriched_keywords.append(info)
        else:
            print(f"⚠️ '{kw}' 검색량 없음")
        time.sleep(0.5)

    if not enriched_keywords:
        print("❌ 검색량 데이터가 하나도 수집되지 않았습니다.")
        exit()

    # 검색량 기준 정렬 및 상위 100개 선택
    df = pd.DataFrame(enriched_keywords)
    df['총검색량'] = df['PC검색량'] + df['모바일검색량']
    df = df.sort_values(by='총검색량', ascending=False).head(100)

    # 출력 및 저장
    print(df[['키워드', '총검색량', '경쟁도']].to_string(index=False))
    if not df.empty:
        df.to_csv('filtered_keywords.csv', index=False, encoding='utf-8-sig')
    else:
        print("❌ 저장할 키워드 데이터가 없습니다.")
