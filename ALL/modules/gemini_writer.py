import os
import sys
import configparser
import google.generativeai as genai


def load_api_key(path=None) -> str:
    # 1) exe 환경인지 확인
    if getattr(sys, "frozen", False):
        # PyInstaller --onefile 로 묶인 경우, exe와 같은 폴더에서 찾기
        base_path = os.path.dirname(sys.executable)
    else:
        # .py 로 실행할 때
        base_path = os.path.dirname(os.path.dirname(__file__))  # ALL 폴더로 이동

    # 2) config.ini 경로 설정
    if path is None:
        path = os.path.join(base_path, "config.ini")

    # 3) 파일 읽기
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')

    # 4) 안전하게 값 읽기
    try:
        return config["gemini"]["api_key"]
    except KeyError:
        raise Exception("config.ini에서 [gemini] 섹션 또는 api_key를 찾을 수 없습니다.")


def generate_article(prompt: str, model_name="gemini-1.5-flash") -> str:
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "❌ 글 생성 실패"
    except Exception as e:
        return f"❌ 에러 발생: {e}"
