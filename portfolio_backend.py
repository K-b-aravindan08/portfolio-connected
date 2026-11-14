"""
DevFlow Portfolio Backend
API for portfolio projects, skills, and contact forms
Run: python portfolio_backend.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'portfolio.db'

def init_db():
    """Initialize database for portfolio"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Projects Table
        cursor.execute('''
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                link TEXT
            )
        ''')
        
        # Skills Table
        cursor.execute('''
            CREATE TABLE skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level INTEGER
            )
        ''')
        
        # Messages Table
        cursor.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample projects
        projects = [
            ('🎨 Design System', 'A comprehensive design system with reusable components, animations, and theming capabilities.', 'CSS,Animation,UI/UX', 'https://github.com'),
            ('⚡ Web App', 'Full-stack web application with real-time data updates and interactive user dashboard.', 'React,Node.js,MongoDB', 'https://github.com'),
            ('🤖 AI Chatbot', 'Intelligent chatbot powered by machine learning for customer support automation.', 'Python,ML,API', 'https://github.com'),
            ('📱 Mobile App', 'Responsive mobile-first application with offline capabilities and native feel.', 'React Native,Firebase,PWA', 'https://github.com'),
            ('📊 Analytics Dashboard', 'Data visualization dashboard with real-time charts and business intelligence tools.', 'D3.js,Charts,Analytics', 'https://github.com'),
            ('🔐 Auth System', 'Secure authentication and authorization system with JWT and OAuth support.', 'Security,JWT,Backend', 'https://github.com'),
        ]
        
        for title, desc, tags, link in projects:
            cursor.execute('''
                INSERT INTO projects (title, description, tags, link)
                VALUES (?, ?, ?, ?)
            ''', (title, desc, tags, link))
        
        # Insert sample skills
        skills = [
            ('Frontend Development', 90),
            ('Backend Development', 85),
            ('UI/UX Design', 80),
            ('Database Design', 75),
            ('AI/Machine Learning', 70),
        ]
        
        for name, level in skills:
            cursor.execute('''
                INSERT INTO skills (name, level)
                VALUES (?, ?)
            ''', (name, level))
        
        conn.commit()
        conn.close()
        print("✅ Portfolio database initialized!")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============= API ENDPOINTS =============

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': '🚀 DevFlow Portfolio API',
        'version': '1.0.0',
        'endpoints': [
            'GET /api/projects',
            'GET /api/skills',
            'POST /api/contact',
            'GET /api/messages'
        ]
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Fetch all projects"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects')
        projects = cursor.fetchall()
        conn.close()
        
        projects_list = [
            {
                'id': p['id'],
                'title': p['title'],
                'description': p['description'],
                'tags': p['tags'].split(','),
                'link': p['link']
            }
            for p in projects
        ]
        
        return jsonify(projects_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Fetch all skills"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM skills ORDER BY level DESC')
        skills = cursor.fetchall()
        conn.close()
        
        skills_list = [
            {
                'id': s['id'],
                'name': s['name'],
                'level': s['level']
            }
            for s in skills
        ]
        
        return jsonify(skills_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('name', 'email', 'message')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip()
        message = data['message'].strip()
        
        if '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(message) < 5:
            return jsonify({'error': 'Message must be at least 5 characters'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (name, email, message)
            VALUES (?, ?, ?)
        ''', (name, email, message))
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        print(f"📧 New message from {name} ({email})")
        
        return jsonify({
            'success': True,
            'message': f'Thanks {name}! Your message has been received.',
            'id': message_id
        }), 201
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Fetch all messages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC')
        messages = cursor.fetchall()
        conn.close()
        
        messages_list = [
            {
                'id': m['id'],
                'name': m['name'],
                'email': m['email'],
                'message': m['message'],
                'timestamp': m['timestamp']
            }
            for m in messages
        ]
        
        return jsonify({
            'total': len(messages_list),
            'messages': messages_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Message deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get portfolio statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM projects')
        total_projects = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM skills')
        total_skills = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM messages')
        total_messages = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'total_projects': total_projects,
            'total_skills': total_skills,
            'total_messages': total_messages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'server': 'running'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============= MAIN =============

if __name__ == '__main__':
    init_db()
    
    print("=" * 60)
    print("🚀 DevFlow Portfolio Backend")
    print("=" * 60)
    print("📍 Running on: http://localhost:5000")
    print("\n📚 API Endpoints:")
    print("  GET  /api/projects       - Fetch all projects")
    print("  GET  /api/skills         - Fetch all skills")
    print("  POST /api/contact        - Submit contact form")
    print("  GET  /api/messages       - View all messages")
    print("  DELETE /api/messages/<id> - Delete message")
    print("  GET  /api/stats          - Portfolio statistics")
    print("  GET  /api/health         - Health check")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
