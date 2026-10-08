#!/bin/bash
# =============================================================================
# STRIVE - One-Click Launcher for macOS
# Starts CV Service (FastAPI:8000), Spring Boot Backend (:8080), and Frontend (:3000)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home"
export PATH="$SCRIPT_DIR/tools/apache-maven-3.9.6/bin:$JAVA_HOME/bin:$PATH"
export MPLCONFIGDIR="/tmp/mpl"

echo "================================================================="
echo "   🏃‍♂️ STRIVE - Sports Talent Assessment Framework Launcher     "
echo "================================================================="
echo "  Java Home : $JAVA_HOME"
echo "  Maven Path: $SCRIPT_DIR/tools/apache-maven-3.9.6/bin/mvn"
echo "  Project   : $SCRIPT_DIR"
echo "================================================================="

# Trap Ctrl+C (SIGINT / SIGTERM) to cleanly terminate child processes
cleanup() {
    echo ""
    echo "🛑 Shutting down STRIVE services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start CV Service (FastAPI)
echo "🚀 [1/3] Starting Computer Vision Service on http://localhost:8000 ..."
cd "$SCRIPT_DIR/cv-service"
"$SCRIPT_DIR/cv-service/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
CV_PID=$!

# 2. Start Spring Boot Backend
echo "🚀 [2/3] Starting Spring Boot Backend on http://localhost:8080 ..."
cd "$SCRIPT_DIR/backend"
mvn spring-boot:run &
BACKEND_PID=$!

# 3. Start Frontend HTTP Server
echo "🚀 [3/3] Starting Mobile-First Frontend on http://localhost:3000 ..."
cd "$SCRIPT_DIR/frontend"
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "================================================================="
echo "✅ All STRIVE services are booting up!"
echo "================================================================="
echo "  📱 Web Application     : http://localhost:3000"
echo "  ⚙️  Backend Swagger UI  : http://localhost:8080/swagger-ui.html"
echo "  👁️  CV Service Docs     : http://localhost:8000/docs"
echo "================================================================="
echo "  Pre-seeded Demo Accounts:"
echo "    • Athlete : athlete@strive.org / Strive@2026"
echo "    • Coach   : coach@strive.org   / Strive@2026"
echo "    • Scout   : scout@strive.org   / Strive@2026"
echo "================================================================="
echo "Press Ctrl+C at any time to stop all services."
echo ""

# Wait for background processes
wait
