import configparser
import os
import time
import pyperclip
from . import naver_uploader_pic
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def load_naver_account(config_path="./config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config["naver"]["id"], config["naver"]["pw"]


def paste_input(driver, element, text):
    element.click()
    pyperclip.copy(text)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys(
        'v').key_up(Keys.CONTROL).perform()
    time.sleep(1)


def slow_typing(actions, text, delay=0.03):
    for char in text:
        actions.send_keys(char).perform()
        time.sleep(delay)


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


def str_to_bool(val: str) -> bool:
    return val.lower() in ['y', 'yes', 'true', '1']


def upload_to_naver_blog_with_content(title, raw_content, config_path="./config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    image_folder = config["image"]["img_folder"]
    max_images = int(config["image"]["img_count"])
    add_images = str_to_bool(config["image"]["add_images"])
    image_index = 1
    profile_dir = os.path.abspath("./naver_profile")
    options = Options()
    options.add_argument(f"user-data-dir={profile_dir}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    try:
        print("🔐 자동 로그인 시도 중...")
        user_id, user_pw = load_naver_account(config_path)
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)
        paste_input(driver, driver.find_element(By.ID, "id"), user_id)
        paste_input(driver, driver.find_element(By.ID, "pw"), user_pw)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

        current_url = driver.current_url
        if not current_url.startswith("https://www.naver.com"):
            print("📱 2차 인증이 필요합니다. 수동 인증 후 Enter를 눌러주세요.")
            input("➡ 인증 완료 후 Enter ▶️ ")
            time.sleep(5)
            if not driver.current_url.startswith("https://www.naver.com"):
                print("❌ 여전히 로그인 상태가 아님. 작업 종료")
                driver.quit()
                return
        else:
            print("✅ 2차 인증 없이 로그인 성공")

        driver.get("https://blog.naver.com")
        time.sleep(2)
        driver.find_element(
            By.CSS_SELECTOR, 'a[href="https://blog.naver.com/GoBlogWrite.naver"]').click()
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        driver.switch_to.frame(driver.find_element(
            By.CSS_SELECTOR, "#mainFrame"))
        time.sleep(2)

        try:
            driver.find_element(
                By.CSS_SELECTOR, ".se-popup-button-cancel").click()
            print("❎ 팝업 취소 클릭")
            time.sleep(1)
        except:
            pass

        try:
            driver.find_element(
                By.CSS_SELECTOR, ".se-help-panel-close-button").click()
            print("❎ 도움말 닫기")
            time.sleep(1)
        except:
            pass

        actions = ActionChains(driver)

        # ✏️ 제목 입력
        print("✏️ 제목 입력 중...")
        title_area = driver.find_element(
            By.CSS_SELECTOR, ".se-section-documentTitle")
        title_area.click()
        slow_typing(actions, title)

        print("📝 본문 입력 중...")
        body_area = driver.find_element(By.CSS_SELECTOR, ".se-section-text")
        body_area.click()
        time.sleep(1)

        content_blocks = split_by_double_newline(raw_content)

        for block in content_blocks:
            for line in block.split("\n"):
                slow_typing(actions, line)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(0.03)

            if add_images and image_index <= max_images:
                image_path = os.path.join(image_folder, f"{image_index}.jpg")
                print(f"🖼 이미지 삽입 중: {image_path}")
                naver_uploader_pic.upload_image(driver, image_path)
                image_index += 1

        print("📤 저장 버튼 클릭 중...")
        driver.find_element(By.CLASS_NAME, "save_btn__bzc5B").click()
        time.sleep(2)

        print(f"✅ 블로그 글 저장 완료: {title}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    finally:
        driver.quit()


def run(articles: list[tuple[str, str]], config_path="config.ini"):
    for title, content in articles:
        print(f"\n🚀 업로드 시도: {title}")
        upload_to_naver_blog_with_content(title, content, config_path)
