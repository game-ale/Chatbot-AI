from app import create_app, db
from app.models import User, ChatHistory

def check_chat_history():
    # Query all users
    users = User.query.all()
    if not users:
        print("No users found in the database.")
        return

    for user in users:
        print(f"\nUser: {user.name} (Email: {user.email})")
        print("-" * 50)

        # Fetch chat history for the user
        chat_history = ChatHistory.query.filter_by(user_id=user.id).all()
        if chat_history:
            for chat in chat_history:
                print(f"Request: {chat.request}")
                print(f"Response: {chat.response}")
                print(f"Requested at: {chat.request_time}")
                print(f"Responded at: {chat.response_time}")
                print("-" * 50)
        else:
            print("No chat history for this user.")

if __name__ == "__main__":
    # Create the Flask app
    app = create_app()

    # Use the app context
    with app.app_context():
        check_chat_history()
