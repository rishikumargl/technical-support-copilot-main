@echo off
echo ========================================
echo Starting Qdrant Vector Database (Port 6333)
echo ========================================
echo Make sure Docker is running first!
echo.
docker run -p 6333:6333 qdrant/qdrant
pause
