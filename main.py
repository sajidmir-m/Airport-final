from app import app

# Export the WSGI application for Vercel
application = app

if __name__ == '__main__':
    # Only run locally, not on Vercel
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
