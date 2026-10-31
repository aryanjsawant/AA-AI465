@echo off
rem Starts the local model server used by every script in this project.
rem 5 slots = one ESC window of 5 samples in parallel; 4 CPU threads.
bin\llama-server.exe -m models\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 8192 -np 5 -t 4 --host 127.0.0.1 --port 8088
