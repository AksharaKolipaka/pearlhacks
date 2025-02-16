from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import logging
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
from dotenv import load_dotenv
import os
from beginner_chat import beginner_bp
from intermediate_chat import intermediate_bp
from advanced_chat import advanced_bp

load_dotenv() 
api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define detailed prompts for each level
prompts = {
    "initial_consultation": "Welcome! I'm here to help you with your personal finances. Whether you're just starting to manage your money or looking to optimize your finances, I'm here to help. What would you like assistance with today?",
    
    "financial_goal_setting": "Let's talk about your financial goals. Are you saving for something specific like a home, education, or retirement? Or do you have other financial targets in mind? Share what you'd like to achieve.",
    
    "tax_optimization": "Would you like to understand more about taxes and potential tax-saving strategies? We can discuss basic tax concepts, deductions, or ways to be more tax-efficient with your money.",
    
    "retirement_planning": "Let's discuss your retirement planning. Whether you're just starting to think about retirement or already saving, we can explore how much you might need and different ways to save for your future.",
    
    "estate_planning": "Would you like to learn about estate planning basics? We can discuss wills, beneficiaries, and how to ensure your assets are protected and distributed according to your wishes.",
    
    "investment_recommendations": "Let's talk about investing. Whether you're new to investing or looking to expand your portfolio, we can discuss investment basics, risk tolerance, and different investment options.",
    
    "budgeting": "Need help creating or improving your budget? We can start by looking at your income and expenses, then work on creating a plan that helps you reach your financial goals.",
    
    "debt_management": "Looking to manage or reduce your debt? We can discuss different types of debt, strategies for paying it off, and creating a plan that works for your situation.",

    "investment_strategies": "Interested in investing? Let's explore strategies like mutual funds, ETFs, and building a diversified portfolio. What specific areas are you looking to learn about?",

    "retirement_planning": "Planning for retirement? We can discuss 401(k)s, IRAs, pension plans, and income strategies to help secure your future. What questions do you have?",

    "tax_planning": "Let's talk about tax-efficient investing and strategies to minimize your tax burden. Whether it's deductions, credits, or tax-advantaged accounts, how can I assist you?",

    "real_estate": "Thinking about real estate investing? We can cover mortgages, rental properties, and property management basics. What would you like to explore?",

    "insurance": "Insurance is key to financial security. Let's discuss life insurance, disability coverage, and ways to protect your future. What type of insurance are you interested in?",

    "education": "Saving for education? We can talk about 529 plans, student loan management, and other education funding strategies. What would you like to focus on?",

    "portfolio": "Want to dive deeper into portfolio management? Let's explore asset allocation, modern portfolio theory, and risk management strategies. What are you interested in?",

    "derivatives": "Curious about derivatives? We can discuss options, futures, and hedging strategies to help you navigate complex financial markets. What aspect intrigues you?",

    "estate": "Let's talk about estate planning—trusts, tax-efficient wealth transfer, and legacy planning. How can I help you structure your estate effectively?",

    "business": "Looking into business finance? We can explore valuation methods, capital structure, and M&A strategies to optimize financial decisions. What specific topics interest you?",

    "international": "Interested in global finance? Let's discuss international investing, forex markets, and cross-border tax strategies. What aspect would you like to explore?",

    "crypto": "Want to understand cryptocurrency better? We can explore blockchain technology, DeFi, and crypto investment strategies. What would you like to learn more about?"
}



# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    financial_level = db.Column(db.String(20), nullable=True, default=None)

# Conversation model
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario = db.Column(db.String(80), nullable=False)
    messages = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('conversations', lazy=True))

# Create the database tables within the application context
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

app.register_blueprint(beginner_bp)
app.register_blueprint(intermediate_bp)
app.register_blueprint(advanced_bp)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            # Check if user has taken the financial test
            if user.financial_level is None:
                return redirect(url_for('financial_test'))
            # Redirect to appropriate chat page based on financial level
            if user.financial_level == 'beginner':
                return redirect(url_for('chat_beginner'))
            elif user.financial_level == 'intermediate':
                return redirect(url_for('chat_intermediate'))
            else:  # advanced
                return redirect(url_for('chat_advanced'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            return "Username already taken. Please choose a different one."

        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        # Redirect new users to the financial test
        return redirect(url_for('financial_test'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    # Add error handling for when user is not found
    if user is None:
        session.pop('username', None)  # Clear invalid session
        return redirect(url_for('login'))
    
    # Now we can safely check the financial level
    if user.financial_level is None:
        return redirect(url_for('financial_test'))
    elif user.financial_level == 'beginner':
        return redirect(url_for('chat_beginner'))
    elif user.financial_level == 'intermediate':
        return redirect(url_for('chat_intermediate'))
    else:  # advanced
        return redirect(url_for('chat_advanced'))

def get_openai_response(user_input, scenario):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful financial assistant.'},
            {'role': 'user', 'content': prompts.get(scenario, "How can I assist you with your financial needs today?")},
            {'role': 'user', 'content': user_input}
        ]
    }
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return "An error occurred while processing your request. Please try again later."

@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'response': 'Please log in to use the chat feature.'}), 403

    user = User.query.filter_by(username=session['username']).first()
    
    # Add error handling for when user is not found
    if user is None:
        return jsonify({'response': 'User not found. Please log in again.'}), 403
    
    data = request.json
    topic = data.get('topic', 'initial_consultation')
    message = data.get('message', '')

    # Get the appropriate prompt from the prompts dictionary
    system_prompt = prompts.get(topic, "How can I help you with your financial questions?")

    # If this is the first message for this topic, return the system prompt
    if not message:
        return jsonify({'response': system_prompt})

    # Get response from OpenAI
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    openai_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': system_prompt},
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
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.'})

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))
    

@app.route('/financial-test')
def financial_test():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('financial_test.html')

CORRECT_ANSWERS = {
    'q1': 'a', 'q2': 'b', 'q3': 'c', 'q4': 'b', 'q5': 'b',
    'q6': 'b', 'q7': 'b', 'q8': 'c', 'q9': 'b', 'q10': 'a'
}

def determine_level(score):
    if score <= 5:
        return 'beginner'
    elif score > 5 or score <= 8:
        return 'intermediate'
    else:
        return 'advanced'

@app.route('/submit-test', methods=['POST'])
def submit_test():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    score = 0
    for question, correct_answer in CORRECT_ANSWERS.items():
        user_answer = request.form.get(question)
        if user_answer == correct_answer:
            score += 1
    
    level = determine_level(score)
    
    # Store the user's level in the database
    user = User.query.filter_by(username=session['username']).first()
    user.financial_level = level
    db.session.commit()
    
    # Redirect to the appropriate chat page based on level
    if level == 'beginner':
        return redirect(url_for('chat_beginner'))
    elif level == 'intermediate':
        return redirect(url_for('chat_intermediate'))
    else:
        return redirect(url_for('chat_advanced'))

@app.route('/chat-beginner')
def chat_beginner():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat_beginner.html', username=session['username'])

@app.route('/chat-intermediate')
def chat_intermediate():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat_intermediate.html', username=session['username'])

@app.route('/chat-advanced')
def chat_advanced():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat_advanced.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True, port=7000)
