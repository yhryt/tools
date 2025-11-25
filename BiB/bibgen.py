import datetime
import re
import json
import urllib.request
import urllib.error

# --- 設定 ---
DEFAULT_FILENAME = "references.bib"

def sanitize_key(author, year):
    """引用キーを生成する。日本語対応版"""
    if not author:
        author = "Unknown"
    
    # 著者の最初の単語を取得
    first_word = author.split()[0]
    
    # 英数字のみ抽出
    clean_author = re.sub(r'[^a-zA-Z0-9]', '', first_word)
    
    # 日本語などで空になった場合、元のテキストをローマ字風にするか、手動入力を促すのが理想だが
    # ここでは簡易的に "Author" + ランダム要素などを防ぐため、そのまま使用不可ならプレースホルダー
    if not clean_author:
        # 英数字が含まれない（日本語のみなど）場合は、安全策として一時的なキーを提案
        print(f"警告: 著者名 '{first_word}' から有効なキーが生成できません。")
        manual_key = input("  => 引用キーを手動で入力してください (例: Tanaka2025): ").strip()
        return manual_key if manual_key else f"Key_{datetime.datetime.now().strftime('%M%S')}"

    return f"{clean_author}{year}"

def get_input(prompt, required=True, default=None):
    """ユーザー入力を取得する（デフォルト値対応）"""
    prompt_text = f"{prompt}"
    if default:
        prompt_text += f" [Default: {default}]"
    
    while True:
        value = input(f"{prompt_text}: ").strip()
        if not value and default:
            return default
        if value or not required:
            return value
        print("エラー: この項目は必須です。")

# --- 自動化機能: DOIからBibTeXを取得 ---
def fetch_bibtex_by_doi():
    print("\n--- DOI 自動取得 ---")
    doi = get_input("DOIを入力 (例: 10.1038/nature...)")
    
    # DOIのURLクリーニング
    doi = doi.replace("https://doi.org/", "").strip()
    url = f"https://doi.org/{doi}"
    
    req = urllib.request.Request(url)
    # Content Negotiation: サーバーにBibTeX形式を要求するヘッダー
    req.add_header('Accept', 'application/x-bibtex')
    
    try:
        print("通信中... 情報を取得しています...")
        with urllib.request.urlopen(req) as response:
            bib_data = response.read().decode('utf-8')
            print("\n[取得成功]")
            # 整形して表示（オプション）
            print("-" * 40)
            print(bib_data.strip())
            print("-" * 40)
            return bib_data.strip()
    except urllib.error.HTTPError as e:
        print(f"取得失敗: DOIが見つからないか、サーバーが対応していません (Error: {e.code})")
        return None
    except Exception as e:
        print(f"エラー発生: {e}")
        return None

# --- 1. 雑誌論文 (@article) ---
def generate_journal_article():
    print("\n--- 雑誌論文 (@article) ---")
    # ここでDOI自動取得を提案
    choice = input("DOIから自動取得しますか？ (y/n) >> ").lower()
    if choice == 'y':
        result = fetch_bibtex_by_doi()
        if result: return result
        print("手動入力に切り替えます。")

    author = get_input("著者名 (Author)")
    title = get_input("論文タイトル (Title)")
    journal = get_input("雑誌名 (Journal)")
    year = get_input("発行年 (Year)")
    
    volume = get_input("巻 (Vol)", required=False)
    number = get_input("号 (No)", required=False)
    pages = get_input("ページ (Pages)", required=False)
    
    key = sanitize_key(author, year)
    
    lines = [
        f"@article{{{key},",
        f"  author    = {{{author}}},",
        f"  title     = {{{title}}},",
        f"  journal   = {{{journal}}},",
        f"  year      = {{{year}}},"
    ]
    if volume: lines.append(f"  volume    = {{{volume}}},")
    if number: lines.append(f"  number    = {{{number}}},")
    if pages: lines.append(f"  pages     = {{{pages}}},")
    lines.append("}")
    return "\n".join(lines)

