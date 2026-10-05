@echo off
echo ===================================================
echo     Scanalytical - Push to GitHub Repository
echo ===================================================
echo.

set /p REPO_URL="Enter your GitHub repository URL (e.g. https://github.com/username/scanalytical.git): "

if "%REPO_URL%"=="" (
    echo Error: No repository URL provided.
    pause
    exit /b 1
)

echo.
echo Adding remote origin...
"%~dp0mingit\cmd\git.exe" remote remove origin 2>nul
"%~dp0mingit\cmd\git.exe" remote add origin %REPO_URL%

echo Pushing main branch to GitHub...
"%~dp0mingit\cmd\git.exe" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo  SUCCESS! Code pushed to GitHub.
    echo.
    echo  To enable live hosting on GitHub Pages:
    echo   1. Go to your repo on GitHub: Settings -^> Pages
    echo   2. Under 'Build and deployment' Source: Deploy from a branch
    echo   3. Branch: main, Folder: /docs -^> Click Save!
    echo   4. Your dashboard will be live at:
    echo      https://^<your-username^>.github.io/^<repo-name^>/
    echo ===================================================
) else (
    echo.
    echo Push failed. Please check your repository URL and permissions.
)

echo.
pause
