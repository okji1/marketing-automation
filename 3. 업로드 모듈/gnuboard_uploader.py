from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import time
import tkinter as tk
from tkinter import filedialog

# 폴더 및 설정

root = tk.Tk()

file_paths = filedialog.askopenfilenames(
    title="업로드할 텍스트 파일 선택",
    filetypes=[("Text Files", "*.txt")]
)

if not file_paths:
    print("❌ 선택된 파일이 없습니다. 종료합니다.")
    exit()

bo_table = "v6_06"
login_url = "http://220.95.52.164/sample03/bbs/login.php"
write_url = f"http://220.95.52.164/sample03/bbs/write.php?bo_table={bo_table}"
user_id = "hcom01"
user_pw = "dpstudy2401"

# 크롬 옵션
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

# 1. 로그인
print("🔐 로그인 중...")
driver.get(login_url)
driver.find_element(By.NAME, "mb_id").send_keys(user_id)
driver.find_element(By.NAME, "mb_password").send_keys(user_pw)
driver.find_element(By.NAME, "mb_password").send_keys(Keys.ENTER)
time.sleep(2)

# 2. 텍스트 파일 루프
for filepath in file_paths:
    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 2:
                print(f"⚠️ 본문 부족: {os.path.basename(filepath)}")
                continue
            title = lines[0].strip()
            content = "".join(lines[1:]).strip()

        # 글쓰기 페이지 이동
        driver.get(write_url)
        time.sleep(1)

        # 제목 및 본문 작성
        driver.find_element(By.NAME, "wr_subject").send_keys(title)
        driver.find_element(By.NAME, "wr_content").send_keys(content)

        # 작성 완료
        driver.find_element(By.ID, "btn_submit").click()
        print(f"✅ 업로드 완료: {os.path.basename(filepath)}")
        time.sleep(2)


print("🎉 전체 업로드 완료!")
driver.quit()
