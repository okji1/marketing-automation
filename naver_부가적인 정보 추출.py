import time
import requests
import base64
import hmac
import hashlib


class Signature:

    @staticmethod
    def generate(timestamp, method, uri, secret_key):
        message = "{}.{}.{}".format(timestamp, method, uri)
        hash = hmac.new(bytes(secret_key, "utf-8"),
                        bytes(message, "utf-8"), hashlib.sha256)

        hash.hexdigest()
        return base64.b64encode(hash.digest())


# --- API 인증 정보 ---
BASE_URL = 'https://api.searchad.naver.com'
API_KEY = '0100000000494cade1912d71b68bbff42a0b25af7feee034a98b2e8941c140ea4c3254b31f'
SECRET_KEY = 'AQAAAABJTK3hkS1xtou/9CoLJa9/n972brGWeTTn7amLhlhNrw=='
CUSTOMER_ID = '3488393'

# --- 헤더 생성 함수 ---


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    # Signature.generate 함수는 timestamp, method, uri, secret_key를 이용해 서명 생성
    signature = Signature.generate(timestamp, method, uri, secret_key)
    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }


# --- 키워드 도구 API 호출 ---
uri = '/keywordstool'
method = 'GET'
keyword_to_search = input("검색할 키워드를 입력하세요: ")

# 요청 URL 생성 (쿼리 파라미터 포함)
request_url = BASE_URL + uri + \
    f'?hintKeywords={keyword_to_search}&showDetail=1'

# 헤더 생성
headers = get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID)

# API 요청 보내기
response = requests.get(request_url, headers=headers)

# 결과 확인 (JSON 형식)
if response.status_code == 200:
    result = response.json()
    # 예시: 첫 번째 키워드 정보 출력
    if result.get('keywordList'):
        print(result['keywordList'][0])
    else:
        print("키워드 정보를 찾을 수 없습니다.")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
