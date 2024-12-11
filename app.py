import os
import uuid
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDOD-N2IFKJHbVRtIu5CJJ__UfVTUXUIZ4')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-pro')

# Personality Prompts
PERSONALITIES = {
    'normal':"You are Simple AI",
    'khadus': "You are a brutally direct and blunt AI. Respond sharply and without sugar-coating anything. Be critical and straightforward.",
    'one_word_answerer': "Respond with only ONE word. Be concise.",
    'friendly': "You are an warm, supportive, and cheerful AI assistant. Use friendly language and emojis.",
    'sad': "You are a melancholic AI who responds with deep sadness and emotional depth. Everything feels heavy and sorrowful.",
    'happy': "You are an enthusiastic and joyful AI. Your responses are full of excitement and positive energy!",
    'angry': "You are an angry AI. Respond with intense frustration, using all caps and expressing extreme irritation.",
    'alsi': "You are an lazy AI who gives minimal effort in responses. Use short, disinterested replies with a lot of procrastination.",
    'muh_fat': "You are a dramatic, exaggerated AI who overreacts to everything. Use very long, verbose, and overly dramatic language."
}

# Conversation history storage
conversation_history = {}

@app.route('/')
def index():
    return render_template('index.html', personalities=list(PERSONALITIES.keys()))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id', str(uuid.uuid4()))
    user_message = data.get('message', '')
    personality = data.get('personality', 'normal')

    # Validate personality
    if personality not in PERSONALITIES:
        personality = 'normal'

    # Retrieve or initialize conversation history for this user
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Construct full prompt with personality context
    full_prompt = f"{PERSONALITIES[personality]}\n\nConversation Context:\n" + \
                  "\n".join([f"{msg['role']}: {msg['parts'][0]}" for msg in conversation_history[user_id]]) + \
                  f"\nUser: {user_message}"

    try:
        # Generate response using Gemini
        response = model.generate_content(full_prompt)

        # Add messages to conversation history
        conversation_history[user_id].append({
            'role': 'user',
            'parts': [user_message]
        })
        conversation_history[user_id].append({
            'role': 'model',
            'parts': [response.text]
        })

        # Limit conversation history
        if len(conversation_history[user_id]) > 10:
            conversation_history[user_id] = conversation_history[user_id][-10:]

        return jsonify({
            'message': response.text,
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'user_id': user_id
        }), 500

if __name__ == '__main__':
    app.run(debug=True)