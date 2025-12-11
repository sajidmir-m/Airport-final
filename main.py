"""
Vercel serverless function entry point for Flask application.
This file exports the Flask app for Vercel's serverless environment.
"""
import os
import sys
import logging
import traceback
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app with comprehensive error handling
app_created = False
init_error = None

try:
    # Try to import and create the app
    from web_server import create_app
    app = create_app()
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app_created = True
    logger.info("Flask app created successfully")
except ImportError as e:
    init_error = f"Import error: {str(e)}\n{traceback.format_exc()}"
    logger.error(init_error)
except Exception as e:
    init_error = f"Failed to create Flask app: {str(e)}\n{traceback.format_exc()}"
    logger.error(init_error, exc_info=True)

# If app creation failed, create a minimal error app
if not app_created:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    
    @app.route('/')
    def error_handler_root():
        error_msg = init_error or "Unknown error during initialization"
        # Return HTML for browser requests
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #d32f2f; }}
                pre {{ background: #f5f5f5; padding: 20px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Application Initialization Failed</h1>
            <p><strong>Error:</strong> {str(error_msg).split(chr(10))[0]}</p>
            <p>Check Vercel logs for details. Ensure DATABASE_URL is set correctly.</p>
            <details>
                <summary>Full Error Details</summary>
                <pre>{error_msg}</pre>
            </details>
            <p><small>Python: {sys.version.split()[0]} | Vercel Env: {os.environ.get('VERCEL_ENV', 'not set')}</small></p>
        </body>
        </html>
        """, 500
    
    @app.route('/<path:path>')
    def error_handler(path=''):
        error_msg = init_error or "Unknown error during initialization"
        # Check if it's an API request
        if path.startswith('api/'):
            return jsonify({
                'error': 'Application initialization failed',
                'message': str(error_msg).split('\n')[0],
                'full_error': error_msg,
                'hint': 'Check Vercel logs for details. Ensure DATABASE_URL is set correctly.',
                'python_version': sys.version,
                'vercel_env': os.environ.get('VERCEL_ENV', 'not set')
            }), 500
        else:
            # Return HTML for other routes
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Application Error</title></head>
            <body>
                <h1>Application Initialization Failed</h1>
                <p>{str(error_msg).split(chr(10))[0]}</p>
            </body>
            </html>
            """, 500
    
    # Add a test route even in error mode
    @app.route('/api/test')
    def test_error_mode():
        return jsonify({
            'status': 'error',
            'message': 'App initialization failed',
            'error': str(init_error).split('\n')[0] if init_error else 'Unknown error'
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
# Vercel expects the app to be named 'app' or 'application'
# Ensure it's always defined, even if initialization failed
if 'app' not in locals():
    # Fallback: create absolute minimal app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    
    @app.route('/')
    @app.route('/<path:path>')
    def fallback_error(path=''):
        return jsonify({
            'error': 'Critical initialization failure',
            'message': 'Unable to create Flask application'
        }), 500

application = app

# For local development
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
