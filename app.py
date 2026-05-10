from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from ai_engine import get_response
from database import save_chat, get_chats, save_user_google, save_user_email, get_user_by_email, get_user_by_id, check_password, create_thread, get_threads, get_thread, save_user_data, get_user_data
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Google OAuth setup
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

class User(UserMixin):
    def __init__(self, id, google_id, name, email):
        self.id = id
        self.google_id = google_id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
        user_data = get_user_by_id(user_id)
        if user_data:
            return User(user_data[0], None, user_data[1], user_data[2])
    except:
        pass
    return None

@app.route("/")
@login_required
def home():
    threads = get_threads(current_user.id)
    if not threads:
        # Create default thread
        thread_id = create_thread(current_user.id, "Welcome to Justin AI")
        # Add welcome message
        welcome_msg = "Hello! I'm Justin AI. How can I help you today?"
        save_chat(thread_id, "", welcome_msg)  # Empty user_msg for system
        threads = get_threads(current_user.id)
    current_thread_id = session.get('current_thread_id', threads[0][0] if threads else None)
    if current_thread_id:
        chats = get_chats(current_thread_id)
        current_thread = get_thread(current_thread_id)
    else:
        chats = []
        current_thread = None
    return render_template("index.html", threads=threads, chats=chats, current_thread=current_thread)

@app.route("/new_thread", methods=["POST"])
@login_required
def new_thread():
    title = request.form.get("title", "New Chat")
    thread_id = create_thread(current_user.id, title)
    session['current_thread_id'] = thread_id
    return redirect(url_for("home"))

@app.route("/select_thread/<int:thread_id>")
@login_required
def select_thread(thread_id):
    # Verify ownership
    thread = get_thread(thread_id)
    if thread:
        session['current_thread_id'] = thread_id
    return redirect(url_for("home"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        google_id = user_info["id"]
        name = user_info["name"]
        email = user_info["email"]
        user_id = save_user_google(google_id, name, email)
        user = User(user_id, google_id, name, email)
        login_user(user)
        return redirect(url_for("home"))
    return "Failed to login"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]
        if password != confirm:
            flash("Passwords do not match")
            return redirect(url_for("register"))
        # Check if email already exists
        user_data = get_user_by_email(email)
        if user_data:
            flash("Email already registered. Please log in instead.")
            return redirect(url_for("login"))
        # Create new user
        try:
            user_id = save_user_email(name, email, password)
            user = User(user_id, None, name, email)
            login_user(user)
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login_email", methods=["POST"])
def login_email():
    email = request.form["email"]
    password = request.form["password"]
    user_data = get_user_by_email(email)
    if not user_data:
        flash("Email not found. Please sign up first.")
        return redirect(url_for("login"))
    user_id, name, user_email, password_hash = user_data
    if not password_hash:
        flash("This account uses Google Sign-In. Please use Google to log in.")
        return redirect(url_for("login"))
    if check_password(user_id, password):
        user = User(user_id, None, name, user_email)
        login_user(user)
        return redirect(url_for("home"))
    flash("Invalid password")
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    try:
        user_msg = request.form.get("message", "").strip()
        if not user_msg:
            flash("Please enter a message")
            return redirect(url_for("home"))
        
        thread_id = session.get('current_thread_id')
        if not thread_id:
            # Fallback, but should not happen
            threads = get_threads(current_user.id)
            thread_id = threads[0][0] if threads else create_thread(current_user.id)
            session['current_thread_id'] = thread_id
        
        response = get_response(user_msg, thread_id)
        ai_reply = response.get("text") if isinstance(response, dict) else response
        media_type = response.get("media_type") if isinstance(response, dict) else None
        media_url = response.get("media_url") if isinstance(response, dict) else None
        
        save_chat(thread_id, user_msg, ai_reply, media_type, media_url)
        return redirect(url_for("home"))
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)