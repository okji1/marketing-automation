import requests
import json
import time

# ─── Google 키워드 수집 ────────────────────────────────


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


def google_recursive_collect(query, collected, max_keywords):
    if len(collected) >= max_keywords:
        return

    suggestions = google_autocomplete(query)
    print(f"🔍 Google: '{query}' → {len(suggestions)}개 제안")

    for kw in suggestions:
        if len(collected) >= max_keywords:
            break
        if kw not in collected:
            collected.add(kw)
            time.sleep(0.3)
            google_recursive_collect(kw, collected, max_keywords)

# ─── Naver 키워드 수집 ────────────────────────────────


def get_naver_keywords(keyword):
    url = f'https://ac.search.naver.com/nx/ac?q={keyword}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&st=100&_callback=_jsonp_4'
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://search.naver.com/"
    }

    try:
        res = requests.get(url, headers=headers).text
        ret = res.replace("_jsonp_4(", "").rstrip(")")
        jsonData = json.loads(ret)
        items = jsonData['items'][0]
        return [i[0] for i in items if i]
    except Exception as e:
        print(f"❌ Naver '{keyword}' 요청 실패: {e}")
        return []


def naver_collect(seed):
    all_keywords = set()
    first_level = get_naver_keywords(seed)
    print(f"\n✅ Naver 1차 키워드 ({len(first_level)}개):")
    for kw in first_level:
        print(f"  - {kw}")
    all_keywords.update(first_level)

    for kw in first_level:
        time.sleep(1.0)
        second_level = get_naver_keywords(kw)
        print(f"\n🔄 Naver: '{kw}' → {len(second_level)}개 제안")
        all_keywords.update(second_level)

    return all_keywords


# ─── 실행부 ──────────────────────────────────────────
if __name__ == "__main__":
    seed = input("🔑 키워드 입력: ").strip()

    google_keywords = set()
    google_recursive_collect(seed, google_keywords, max_keywords=100)

    naver_keywords = naver_collect(seed)

    # 공통 키워드 추출
    common_keywords = sorted(google_keywords & naver_keywords)

    # 결과 출력
    print(f"\n📦 Google 키워드 수: {len(google_keywords)}")
    print(f"📦 Naver 키워드 수: {len(naver_keywords)}")
    print(f"\n✅ 공통 키워드 수: {len(common_keywords)}개\n")
    for i, kw in enumerate(common_keywords, 1):
        print(f"{i}. {kw}")
