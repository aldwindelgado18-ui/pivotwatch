# Save this as .gitignore in your root directory
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
*.egg-info/
dist/
build/

# Database
*.db
*.sqlite3

# Environment variables
.env
.env.local
.env.*.local

# Screenshots and uploads
/backend/screenshots/
/backend/uploads/

# Frontend
/frontend/node_modules/
/frontend/build/
/frontend/.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF