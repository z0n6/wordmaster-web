import os
import requests
import datetime

# 設定檔案路徑
BASE_DIR = os.path.dirname(__file__)
ANSWERS_PATH = os.path.join(BASE_DIR, '../data/answers.csv')
VOCAB_PATH = os.path.join(BASE_DIR, '../data/vocabularies.csv')

def get_todays_wordle():
    """從 NYT API 取得今天的 Wordle 答案"""
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WordMasterBot/1.0)"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("solution", "").upper()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def load_word_set(filepath):
    """讀取 CSV 資料到 Set 中 (通用)"""
    word_set = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # 兼容逗號或換行分隔
            raw_words = content.replace(',', '\n').splitlines()
            for w in raw_words:
                clean_w = w.strip().upper()
                if len(clean_w) == 5:
                    word_set.add(clean_w)
    return word_set

def append_word_to_file(filepath, word):
    """將新單字附加到檔案末尾 (通用)"""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            # 如果檔案有內容，確保先換行
            if os.path.getsize(filepath) > 0:
                f.write(f"\n{word}")
            else:
                f.write(word)
        return True
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")
        return False

def update_databases(new_word):
    """檢查並更新兩個資料庫"""
    if not new_word or len(new_word) != 5:
        print("Invalid word received.")
        return

    # 1. 處理 Answers
    answers_set = load_word_set(ANSWERS_PATH)
    if new_word in answers_set:
        print(f"Word '{new_word}' already in answers. (Skipping Answer update)")
    else:
        if append_word_to_file(ANSWERS_PATH, new_word):
            print(f"Added '{new_word}' to answers.csv")

    # 2. 處理 Vocabularies
    vocab_set = load_word_set(VOCAB_PATH)
    if new_word in vocab_set:
        print(f"Word '{new_word}' already in vocab. (Skipping Vocab update)")
    else:
        if append_word_to_file(VOCAB_PATH, new_word):
            print(f"Added '{new_word}' to vocabularies.csv")

if __name__ == "__main__":
    print("--- Daily Update Start ---")
    word = get_todays_wordle()
    if word:
        print(f"Today's word from API: {word}")
        update_databases(word)
    else:
        print("Failed to retrieve word.")
    print("--- Daily Update End ---")
