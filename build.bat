@echo off
echo ==============================================
echo  Compilando Moupenix com PyInstaller...
echo ==============================================
python -m PyInstaller --onefile --noconsole --name "Moupenix" main.py
echo.
if exist "dist\Moupenix.exe" (
    echo ==============================================
    echo  Sucesso! Executavel gerado em:
    echo  dist\Moupenix.exe
    echo ==============================================
) else (
    echo Erro ao compilar. Verifique as mensagens acima.
)
pause

