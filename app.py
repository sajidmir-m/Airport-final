import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from web_server import create_app

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to INFO for production

# Create the Flask app
app = create_app()
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure for Vercel deployment
if os.environ.get('VERCEL_ENV'):
    # Vercel-specific configuration
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config['PREFERRED_URL_SCHEME'] = 'https'

# Export the WSGI application for Vercel
application = app

if __name__ == "__main__":
    # Only run locally, not on Vercel
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
