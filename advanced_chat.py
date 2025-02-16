from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

advanced_bp = Blueprint('advanced', __name__)

ADVANCED_PROMPTS = {
    'portfolio': 'You are a helpful financial advisor focusing on advanced portfolio management.',
    'derivatives': 'You are a helpful financial advisor focusing on derivatives and options trading.',
    'estate': 'You are a helpful financial advisor focusing on advanced estate planning.',
    'business': 'You are a helpful financial advisor focusing on business finance.',
    'international': 'You are a helpful financial advisor focusing on international investing.',
    'crypto': 'You are a helpful financial advisor focusing on cryptocurrency and DeFi.'
}

@advanced_bp.route('/chat-advanced')
def render_advanced_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat_advanced.html', username=session['username'])

@advanced_bp.route('/chat-advanced-api', methods=['POST'])
def chat_advanced():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 403

    if request.method == 'POST':
        data = request.json
        topic = data.get('topic')
        message = data.get('message')

        if topic not in ADVANCED_PROMPTS:
            return jsonify({'error': 'Invalid topic'}), 400

        # Get OpenAI response
        api_key = os.getenv('OPENAI_API_KEY')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        openai_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': ADVANCED_PROMPTS[topic]},
                {'role': 'user', 'content': message}
            ]
        }

        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=openai_data
            )
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': 'Failed to get response'}), 500

    return jsonify({'response': 'Connected to advanced chat'}) 