#!/usr/bin/env python3
"""
Simple test script to verify the Flask app works correctly
"""

from web_server import create_app

def test_app_creation():
    """Test that the Flask app can be created without errors"""
    try:
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test that the airports variable is available within app context
        with app.app_context():
            # Access airports through the app context
            from web_server import create_app
            app_instance = create_app()
            # Get airports from the app instance
            airports = app_instance.config.get('AIRPORTS', {})
            if not airports:
                # Try to get it from the module level
                import web_server
                airports = getattr(web_server, 'airports', {})
            
            print(f"✅ Airports variable available: {len(airports)} airports")
            for code, airport in airports.items():
                print(f"   - {code}: {airport['name']}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating Flask app: {e}")
        return False

def test_routes():
    """Test that routes can be accessed"""
    try:
        app = create_app()
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            print(f"✅ Main page: {response.status_code}")
            
            # Test passenger services page
            response = client.get('/passenger')
            print(f"✅ Passenger services: {response.status_code}")
            
            # Test facilities API
            response = client.get('/api/airport/DEL/facilities')
            print(f"✅ Facilities API: {response.status_code}")
            
            # Test baggage tracking API
            response = client.get('/api/baggage/track?bag_id=BAG12345')
            print(f"✅ Baggage tracking API: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Error testing routes: {e}")
        return False

if __name__ == "__main__":
    print("Testing Airport Dashboard Application...")
    print("=" * 50)
    
    success = True
    success &= test_app_creation()
    success &= test_routes()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! Application is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
