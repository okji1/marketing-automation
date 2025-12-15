import time
from selenium.webdriver.common.by import By
import pyautogui


def upload_image(driver, image_path: str):
    main_window = driver.current_window_handle

    try:
        # 1. SmartEditor2 iframe 진입
        iframe = driver.find_element(
            By.CSS_SELECTOR, "iframe[src*='SmartEditor2Skin.html']")
        driver.switch_to.frame(iframe)

        # 2. 사진 버튼 클릭
        photo_button = driver.find_element(By.CLASS_NAME, "se2_photo")
        photo_button.click()
        time.sleep(2)

        # 3. 팝업 창으로 전환
        driver.switch_to.default_content()
        time.sleep(1)
        all_windows = driver.window_handles
        for win in all_windows:
            if win != main_window:
                driver.switch_to.window(win)
                break

        # 4. 파일선택 버튼 클릭
        file_select_button = driver.find_element(
            By.CSS_SELECTOR, "span.btn-success.fileinput-button")
        file_select_button.click()
        time.sleep(2)

        # 5. 파일 경로 입력 및 엔터
        pyautogui.write(image_path)
        pyautogui.press('enter')
        time.sleep(2)

        # 6. 등록 버튼 클릭
        upload_btn = driver.find_element(By.ID, "img_upload_submit")
        upload_btn.click()
        print("✅ 이미지 등록 버튼 클릭 완료")

        # 원래 창으로 복귀
        driver.switch_to.window(main_window)

    except Exception as e:
        print(f"❌ 이미지 업로드 실패: {e}")
        try:
            driver.switch_to.window(main_window)
        except:
            pass
        return False
