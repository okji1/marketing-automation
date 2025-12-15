from modules.gemini_writer import generate_article
import configparser
import os


def load_prompt_config():
    """prompt_config.ini에서 설정을 읽어오는 함수"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), "prompt_config.ini")

    # 기본값 설정
    default_settings = {
        'word_count': '300',
        'subtitle_format': '[소제목]',
        'include_keywords': 'yes',
        'keyword_count': '5',
        'custom_instruction': '소제목이 있고, 소제목은 [소제목] 형태로 써주고, 소제목을 쓸 때는 반드시 소제목 바로 위에 줄바꿈 2번(빈 줄 1줄)을 추가해줘. 단, 소제목과 그 소제목의 본문 사이에는 줄바꿈이 2번 오면 안 돼.'
    }

    try:
        config.read(config_path, encoding='utf-8')
        if config.has_section('prompt_settings'):
            return {
                'word_count': config.get('prompt_settings', 'word_count', fallback=default_settings['word_count']),
                'subtitle_format': config.get('prompt_settings', 'subtitle_format', fallback=default_settings['subtitle_format']),
                'include_keywords': config.get('prompt_settings', 'include_keywords', fallback=default_settings['include_keywords']),
                'keyword_count': config.get('prompt_settings', 'keyword_count', fallback=default_settings['keyword_count']),
                'custom_instruction': config.get('prompt_settings', 'custom_instruction', fallback=default_settings['custom_instruction'])
            }
    except:
        pass

    return default_settings


def build_prompt(seed: str, related_keywords: list[str], style: str):
    # 설정값 불러오기
    settings = load_prompt_config()

    # 키워드 처리
    if settings['include_keywords'].lower() == 'yes' and related_keywords:
        try:
            keyword_count = int(settings['keyword_count'])
        except ValueError:
            keyword_count = 5
        keyword_text = ", ".join(related_keywords[:keyword_count])
        keyword_instruction = f"글 안에는 '{keyword_text}' 같은 연관 개념도 자연스럽게 녹여줘. "
    else:
        keyword_instruction = ""

    # 프롬프트 구성
    prompt = (
        f"'{seed}'라는 주제로 {style} 스타일의 글을 작성해줘. "
        f"{keyword_instruction}"
        f"{settings['word_count']}자 분량으로 써줘. "
        f"{settings['custom_instruction']}"
    )
    return prompt


def run(seed: str, related_keywords: list[str], style: str = "마케팅 블로그"):
    if not style:
        style = "마케팅 블로그"
    prompt = build_prompt(seed, related_keywords, style)
    title = f"{seed}에 대한 {style} 글"
    content = generate_article(prompt)
    return [(title, content)]