# --- 2. 国際会議 (@inproceedings) ---
def generate_conference_paper():
    print("\n--- 国際会議/学会予稿 (@inproceedings) ---")
    author = get_input("著者名")
    title = get_input("発表タイトル")
    booktitle = get_input("会議名 (Proc. of ...)") 
    year = get_input("開催年")
    
    key = sanitize_key(author, year)
    
    lines = [
        f"@inproceedings{{{key},",
        f"  author    = {{{author}}},",
        f"  title     = {{{title}}},",
        f"  booktitle = {{{booktitle}}},",
        f"  year      = {{{year}}},"
    ]
    lines.append("}")
    return "\n".join(lines)

# --- 3. 学位論文 ---
def generate_thesis():
    print("\n--- 学位論文 ---")
    t_choice = get_input("種類 (p: PhD, m: Master)", default="p")
    bib_type = "phdthesis" if t_choice.lower().startswith('p') else "mastersthesis"
    
    author = get_input("著者名")
    title = get_input("論文タイトル")
    school = get_input("大学名")
    year = get_input("授与年")
    
    key = sanitize_key(author, year)
    
    return (
        f"@{bib_type}{{{key},\n"
        f"  author    = {{{author}}},\n"
        f"  title     = {{{title}}},\n"
        f"  school    = {{{school}}},\n"
        f"  year      = {{{year}}}\n"
        f"}}"
    )

# --- 4. Webサイト (@misc) ---
def generate_web_bibtex():
    print("\n--- Webサイト (@misc) ---")
    author = get_input("著者または組織名") 
    title = get_input("ページタイトル")
    url = get_input("URL")
    year = get_input("公開年", required=False)
    
    access_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # 年がない場合はアクセス年をキーに使う
    key_year = year if year else datetime.date.today().year
    key = sanitize_key(author, key_year)

    lines = [
        f"@misc{{{key},",
        f"  author       = {{{author}}},",
        f"  title        = {{{title}}},",
        f"  howpublished = {{\\url{{{url}}}}},"
    ]
    if year:
        lines.append(f"  year         = {{{year}}},")
        
    lines.append(f"  note         = {{Accessed: {access_date}}}")
    lines.append("}")
    return "\n".join(lines)

# --- 5. 書籍 (@book) ---
def generate_book_bibtex():
    print("\n--- 書籍 (@book) ---")
    # Google Books API等を使えば自動化可能だが、今回はシンプルに手動維持
    author = get_input("著者名")
    title = get_input("書名")
    publisher = get_input("出版社")
    year = get_input("発行年")
    
    key = sanitize_key(author, year)
    lines = [
        f"@book{{{key},",
        f"  author    = {{{author}}},",
        f"  title     = {{{title}}},",
        f"  publisher = {{{publisher}}},",
        f"  year      = {{{year}}},"
    ]
    lines.append("}")
    return "\n".join(lines)

def save_to_file(bib_list):
    filename = get_input("保存ファイル名", required=False, default=DEFAULT_FILENAME)
    if not filename.endswith(".bib"): filename += ".bib"
    
    try:
        # 追記モードで保存
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n" + "\n\n".join(bib_list) + "\n")
        print(f"\n[成功] {filename} に {len(bib_list)} 件の文献を追加しました。")
    except Exception as e:
        print(f"エラー: {e}")

def main():
    print("=== Smart BibTeX Generator ===")
    results = []
    
    while True:
        print("\n[メニュー]")
        print("1: 論文 (DOI自動取得あり)")
        print("2: 国際会議")
        print("3: 書籍")
        print("4: 学位論文")
        print("5: Webサイト")
        print("q: 終了して保存")
        
        choice = input("選択 >> ").lower()
        
        entry = None
        if choice == '1': entry = generate_journal_article()
        elif choice == '2': entry = generate_conference_paper()
        elif choice == '3': entry = generate_book_bibtex()
        elif choice == '4': entry = generate_thesis()
        elif choice == '5': entry = generate_web_bibtex()
        elif choice == 'q': break
        
        if entry:
            results.append(entry)
            print("-> リストに追加 (一時保存)")

    if results:
        save_to_file(results)
    else:
        print("何も保存せずに終了します。")

if __name__ == "__main__":
    main()