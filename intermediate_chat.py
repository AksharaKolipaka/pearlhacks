from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

intermediate_bp = Blueprint('intermediate', __name__)

INTERMEDIATE_PROMPTS = {
    'investing': 'You are a helpful financial advisor focusing on intermediate investment strategies.',
    'retirement': 'You are a helpful financial advisor focusing on retirement planning.',
    'tax': 'You are a helpful financial advisor focusing on tax planning strategies.',
    'insurance': 'You are a helpful financial advisor focusing on insurance planning.',
    'realestate': 'You are a helpful financial advisor focusing on real estate basics.'
}

@intermediate_bp.route('/chat-intermediate')
def render_intermediate_chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat_intermediate.html', username=session['username'])

@intermediate_bp.route('/chat-intermediate-api', methods=['POST'])
def chat_intermediate():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 403

    if request.method == 'POST':
        data = request.json
        topic = data.get('topic')
        message = data.get('message')

        if topic not in INTERMEDIATE_PROMPTS:
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
                {'role': 'system', 'content': INTERMEDIATE_PROMPTS[topic]},
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

    return jsonify({'response': 'Connected to intermediate chat'}) 