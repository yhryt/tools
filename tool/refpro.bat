@echo off
echo Starting ResearchObsidian...

:: Navigate to the project directory explicitly
cd /d "c:\tools\ref"

if not exist node_modules (
    echo Installing dependencies...
    npm install
)

start "" "http://localhost:3000"
npm run dev
