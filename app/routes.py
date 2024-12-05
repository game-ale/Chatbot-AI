from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from .models import ChatHistory
from . import db
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Set up the blueprint
views = Blueprint('views', __name__)

# Load environment variables
load_dotenv()

# This function will be run before each request
@views.before_request
def before_request():
    """Executes before every request."""
    print(current_user.is_authenticated)
    # Check if user is authenticated or perform other logic
    if "user_id" not in session and request.endpoint not in ['auth.login', 'auth.signup']:
        # Redirect user to login if they are not authenticated
        return redirect(url_for("auth.login"))

@views.route('/')
def homepage():
    return render_template('index.html')

@views.route("/chat", methods=["GET"])
@login_required
def chat_page():
    user_id = session["user_id"]
    chat_history = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.request_time.desc()).all()
    chat_history.reverse()
    return render_template("chat.html", history=chat_history)

@views.route('/chat', methods=['POST'])
@login_required
def chat():
    # Get the user's input from the frontend
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'No message provided!'}), 400

    # Send the message to the AI model
    response = chat_with_ai(message)

    # Save the chat to the database
    new_chat = ChatHistory(
        user_id=current_user.id,
        request=message,
        response=response
    )
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({'response': response})

def chat_with_ai(message):
    """Interacts with Google's Generative AI model."""
    try:
        api_key = os.getenv('API_KEY')
        genai.configure(api_key=api_key)  # Replace with your API key
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')  # Adjust model name if needed
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        print(f"Error communicating with AI: {e}")
        return "Sorry, there was an error processing your message."
