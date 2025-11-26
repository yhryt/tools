@echo off
rem 文字コードをUTF-8に変更（日本語ファイル名対策）
chcp 65001 >nul

rem ========================================================
rem  重要: 下のパスを実際のPythonファイルの場所に書き換えてください
rem  例: C:\tools\graph\interactive_graph.py
rem ========================================================
set PYTHON_SCRIPT="C:\tools\graph\graphpro\graphpro.py"

rem スクリプトが存在するか確認
if not exist %PYTHON_SCRIPT% (
    echo エラー: Pythonファイルが見つかりません。
    echo 設定されたパス: %PYTHON_SCRIPT%
    echo batファイルの中身を編集して正しいパスを指定してください。
    pause
    exit /b
)

rem Pythonを実行
python %PYTHON_SCRIPT% %*

rem 実行後に一時停止（エラー確認用）
pause