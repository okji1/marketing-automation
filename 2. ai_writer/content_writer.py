from modules.gemini_writer import generate_article

if __name__ == "__main__":
    keyword = input("✏️ 키워드를 입력하세요: ").strip()
    style = input("🎨 어떤 스타일로 작성할까요? (예: 마케팅 블로그 / 뉴스 / SNS 등): ").strip()
    try:
        length = int(input("✍️ 글자 수는 몇 자로 할까요? (예: 300): ").strip())
    except ValueError:
        print("❌ 숫자로 입력되지 않아 기본값 300으로 설정합니다.")
        length = 300

    # 👉 prompt 구성
    prompt = f"{keyword}에 대해 {style} 스타일로 {length}자 분량의 글을 작성해줘."

    # 👉 prompt를 1개 인자로 전달
    article = generate_article(prompt)

    print("\n📝 생성된 글:\n")
    print(article)
