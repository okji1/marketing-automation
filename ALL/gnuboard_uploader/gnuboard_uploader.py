import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
from . import gnuboard_uploader_pic
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def str_to_bool(val: str) -> bool:
    return val.lower() in ['y', 'yes', 'true', '1']


def remove_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)


def split_by_double_newline(text):
    """두 줄 이상의 줄바꿈을 기준으로 문단 분리"""
    parts = []
    buffer = []
    newline_count = 0
    for line in text.splitlines():
        if line.strip() == "":
            newline_count += 1
        else:
            newline_count = 0
        buffer.append(line)
        if newline_count >= 2:
            parts.append("\n".join(buffer).strip())
            buffer = []
    if buffer:
        parts.append("\n".join(buffer).strip())
    return [p for p in parts if p]


def insert_text_to_editor(driver, html_block):
    # SmartEditor2 공식 JS API 활용! (그누보드에서 지원)
    driver.execute_script("""
        if (typeof oEditors !== 'undefined' && oEditors.getById) {
            oEditors.getById['wr_content'].exec('PASTE_HTML', [arguments[0]]);
        }
    """, html_block)
    time.sleep(1)


def upload_to_gnuboard(
    title, raw_content,
    config_path="./config.ini"
):
    # === config.ini에서 값 읽기 ===
    config = configparser.ConfigParser()
    config.read(config_path)
    url_base = config["gnuboard"]["url"]
    user_id = config["gnuboard"]["id"]
    user_pw = config["gnuboard"]["pw"]
    image_folder = config["image"]["img_folder"]
    max_images = int(config["image"]["img_count"])
    add_images = str_to_bool(config["image"]["add_images"])

    title = remove_non_bmp(title)
    raw_content = remove_non_bmp(raw_content)

    login_url = f"{url_base}/bbs/login.php"
    # bo_table 필요시 config에서 관리
    write_url = f"{url_base}/bbs/write.php?bo_table=v6_06"

    options = Options()
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("🔐 로그인 중...")
        driver.get(login_url)
        driver.find_element(By.NAME, "mb_id").send_keys(user_id)
        driver.find_element(By.NAME, "mb_password").send_keys(user_pw)
        driver.find_element(By.NAME, "mb_password").send_keys(Keys.ENTER)
        time.sleep(2)

        print("📝 글쓰기 페이지 이동...")
        driver.get(write_url)
        time.sleep(3)

        print("✏️ 제목 입력 중...")
        driver.find_element(By.NAME, "wr_subject").send_keys(title)
        time.sleep(1)

        image_index = 1

        print("🖊 SmartEditor2 본문 입력 중(문단/줄 단위 붙여넣기)...")
        content_blocks = split_by_double_newline(raw_content)
        for i, block in enumerate(content_blocks):
            # 줄 단위 줄바꿈도 그대로 반영!
            html_block = "<p>" + block.replace("\n", "<br>") + "</p>"
            insert_text_to_editor(driver, html_block)
            # 이미지 자동삽입 (옵션 적용)
            if add_images and image_index <= max_images:
                image_path = os.path.join(image_folder, f"{image_index}.jpg")
                gnuboard_uploader_pic.upload_image(driver, image_path)
                image_index += 1

        print("📤 제출 버튼 클릭 중...")
        driver.find_element(By.ID, "btn_submit").click()
        print(f"✅ 업로드 완료: {title}")
        time.sleep(2)
        driver.quit()
        return True

    except Exception as e:
        print(f"❌ 업로드 실패: {e}")
        driver.quit()
        return False


def run(articles: list[tuple[str, str]], config_path="./config.ini"):
    for title, content in articles:
        print(f"🚀 업로드 시도: {title}")
        upload_to_gnuboard(title, content, config_path=config_path)
