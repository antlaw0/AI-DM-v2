@echo off
echo Launching DeepSeek Coder 6.7B Instruct...
title Terminal for lLama deepseek server
cd C:\Users\alawl\Desktop\Game Dev Projects\AI-DM-v2\AI-DM-v2
:: Run llama-server with proper settings for full output
llama-server.exe ^
  --model "C:\Users\alawl\llama.cpp\models\deepseek-coder-6.7b-instruct.Q4_K_M.gguf" ^
  --port 8080 ^
  --n-predict 6000 ^
  --ctx-size 16384 ^
  --ignore-eos ^
  --temp 0.7 ^
  --threads 32 ^
  --gpu-layers 100

pause
