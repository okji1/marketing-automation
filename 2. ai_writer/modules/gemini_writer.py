import os
import configparser
import google.generativeai as genai


def load_api_key(path=None) -> str:
    if path is None:
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'api_key.ini'))

    config = configparser.ConfigParser()
    config.read(path)

    return config["gemini"]["api_key"]


def generate_article(prompt: str, model_name="gemini-1.5-flash") -> str:
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "❌ 글 생성 실패"
    except Exception as e:
        return f"❌ 에러 발생: {e}"
