@echo off
setlocal enabledelayedexpansion

:: 確認 ./cnf 資料夾存在
if not exist ".\cnf" (
    mkdir ".\cnf"
    echo Created directory: .\cnf
)

:: 遍歷 ./graph 資料夾中的所有 graph*.txt 檔
for %%F in (.\graph\graph*.txt) do (
    :: 提取檔名（不含路徑和副檔名），例如 graph1
    set "filename=%%~nF"
    :: 移除 "graph" 前綴，取得數字部分，例如 1
    set "id=!filename:graph=!"
    :: 執行指令：python reduce_hc.py ./graph/graph{id}.txt > ./cnf/hc{id}.cnf
    echo Processing graph!id!.txt...
    python reduce_hc.py ".\graph\graph!id!.txt" > ".\cnf\hc!id!.cnf"
    if errorlevel 1 (
        echo Error: Failed to process graph!id!.txt.
    ) else (
        echo Successfully generated hc!id!.cnf.
    )
)

echo All files processed.
pause