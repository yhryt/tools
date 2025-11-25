@echo off
chcp 65001 > nul

:: .gitフォルダがない場所では実行させない安全装置
if not exist .git (
    echo [エラー] ここはGitリポジトリではありません。
    echo 'git init' をしたフォルダで実行してください。
    pause
    exit /b
)

echo === Universal Git Push ===
git status

echo.
echo ----------------------------------------
set /p commit_msg="コミットメッセージ (Enterで 'Update'): "
if "%commit_msg%"=="" set commit_msg=Update

:: add, commit, push
echo.
git add .
git commit -m "%commit_msg%"
git push

if %errorlevel% neq 0 (
    echo [失敗] エラーが発生しました。
    pause
) else (
    echo [成功] 完了しました！
)
:: 自動で画面を閉じるため pause は削除してもOK