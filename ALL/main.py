import tkinter as tk
from tkinter import messagebox, Toplevel
import configparser
import threading
from modules import keyword_collector, content_writer

CONFIG_FILE = "config.ini"
PROMPT_CONFIG_FILE = "prompt_config.ini"

# AI 프롬프트 설정 창 함수


def open_prompt_config_window():
    # 기본 프롬프트 설정값
    default_config = {
        'prompt_settings': {
            'word_count': '300',
            'subtitle_format': '[소제목]',
            'include_keywords': 'yes',
            'keyword_count': '5',
            'custom_instruction': '소제목이 있고, 소제목은 [소제목] 형태로 써주고, 소제목을 쓸 때는 반드시 소제목 바로 위에 줄바꿈 2번(빈 줄 1줄)을 추가해줘. 단, 소제목과 그 소제목의 본문 사이에는 줄바꿈이 2번 오면 안 돼.'
        }
    }

    # prompt_config.ini 파일 읽기 (없으면 기본값 사용)
    prompt_config = configparser.ConfigParser()
    try:
        prompt_config.read(PROMPT_CONFIG_FILE, encoding='utf-8')
        if not prompt_config.sections():
            # 파일이 비어있으면 기본값 설정
            for section, options in default_config.items():
                prompt_config.add_section(section)
                for key, value in options.items():
                    prompt_config.set(section, key, value)
    except:
        # 파일이 없으면 기본값으로 설정
        for section, options in default_config.items():
            prompt_config.add_section(section)
            for key, value in options.items():
                prompt_config.set(section, key, value)

    win = Toplevel(root)
    win.title("AI 프롬프트 설정")
    win.geometry("600x500")

    entries = {}
    row = 0

    # 프롬프트 설정 섹션
    tk.Label(win, text="[AI 프롬프트 설정]", font=("bold", 12)).grid(
        row=row, column=0, sticky="w", pady=(10, 10), columnspan=2)
    row += 1

    # 글자 수 설정
    tk.Label(win, text="글자 수:").grid(
        row=row, column=0, sticky="e", padx=5, pady=3)
    word_count_entry = tk.Entry(win, width=20)
    word_count_entry.grid(row=row, column=1, padx=5, pady=3, sticky="w")
    word_count_entry.insert(0, prompt_config.get(
        'prompt_settings', 'word_count', fallback='300'))
    entries['word_count'] = word_count_entry
    row += 1

    # 소제목 형식
    tk.Label(win, text="소제목 형식:").grid(
        row=row, column=0, sticky="e", padx=5, pady=3)
    subtitle_entry = tk.Entry(win, width=20)
    subtitle_entry.grid(row=row, column=1, padx=5, pady=3, sticky="w")
    subtitle_entry.insert(0, prompt_config.get(
        'prompt_settings', 'subtitle_format', fallback='[소제목]'))
    entries['subtitle_format'] = subtitle_entry
    row += 1

    # 키워드 포함 여부
    tk.Label(win, text="연관 키워드 포함:").grid(
        row=row, column=0, sticky="e", padx=5, pady=3)
    include_keywords_var = tk.StringVar()
    include_keywords_var.set(prompt_config.get(
        'prompt_settings', 'include_keywords', fallback='yes'))
    tk.Radiobutton(win, text="예", variable=include_keywords_var,
                   value="yes").grid(row=row, column=1, sticky="w", padx=5)
    tk.Radiobutton(win, text="아니오", variable=include_keywords_var,
                   value="no").grid(row=row, column=1, sticky="w", padx=50)
    entries['include_keywords'] = include_keywords_var
    row += 1

    # 키워드 개수
    tk.Label(win, text="포함할 키워드 개수:").grid(
        row=row, column=0, sticky="e", padx=5, pady=3)
    keyword_count_entry = tk.Entry(win, width=20)
    keyword_count_entry.grid(row=row, column=1, padx=5, pady=3, sticky="w")
    keyword_count_entry.insert(0, prompt_config.get(
        'prompt_settings', 'keyword_count', fallback='5'))
    entries['keyword_count'] = keyword_count_entry
    row += 1

    # 사용자 정의 지시사항
    tk.Label(win, text="사용자 정의 지시사항:", font=("bold", 10)).grid(
        row=row, column=0, sticky="nw", padx=5, pady=(10, 3), columnspan=2)
    row += 1

    custom_text = tk.Text(win, width=70, height=15, wrap=tk.WORD)
    custom_text.grid(row=row, column=0, columnspan=2, padx=5, pady=3)
    custom_text.insert(tk.END, prompt_config.get('prompt_settings', 'custom_instruction',
                                                 fallback=default_config['prompt_settings']['custom_instruction']))
    entries['custom_instruction'] = custom_text
    row += 1

    def save_prompt_config():
        # prompt_settings 섹션이 없으면 생성
        if not prompt_config.has_section('prompt_settings'):
            prompt_config.add_section('prompt_settings')

        # 설정값 저장
        prompt_config.set('prompt_settings', 'word_count',
                          entries['word_count'].get())
        prompt_config.set('prompt_settings', 'subtitle_format',
                          entries['subtitle_format'].get())
        prompt_config.set('prompt_settings', 'include_keywords',
                          entries['include_keywords'].get())
        prompt_config.set('prompt_settings', 'keyword_count',
                          entries['keyword_count'].get())
        prompt_config.set('prompt_settings', 'custom_instruction',
                          entries['custom_instruction'].get("1.0", tk.END).strip())

        # 파일에 저장
        with open(PROMPT_CONFIG_FILE, "w", encoding="utf-8") as f:
            prompt_config.write(f)

        messagebox.showinfo("저장 완료", "AI 프롬프트 설정이 저장되었습니다.")
        win.destroy()

    # 저장 버튼
    tk.Button(win, text="저장", command=save_prompt_config, width=15).grid(
        row=row, column=0, columnspan=2, pady=20)

