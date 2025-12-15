import requests
import json
import time


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
        print(f"❌ '{keyword}' 요청 실패: {e}")
        return []


# 실행
keyword = input("🔑 키워드 입력: ").strip()
all_keywords = set()

# 1단계
first_level = get_naver_keywords(keyword)
print(f"\n✅ 1차 키워드 ({len(first_level)}개):")
for kw in first_level:
    print(f"  - {kw}")
all_keywords.update(first_level)

# 2단계
for kw in first_level:
    time.sleep(1.0)
    second_level = get_naver_keywords(kw)
    print(f"\n🔄 '{kw}' → {len(second_level)}개 제안")
    all_keywords.update(second_level)

# 최종 출력
print(f"\n📌 총 수집된 키워드 수: {len(all_keywords)}")
for i, kw in enumerate(sorted(all_keywords), 1):
    print(f"{i}. {kw}")
