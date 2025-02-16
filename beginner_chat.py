from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

beginner_bp = Blueprint('beginner', __name__)

BEGINNER_PROMPTS = {
    'budgeting': 'You are a helpful financial advisor focusing on basic budgeting concepts for beginners.',
    'savings': 'You are a helpful financial advisor focusing on basic savings strategies for beginners.',
    'debt': 'You are a helpful financial advisor focusing on basic debt management for beginners.',
    'credit': 'You are a helpful financial advisor focusing on credit basics for beginners.'
}

@beginner_bp.route('/chat-beginner')
def render_beginner_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat_beginner.html', username=session['username'])

@beginner_bp.route('/chat-beginner-api', methods=['POST'])
def chat_beginner():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 403

    if request.method == 'POST':
        data = request.json
        topic = data.get('topic')
        message = data.get('message')

        if topic not in BEGINNER_PROMPTS:
            return jsonify({'error': 'Invalid topic'}), 400

        try:
            # Get API key from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found")

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            openai_data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': BEGINNER_PROMPTS[topic]},
                    {'role': 'user', 'content': message}
                ]
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=openai_data
            )
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        except ValueError as e:
            print(f"Configuration Error: {str(e)}")
            return jsonify({'error': 'Server configuration error'}), 500
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': 'Failed to get response'}), 500

    return jsonify({'response': 'Connected to beginner chat'}) 