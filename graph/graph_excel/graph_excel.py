import xlwings as xw
import random

def main():
    # 1. 呼び出し元のExcelブックを取得
    wb = xw.Book.caller()
    sheet = wb.sheets[0]

    # 2. セルに書き込む
    sheet.range("A1").value = "Pythonからの出力です！"
    
    # 3. ランダムな数値をリストで書き込む
    random_data = [random.randint(0, 100) for _ in range(10)]
    
    # A2から縦方向にデータを入れる (options(transpose=True)で行列入替)
    sheet.range("A2").options(transpose=True).value = random_data

if __name__ == "__main__":
    # デバッグ用：このファイルを直接実行したときは新しいExcelを開く
    xw.Book("my_tool.xlsm").set_mock_caller()
    main()