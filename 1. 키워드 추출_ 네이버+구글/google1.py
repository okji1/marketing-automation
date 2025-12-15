import requests
import time


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


def recursive_collect(query, collected, max_keywords):
    if len(collected) >= max_keywords:
        return

    suggestions = google_autocomplete(query)
    print(f"🔍 '{query}' → {len(suggestions)}개 제안")

    for kw in suggestions:
        if len(collected) >= max_keywords:
            break

        if kw not in collected:
            collected.add(kw)
            time.sleep(0.3)
            recursive_collect(kw, collected, max_keywords)


# 실행
seed = input("🔑 키워드 입력: ").strip()
collected_keywords = set()
recursive_collect(seed, collected_keywords, max_keywords=100)

# 출력
print(f"\n📌 총 수집된 키워드 수: {len(collected_keywords)}")
for i, kw in enumerate(collected_keywords, 1):
    print(f"{i}. {kw}")
