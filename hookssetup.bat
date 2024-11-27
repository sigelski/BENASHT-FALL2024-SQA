@echo off
REM Check if hooks directory exists
if not exist "hooks" (
    echo Error: 'hooks' directory not found. Make sure the script is in the project root.
    exit /b 1
)

REM Check if pre-commit file exists in hooks directory
if not exist "hooks\pre-commit" (
    echo Error: 'hooks\pre-commit' file not found.
    exit /b 1
)

REM Check if .git/hooks directory exists
if not exist ".git\hooks" (
    echo Error: '.git\hooks' directory not found. Are you inside a Git repository?
    exit /b 1
)

REM Copy the pre-commit file to the .git/hooks directory
copy "hooks\pre-commit" ".git\hooks\pre-commit" >nul
if %errorlevel% neq 0 (
    echo Error: Failed to copy pre-commit hook.
    exit /b 1
)

REM Make the hook file executable (Windows Git does not need chmod)
echo Git hooks have been set up successfully!
exit /b 0
