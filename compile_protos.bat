@echo off
setlocal enabledelayedexpansion

:: --- CONFIGURATION (ABSOLUTE PATHS) ---
:: %~dp0 is the directory where this script is located (ends with a backslash)
set "BASE_DIR=%~dp0"
set "SOURCE_DIR=%BASE_DIR%protos"
set "OUTPUT_DIR=%BASE_DIR%generated_protos"

echo ==========================================
echo      SQCR PROTOBUF COMPILER (V3)
echo ==========================================
echo Source: %SOURCE_DIR%
echo Output: %OUTPUT_DIR%
echo.

:: 1. Check for tools
python -c "import grpc_tools.protoc" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] grpcio-tools not found. Installing...
    pip install grpcio-tools
)

:: 2. Clean / Create Output Directory
if not exist "%OUTPUT_DIR%" (
    echo [+] Creating output directory...
    mkdir "%OUTPUT_DIR%"
)

:: 3. Recursive Compilation
echo [+] Compiling .proto files...

:: Loop through all .proto files recursively
for /R "%SOURCE_DIR%" %%f in (*.proto) do (
    
    :: Run protoc with absolute paths
    :: -I points to the root 'protos' folder so imports work correctly
    :: %%f is the absolute path to the file
    
    python -m grpc_tools.protoc -I"%SOURCE_DIR%" --python_out="%OUTPUT_DIR%" "%%f"
    
    if !errorlevel! neq 0 (
        echo [X] ERROR compiling %%~nxf
        echo     Command tried: python -m grpc_tools.protoc -I"%SOURCE_DIR%" --python_out="%OUTPUT_DIR%" "%%f"
        pause
        exit /b 1
    ) else (
        echo     OK: %%~nxf
    )
)

:: 4. Generate __init__.py files (CRITICAL for Python imports)
echo.
echo [+] Generating __init__.py for packages...

:: Create __init__.py in the root of generated_protos
if not exist "%OUTPUT_DIR%\__init__.py" type nul > "%OUTPUT_DIR%\__init__.py"

:: Recursively find all subdirectories in output and add __init__.py
for /D /R "%OUTPUT_DIR%" %%d in (*) do (
    if not exist "%%d\__init__.py" (
        type nul > "%%d\__init__.py"
        echo     Package initialized: %%~nxd
    )
)

echo.
echo ==========================================
echo [V] DONE! You can now run the server.
echo ==========================================
pause