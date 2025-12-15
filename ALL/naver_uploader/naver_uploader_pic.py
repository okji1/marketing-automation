import time
from selenium.webdriver.common.by import By
import pyautogui


def upload_image(driver, image_path: str):
    main_window = driver.current_window_handle

    try:
        # 사진 버튼 클릭
        photo_button = driver.find_element(
            By.CLASS_NAME, "se-image-toolbar-button")
        photo_button.click()
        time.sleep(3)

        # 파일 경로 입력 및 엔터
        pyautogui.write(image_path)
        pyautogui.press('enter')
        time.sleep(3)

    except Exception as e:
        print(f"❌ 이미지 업로드 실패: {e}")
        try:
            driver.switch_to.window(main_window)
        except:
            pass
        return False
