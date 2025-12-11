"""
Vercel serverless function entry point for Flask application.
This file exports the Flask app for Vercel's serverless environment.
"""
import os
import logging
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from web_server import create_app

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app with error handling
app_created = False
try:
    app = create_app()
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app_created = True
except Exception as e:
    logger.error(f"Failed to create Flask app: {e}", exc_info=True)
    # Create a minimal app that shows error
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    
    @app.route('/')
    @app.route('/<path:path>')
    def error_handler(path=''):
        return jsonify({
            'error': 'Application initialization failed',
            'message': str(e),
            'hint': 'Check Vercel logs for details. Ensure DATABASE_URL is set correctly.'
        }), 500

# Configure for Vercel deployment (only if app was created successfully)
if app_created and os.environ.get('VERCEL_ENV'):
    try:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        app.config['PREFERRED_URL_SCHEME'] = 'https'
    except Exception as e:
        logger.warning(f"Failed to configure ProxyFix: {e}")

# Sample route to fetch data from Supabase (only if app was created successfully)
if app_created:
    @app.route('/api/sample/users')
    def sample_users():
        """
        Sample API route to fetch users from Supabase database.
        This demonstrates how to query Supabase using SQLAlchemy.
        """
        try:
            from database import db_session
            from models import User
            from sqlalchemy import select
            
            with db_session() as db:
                # Query users from the database
                users = db.execute(select(User).limit(10)).scalars().all()
                
                # Serialize users
                users_data = []
                for user in users:
                    users_data.append({
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'role': user.role,
                        'airport_code': user.airport_code,
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    })
                
                return jsonify({
                    'success': True,
                    'count': len(users_data),
                    'users': users_data
                })
        except Exception as e:
            logger.error(f"Error fetching users: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/health')
    def health_check():
        """Health check endpoint for Vercel monitoring"""
        try:
            # Test database connection
            from database import db_session
            from sqlalchemy import text
            
            with db_session() as db:
                db.execute(text("SELECT 1"))
            return jsonify({
                'status': 'healthy',
                'database': 'connected'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 500

    @app.route('/api/test')
    def test():
        """Simple test route to verify the app is running"""
        return jsonify({
            'status': 'ok',
            'message': 'Flask app is running',
            'database_configured': os.environ.get('DATABASE_URL') is not None
        })

# Export the WSGI application for Vercel
# Vercel expects the app to be named 'app'
application = app

# For local development
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
