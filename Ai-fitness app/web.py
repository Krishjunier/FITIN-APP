from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import threading
import time

app = FastAPI()

# Mount "fitness" folder to serve HTML files
app.mount("/fitness", StaticFiles(directory="fitness"), name="fitness")

# Hardcoded credentials (for testing)
USERNAME = "admin"
PASSWORD = "admin"

# Temporary user storage for signups
users = {}

# Function to start Streamlit using "python -m streamlit run main.py"
def start_streamlit():
    time.sleep(1)  # Small delay to ensure stability
    subprocess.Popen(["python", "-m", "streamlit", "run", "main.py"], shell=True)

# Serve login page as the default page
@app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/fitness/login.html")

# Serve signup page (GET request)
@app.get("/signup", response_class=RedirectResponse)
def signup_page():
    return RedirectResponse(url="/fitness/signup.html")

# Handle signup form submission (POST request)
@app.post("/signup")
def signup(
    fullname: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")

    users[username] = password  # Store user in memory
    return RedirectResponse(url="/fitness/login.html", status_code=303)

# Serve forgot password page
@app.get("/forget-password", response_class=RedirectResponse)
def forget_password():
    return RedirectResponse(url="/fitness/forget-password.html")

# Handle login authentication
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        threading.Thread(target=start_streamlit, daemon=True).start()  # Start Streamlit in background
        return RedirectResponse(url="http://localhost:8501", status_code=303)  # Redirect to Streamlit app
    else:
        return HTMLResponse(content="""
        <script>
            alert("Wrong username or password! Please try again.");
            window.location.href = "/fitness/login.html";  // Redirect after clicking OK
        </script>
        """, status_code=401)
    
