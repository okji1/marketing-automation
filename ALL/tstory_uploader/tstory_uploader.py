import configparser
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from . import uploader_pic
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def str_to_bool(val: str) -> bool:
    return val.lower() in ['y', 'yes', 'true', '1']


def read_config(config_path="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    user_id = config["tstory"]["id"]
    user_pw = config["tstory"]["pw"]
    blog_name = config["tstory"]["blog_name"]
    image_folder = config["image"]["img_folder"]
    max_images = int(config["image"]["img_count"])
    add_images = str_to_bool(config["image"]["add_images"])
    return user_id, user_pw, blog_name, image_folder, max_images, add_images


def login_to_tstory(driver, user_id, user_pw):
    login_url = (
        "https://accounts.kakao.com/login/?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fclient_id%3D3e6ddd834b023f24221217e370daed18%26state%3DaHR0cHM6Ly93d3cudGlzdG9yeS5jb20v%26redirect_uri%3Dhttps%253A%252F%252Fwww.tistory.com%252Fauth%252Fkakao%252Fredirect%26response_type%3Dcode%26auth_tran_id%3DShQ.HRet9P478tXEYqU33Mj7jt3tYTTMQnmcuw5t8GApx6gJmNyqgD8pw3nw%26ka%3Dsdk%252F2.7.3%2520os%252Fjavascript%2520sdk_type%252Fjavascript%2520lang%252Fko-KR%2520device%252FWin32%2520origin%252Fhttps%25253A%25252F%25252Fwww.tistory.com%26is_popup%3Dfalse%26through_account%3Dtrue&talk_login=hidden#login"
    )
    driver.get(login_url)
    time.sleep(3)
    try:
        profile_btn = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.wrap_profile[role='button']"))
        )
        print("👤 저장된 계정 선택 버튼 발견, 클릭 시도...")
        profile_btn.click()
        time.sleep(2)
    except:
        print("ℹ️ 저장된 계정 버튼 없음, 일반 로그인 시도")

    if "login" in driver.current_url:
        print("👤 로그인 화면 진입, ID/PW 입력 중...")
        driver.find_element(By.ID, "loginId--1").send_keys(user_id)
        driver.find_element(By.ID, "password--2").send_keys(user_pw)
        try:
            driver.find_element(By.CLASS_NAME, "ico_check").click()
            print("🔒 간편로그인 저장 체크 완료")
        except:
            print("⚠️ 간편로그인 체크 실패")
        driver.find_element(By.CLASS_NAME, "submit").click()
        time.sleep(5)

    if not driver.current_url.startswith("https://www.tistory.com"):
        print("📱 2차 인증 또는 수동 인증이 필요합니다. 완료 후 Enter를 눌러주세요.")
        input("➡ 인증 완료 후 Enter ▶️ ")
        time.sleep(5)
        if not driver.current_url.startswith("https://www.tistory.com"):
            print("❌ 로그인 실패 또는 인증 미완료 상태입니다.")
            return False
    else:
        print("✅ 로그인 성공 또는 세션 유지")

    return True


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


def upload_to_tistory(title, content, user_id, user_pw, blog_id, image_folder, max_images, add_images):
    profile_dir = os.path.abspath("./tstory_profile")
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument(f"user-data-dir={profile_dir}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("🔐 티스토리 로그인 시작")
        if not login_to_tstory(driver, user_id, user_pw):
            driver.quit()
            return False

        driver.get(f"https://{blog_id}.tistory.com/manage/newpost")
        time.sleep(4)

        # 임시 저장글 alert 처리
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"⚠️ Alert Text: {alert.text}")
            alert.dismiss()
            print("🛑 임시 저장글 무시 완료")
            time.sleep(2)
        except:
            print("✅ Alert 없음")
        try:
            alert = driver.switch_to.alert
            print(f"⚠️ Alert Text: {alert.text}")
            alert.dismiss()
            print("🛑 임시 저장글 알림 무시함 (dismiss)")
            time.sleep(2)
        except NoAlertPresentException:
            print("✅ Alert 없음, 정상 진입")

        image_index = 1

        # 제목 입력
        driver.find_element(By.ID, "post-title-inp").send_keys(title)
        print("📝 제목 입력 완료")

        # 에디터 iframe 진입
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.ID, "editor-tistory_ifr"))
        )
        body = driver.find_element(By.ID, "tinymce")
        body.click()

        # 본문 입력(문단/줄 단위 + 이미지 삽입)
        content_blocks = split_by_double_newline(content)
        for i, block in enumerate(content_blocks):
            for line in block.split("\n"):
                body.send_keys(line)
                # 줄바꿈(shift+enter)로 한 줄 내림
                body.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(0.05)
            body.send_keys(Keys.ENTER)  # 문단 끝나면 빈 줄
            time.sleep(0.2)

            # 이미지 삽입 로직
            if add_images and image_index <= max_images:
                driver.switch_to.default_content()
                # 이미지 업로드 아이콘 클릭(아이콘 구조 바뀔 수 있음, 셀렉터 필요 시 조정)
                driver.find_element(By.ID, "mceu_0-open").click()
                driver.find_element(By.ID, "attach-image").click()
                upload_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[type='file']"))
                )
                image_path = os.path.join(image_folder, f"{image_index}.jpg")
                upload_input.send_keys(image_path)
                print(f"🖼 이미지 업로드: {image_path}")
                image_index += 1
                time.sleep(3)
                # 다시 에디터 iframe 진입
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.ID, "editor-tistory_ifr"))
                )
                body = driver.find_element(By.ID, "tinymce")
                body.send_keys(Keys.ENTER)
                body.send_keys(Keys.ENTER)

        driver.switch_to.default_content()
        print("✅ 본문 + 이미지 입력 완료")

        # 임시저장 클릭
        driver.find_element(By.LINK_TEXT, "임시저장").click()
        print(f"✅ 티스토리에 임시 저장 완료: {title}")
        time.sleep(2)
        driver.quit()
        return True

    except Exception as e:
        print(f"❌ 티스토리 업로드 실패: {e}")
        driver.quit()
        return False


def run(articles: list[tuple[str, str]], config_path="config.ini"):
    user_id, user_pw, blog_name, image_folder, max_images, add_images = read_config(
        config_path)
    for title, content in articles:
        print(f"🚀 티스토리 업로드 시도: {title}")
        upload_to_tistory(title, content, user_id, user_pw,
                          blog_name, image_folder, max_images, add_images)
