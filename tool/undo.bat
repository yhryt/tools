@echo off
chcp 65001 > nul

if "%1"=="" (
    echo [エラー] 元に戻したいファイル名を指定してください。
    exit /b
)

:: .bak ファイルが存在するか確認
if not exist "%1.bak" (
    echo [エラー] バックアップファイル "%1.bak" が見つかりません。
    exit /b
)

:: 復元処理 (バックアップを正とする)
copy /y "%1.bak" "%1" > nul

echo [復元] "%1" をバックアップ時点の内容に戻しました。