# 환경설정 창 함수


def open_config_window():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    win = Toplevel(root)
    win.title("환경설정 (config.ini)")

    entries = {}
    row = 0
    for section in config.sections():
        tk.Label(win, text=f"[{section}]", font=("bold", 11)).grid(
            row=row, column=0, sticky="w", pady=(10, 0))
        row += 1
        for key in config[section]:
            tk.Label(win, text=key).grid(row=row, column=0, sticky="e", padx=3)
            e = tk.Entry(win, width=40)
            e.grid(row=row, column=1, padx=3, pady=1)
            e.insert(0, config[section][key])
            entries[(section, key)] = e
            row += 1

    def save_config():
        for (section, key), entry in entries.items():
            value = entry.get()
            # 숫자값이 필요한 항목에 대해 비어있으면 기본값 '0'을 넣음
            if value.strip() == '':
                # 숫자값이 필요한 key 이름에 따라 분기 (예시: count, num, limit 등)
                if any(word in key.lower() for word in ['count', 'num', 'limit', 'max', 'min']):
                    value = '0'
            config[section][key] = value
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)
        messagebox.showinfo("저장 완료", "환경설정이 저장되었습니다.")
        win.destroy()

    tk.Button(win, text="저장", command=save_config).grid(
        row=row, column=1, pady=10)

# 플랫폼 선택 함수


def select_platform(platform_name):
    if platform_name == "그누보드":
        from gnuboard_uploader import gnuboard_uploader
        return gnuboard_uploader
    elif platform_name == "네이버":
        from naver_uploader import naver_uploader
        return naver_uploader
    elif platform_name == "티스토리":
        from tstory_uploader import tstory_uploader
        return tstory_uploader
    else:
        return None

# 실행 버튼 클릭 시 동작


def run_all():
    platform_name = platform_var.get()
    user_keyword = entry_seed_keyword.get().strip()
    user_style = entry_style.get().strip()
    if not platform_name:
        messagebox.showwarning("경고", "업로드할 플랫폼을 선택하세요!")
        return
    if not user_keyword:
        messagebox.showwarning("경고", "시드 키워드를 입력하세요!")
        return

    def task():
        log_text.insert(tk.END, f"[플랫폼 선택] {platform_name}\n")
        log_text.insert(tk.END, f"[입력 키워드] {user_keyword}\n")
        log_text.insert(tk.END, f"[글 스타일] {user_style}\n")
        try:
            platform = select_platform(platform_name)
            log_text.insert(tk.END, "키워드 수집 중...\n")
            seed, keywords = keyword_collector.run(user_keyword)
            log_text.insert(tk.END, f"키워드: {keywords}\n")
            log_text.insert(tk.END, "AI 글 작성 중...\n")
            articles = content_writer.run(seed, keywords, user_style)
            log_text.insert(tk.END, "업로드 중...\n")
            platform.run(articles)
            log_text.insert(tk.END, "[완료] 작업이 모두 끝났습니다.\n\n")
            log_text.see(tk.END)
        except Exception as e:
            log_text.insert(tk.END, f"[오류] {str(e)}\n")
            log_text.see(tk.END)

    # run_all을 바로 실행하지 않고 thread로!
    threading.Thread(target=task).start()


# 메인 UI 세팅
root = tk.Tk()
root.title("마케팅 자동화 프로그램")

frm = tk.Frame(root)
frm.pack(padx=15, pady=10)

tk.Label(frm, text="업로드 플랫폼 선택", font=("bold", 12)).grid(
    row=0, column=0, sticky="w", pady=(0, 8), columnspan=3)

platform_var = tk.StringVar()
tk.Radiobutton(frm, text="그누보드", variable=platform_var,
               value="그누보드").grid(row=1, column=0, sticky="w")
tk.Radiobutton(frm, text="네이버", variable=platform_var,
               value="네이버").grid(row=1, column=1, sticky="w")
tk.Radiobutton(frm, text="티스토리", variable=platform_var,
               value="티스토리").grid(row=1, column=2, sticky="w")

# 입력란 1: 시드 키워드
tk.Label(frm, text="시드 키워드 입력").grid(
    row=2, column=0, sticky="w", pady=(15, 3), columnspan=3)
entry_seed_keyword = tk.Entry(frm, width=50)
entry_seed_keyword.grid(row=3, column=0, columnspan=3, pady=(0, 6))

# 입력란 2: 글 스타일
tk.Label(frm, text="글 스타일 입력 (예: 마케팅 블로그 / 뉴스 / SNS)").grid(row=4,
                                                            column=0, sticky="w", pady=(8, 3), columnspan=3)
entry_style = tk.Entry(frm, width=50)
entry_style.insert(0, "마케팅 블로그")  # 기본값
entry_style.grid(row=5, column=0, columnspan=3, pady=(0, 12))

tk.Button(frm, text="실행", command=run_all, width=10).grid(
    row=6, column=0, pady=10, columnspan=3)
tk.Button(frm, text="환경설정(config.ini)", command=open_config_window,
          width=18).grid(row=7, column=0, columnspan=3, pady=(0, 5))
tk.Button(frm, text="AI 프롬프트", command=open_prompt_config_window,
          width=18).grid(row=8, column=0, columnspan=3, pady=(0, 12))

log_text = tk.Text(root, height=15, width=65)
log_text.pack(padx=12, pady=(0, 15))

root.mainloop()
