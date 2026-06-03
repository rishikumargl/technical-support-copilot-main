@echo off
echo ========================================
echo Starting RAG Module
echo ========================================
cd rag
call venv\Scripts\activate.bat
python ask_questions.py
pause
