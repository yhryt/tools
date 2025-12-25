@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo --------------------------------------------------
echo 卒論バックアップシステム (高速版：PDF作成なし)
echo --------------------------------------------------

REM ==================================================
REM ▼ 設定エリア
REM ==================================================

REM 1. 卒論フォルダ
set "THESIS_DIR=C:\Users\tauyu\Documents\卒論"

REM 2. Google Driveの保存先
set "DRIVE_ROOT=G:\マイドライブ\卒論"

REM ==================================================

REM --- 0. 卒論フォルダへ移動 ---
if not exist "%THESIS_DIR%" (
    echo [ERROR] 指定されたフォルダが見つかりません:
    echo %THESIS_DIR%
    pause
    exit /b
)
cd /d "%THESIS_DIR%"

REM --- 1. コミットメッセージ入力 ---
echo.
set /p COMMIT_MSG="コミットメッセージを入力してください: "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Auto backup

REM --- 2. 日付取得 ---
for /f "usebackq delims=" %%A in (`powershell -Command "Get-Date -Format 'yyyyMMdd_HHmm'"`) do set TIMESTAMP=%%A
set "TARGET_DIR=%DRIVE_ROOT%\Backup_%TIMESTAMP%"

REM --- 3. GitHubへプッシュ ---
echo.
echo [1/2] GitHubへアップロード中...
git add .
git commit -m "%COMMIT_MSG%"
git push origin main

REM --- 4. Google Driveへ保存 ---
echo.
echo [2/2] Google Driveへ保存中 (ソースのみ)...
mkdir "%TARGET_DIR%"

REM TeXファイルとBibファイルをコピー
xcopy /y /s *.tex "%TARGET_DIR%\"
xcopy /y /s *.bib "%TARGET_DIR%\"

REM 画像フォルダをコピー
if exist images (
    xcopy /y /s /i images "%TARGET_DIR%\images"
)

echo.
echo --------------------------------------------------
echo ✅ バックアップ完了！
echo --------------------------------------------------
pause