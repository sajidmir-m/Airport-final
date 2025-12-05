from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
    session,
    flash,
    g,
    abort,
)
from datetime import datetime
from dashboard_manager import DashboardManager
from data_sources import DataSourceManager
import logging
from sqlalchemy import select

from database import init_db, db_session
from models import User, StaffNotification

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    # Serve files from public folder
    from flask import send_from_directory
    import os
    
    @app.route('/public/<path:filename>')
    def public_files(filename):
        return send_from_directory(os.path.join(app.root_path, 'public'), filename)
    
    init_db()
    
    # Initialize managers
    dashboard_manager = DashboardManager()
    data_source_manager = DataSourceManager()
    
    # Airport configurations
    airports = {
        'DEL': {'name': 'Indira Gandhi International Airport', 'city': 'New Delhi', 'code': 'DEL'},
        'BLR': {'name': 'Kempegowda International Airport', 'city': 'Bangalore', 'code': 'BLR'},
        'GOX': {'name': 'Manohar International Airport', 'city': 'Goa', 'code': 'GOX'},
        'PNY': {'name': 'Puducherry Airport', 'city': 'Puducherry', 'code': 'PNY'},
        'IXJ': {'name': 'Jammu Airport', 'city': 'Jammu', 'code': 'IXJ'},
        'SXR': {'name': 'Sheikh ul-Alam International Airport', 'city': 'Srinagar', 'code': 'SXR'}
    }
    default_dashboard_widgets = [
        'ai-alerts',
        'conveyor-system',
        'baggage-tracking',
        'ai-insights',
        'passenger-flow',
        'queue-status',
        'flight-status',
        'security-status',
        'resource-utilization',
        'staff-availability',
        'facilities'
    ]
    staff_widget_config = {
        'baggage': ['ai-alerts', 'conveyor-system', 'baggage-tracking', 'ai-insights'],
        'gates': ['ai-alerts', 'flight-status', 'passenger-flow', 'queue-status', 'facilities'],
        'security': ['ai-alerts', 'security-status', 'queue-status', 'staff-availability'],
        'check_in': ['ai-alerts', 'queue-status', 'passenger-flow', 'staff-availability'],
    }
    
    # Simple user class to avoid detached instance errors
    class SimpleUser:
        """Simple user object that doesn't require a database session"""
        def __init__(self, user_id, email, full_name, role, organization=None, airport_code=None, work_assignment=None, created_by=None, created_at=None):
            self.id = user_id
            self.email = email
            self.full_name = full_name
            self.role = role
            self.organization = organization
            self.airport_code = airport_code
            self.work_assignment = work_assignment
            self.created_by = created_by
            self.created_at = created_at
    
    @app.before_request
    def load_current_user():
        g.current_user = None
        user_id = session.get('user_id')
        if user_id:
            try:
                with db_session() as db:
                    user = db.get(User, user_id)
                    if user:
                        # Access all attributes while session is still open
                        # Create SimpleUser with all needed data
                        g.current_user = SimpleUser(
                            user_id=user.id,
                            email=user.email,
                            full_name=user.full_name,
                            role=user.role,
                            organization=user.organization,
                            airport_code=user.airport_code,
                            work_assignment=user.work_assignment,
                            created_by=user.created_by,
                            created_at=user.created_at
                        )
            except Exception as e:
                logger.error(f"Failed to load current user: {e}")
                session.pop('user_id', None)
                session.pop('user_role', None)

    @app.context_processor
    def inject_user():
        return {'current_user': getattr(g, 'current_user', None)}
    
    @app.route('/')
    def index():
        """Intro/landing page - Always show intro page first"""
        # Always show intro page - users can navigate to their portals from navbar
        return render_template('index.html', airports=airports)
    
    @app.route('/dashboard/<airport_code>')
    def dashboard(airport_code):
        """Individual airport dashboard - Staff, Manager and Admin only"""
        # Check if user is logged in and has appropriate role
        user = getattr(g, 'current_user', None)
        if not user:
            flash("Please login to access airport dashboards.")
            return redirect(url_for('login', next=request.path))
        
        # Only staff, manager and admin can access dashboards
        if user.role not in ['staff', 'manager', 'admin']:
            flash("Airport dashboards are only available to staff, managers and administrators.")
            return redirect(url_for('passenger_services'))
        
        # Staff and managers can only access their assigned airport
        if user.role in ['staff', 'manager']:
            if not user.airport_code or user.airport_code != airport_code:
                flash(f"You can only access the dashboard for your assigned airport.")
                if user.airport_code:
                    return redirect(url_for('dashboard', airport_code=user.airport_code))
                else:
                    return redirect(url_for('portal', role=user.role))
        
        if airport_code not in airports:
            return "Airport not found", 404
        
        airport_info = airports[airport_code]

        allowed_widgets = list(default_dashboard_widgets)
        alert_scopes = ['all']
        work_assignment = getattr(user, 'work_assignment', None)

        if user.role == 'staff':
            assignment_key = (work_assignment or '').lower()
            allowed_widgets = list(staff_widget_config.get(assignment_key, default_dashboard_widgets))
            if assignment_key:
                alert_scopes.append(assignment_key)
        elif user.role == 'manager':
            alert_scopes.append('management')
            if work_assignment:
                alert_scopes.append(work_assignment.lower())
        elif user.role == 'admin':
            alert_scopes.append('management')

        return render_template(
            'dashboard.html',
            airport=airport_info,
            airport_code=airport_code,
            allowed_widgets=allowed_widgets,
            alert_scopes=alert_scopes,
            work_assignment=work_assignment,
            user_role=user.role
        )
    
    @app.route('/settings')
    def settings():
        """Settings and configuration page - Admin, Staff, Manager only"""
        user = getattr(g, 'current_user', None)
        if not user:
            flash("Please login to access settings.")
            return redirect(url_for('login', next=request.path))
        
        # Only admin, staff, and manager can access settings
        if user.role not in ['admin', 'staff', 'manager']:
            flash("Settings are only available to staff, managers, and administrators.")
            return redirect(url_for('index'))
        
        return render_template('settings.html', airports=airports)

    # Authentication Routes
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """Signup page - Only for passengers (user role)"""
        error = None
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            organization = request.form.get('organization', '').strip() or None

            if not full_name or not email or not password:
                error = "All fields are required."
            elif len(password) < 6:
                error = "Password must be at least 6 characters long."
            else:
                try:
                    with db_session() as db:
                        existing = db.execute(
                            select(User).where(User.email == email)
                        ).scalar_one_or_none()
                        if existing:
                            error = "An account with this email already exists."
                        else:
                            # Only create passenger accounts (user role)
                            user = User(
                                full_name=full_name,
                                email=email,
                                role='user',  # Always 'user' for signup
                                organization=organization,
                                airport_code=None  # Passengers don't have airport assignment
                            )
                            user.set_password(password)
                            db.add(user)
                            db.commit()
                            session['user_id'] = user.id
                            session['user_role'] = user.role
                            flash("Account created successfully! Welcome to the Passenger Portal.")
                            return redirect(url_for('passenger_services'))
                except Exception as e:
                    logger.error(f"Signup error: {e}")
                    error = "Failed to create account. Please try again."

        return render_template('signup.html', error=error)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        next_url = request.args.get('next')
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            next_url = request.form.get('next') or next_url

            if not email or not password:
                error = "Email and password are required."
            else:
                try:
                    with db_session() as db:
                        user = db.execute(
                            select(User).where(User.email == email)
                        ).scalar_one_or_none()
                        
                        if not user:
                            error = "Invalid email or password."
                            logger.warning(f"Login attempt with non-existent email: {email}")
                        elif not user.check_password(password):
                            error = "Invalid email or password."
                            logger.warning(f"Login attempt with wrong password for: {email}")
                        else:
                            # Successful login
                            session['user_id'] = user.id
                            session['user_role'] = user.role
                            logger.info(f"User logged in: {user.email} (role: {user.role})")
                            
                            # Redirect based on user role
                            if next_url:
                                destination = next_url
                            elif user.role == 'user':
                                destination = url_for('passenger_services')
                            elif user.role == 'manager':
                                destination = url_for('portal', role='manager')  # Managers use manager portal
                            else:
                                destination = url_for('portal', role=user.role)
                            return redirect(destination)
                except Exception as e:
                    logger.error(f"Login error: {e}", exc_info=True)
                    error = "Unable to log in at the moment. Please try again."

        return render_template('login.html', error=error, next=next_url)

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('user_role', None)
        flash("You have been signed out.")
        return redirect(url_for('login'))

    # Portal Routes
    @app.route('/portal/<role>')
    def portal(role):
        try:
            role = role.lower()
            allowed_roles = {'admin', 'staff', 'manager', 'user'}
            if role not in allowed_roles:
                abort(404)

            user = getattr(g, 'current_user', None)
            if not user:
                return redirect(url_for('login', next=request.path))

            # Ensure we're working with SimpleUser (not detached ORM object)
            if not hasattr(user, 'role'):
                logger.error("Invalid user object in portal route")
                return redirect(url_for('login', next=request.path))

            # For regular users, redirect to passenger services instead
            if role == 'user' and user.role == 'user':
                return redirect(url_for('passenger_services'))
            
            # Handle manager role - managers can access their portal
            if user.role == 'manager':
                if role == 'manager' or role == 'staff':
                    return render_template('portal_staff.html', airports=airports)
                else:
                    abort(403)

            # Check role match
            if user.role != role:
                abort(403)

            template_map = {
                'admin': 'portal_admin.html',
                'staff': 'portal_staff.html',
                'manager': 'portal_staff.html',
                'user': 'portal_user.html',
            }
            return render_template(template_map.get(role, 'portal_staff.html'), airports=airports)
        except Exception as e:
            logger.error(f"Error in portal route: {e}")
            flash("An error occurred. Please try again.")
            return redirect(url_for('index'))
    
    # API Endpoints
    @app.route('/api/airport/<airport_code>/passenger-flow')
    def get_passenger_flow(airport_code):
        """Get passenger flow data for charts"""
        try:
            data = data_source_manager.get_passenger_flow_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting passenger flow data: {e}")
            return jsonify({'error': 'Failed to fetch passenger flow data'}), 500
    
    @app.route('/api/airport/<airport_code>/queue-status')
    def get_queue_status(airport_code):
        """Get queue monitoring data"""
        try:
            data = data_source_manager.get_queue_status_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting queue status data: {e}")
            return jsonify({'error': 'Failed to fetch queue status data'}), 500
    
    @app.route('/api/airport/<airport_code>/baggage-tracking')
    def get_baggage_tracking(airport_code):
        """Get baggage tracking data"""
        try:
            data = data_source_manager.get_baggage_tracking_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting baggage tracking data: {e}")
            return jsonify({'error': 'Failed to fetch baggage tracking data'}), 500
    
    @app.route('/api/airport/<airport_code>/flight-status')
    def get_flight_status(airport_code):
        """Get flight status data"""
        try:
            data = data_source_manager.get_flight_status_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting flight status data: {e}")
            return jsonify({'error': 'Failed to fetch flight status data'}), 500
    
    @app.route('/api/airport/<airport_code>/security-status')
    def get_security_status(airport_code):
        """Get security checkpoint status"""
        try:
            data = data_source_manager.get_security_status_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting security status data: {e}")
            return jsonify({'error': 'Failed to fetch security status data'}), 500
    
    @app.route('/api/airport/<airport_code>/resource-utilization')
    def get_resource_utilization(airport_code):
        """Get resource utilization data"""
        try:
            data = data_source_manager.get_resource_utilization_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting resource utilization data: {e}")
            return jsonify({'error': 'Failed to fetch resource utilization data'}), 500
    
    @app.route('/api/airport/<airport_code>/staff-availability')
    def get_staff_availability(airport_code):
        """Get staff availability data"""
        try:
            data = data_source_manager.get_staff_availability_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting staff availability data: {e}")
            return jsonify({'error': 'Failed to fetch staff availability data'}), 500
    
    @app.route('/api/airport/<airport_code>/dashboard-data')
    def get_dashboard_data(airport_code):
        """Get all dashboard data at once"""
        try:
            dataset_fetchers = {
                'passenger_flow': data_source_manager.get_passenger_flow_data,
                'queue_status': data_source_manager.get_queue_status_data,
                'baggage_tracking': data_source_manager.get_baggage_tracking_data,
                'flight_status': data_source_manager.get_flight_status_data,
                'security_status': data_source_manager.get_security_status_data,
                'resource_utilization': data_source_manager.get_resource_utilization_data,
                'staff_availability': data_source_manager.get_staff_availability_data
            }

            data = {}
            errors = {}

            for key, fetcher in dataset_fetchers.items():
                try:
                    result = fetcher(airport_code)
                    data[key] = result
                    if isinstance(result, dict) and result.get('error'):
                        errors[key] = result['error']
                except Exception as dataset_error:
                    readable_name = key.replace('_', ' ').title()
                    logger.error(f"Error getting {key} data: {dataset_error}")
                    data[key] = {'error': f'Failed to fetch {readable_name} data'}
                    errors[key] = str(dataset_error)

            if errors:
                data['errors'] = errors

            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return jsonify({'error': 'Failed to fetch dashboard data'}), 500
    
    # New Enhanced API Endpoints
    @app.route('/api/airport/<airport_code>/weather')
    def get_weather(airport_code):
        """Get weather data"""
        try:
            data = data_source_manager.get_weather_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return jsonify({'error': 'Failed to fetch weather data'}), 500
    
    @app.route('/api/airport/<airport_code>/live-conveyors')
    def get_live_conveyors(airport_code):
        """Get live conveyor belt data"""
        try:
            data = data_source_manager.get_live_conveyor_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting live conveyor data: {e}")
            return jsonify({'error': 'Failed to fetch live conveyor data'}), 500
    
    @app.route('/api/airport/<airport_code>/facilities')
    def get_facilities(airport_code):
        """Get airport facilities information"""
        try:
            data = data_source_manager.get_airport_facilities(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting facilities data: {e}")
            return jsonify({'error': 'Failed to fetch facilities data'}), 500
    
    @app.route('/api/baggage/track')
    def track_baggage():
        """Track passenger baggage"""
        try:
            bag_id = request.args.get('bag_id')
            flight_number = request.args.get('flight_number')
            data = data_source_manager.track_passenger_baggage(bag_id, flight_number)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error tracking baggage: {e}")
            return jsonify({'error': 'Failed to track baggage'}), 500
    
    @app.route('/api/complaints/submit', methods=['POST'])
    def submit_complaint():
        """Submit baggage complaint"""
        try:
            request_data = request.get_json()
            data = data_source_manager.submit_baggage_complaint(
                request_data.get('passenger_name', ''),
                request_data.get('flight_number', ''),
                request_data.get('bag_id', ''),
                request_data.get('issue_type', ''),
                    request_data.get('description', ''),
                    request_data.get('airport_code')
            )
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error submitting complaint: {e}")
            return jsonify({'error': 'Failed to submit complaint'}), 500
    
    @app.route('/api/airport/<airport_code>/complaints')
    def get_complaints(airport_code):
        """Get complaints data for staff"""
        try:
            data = data_source_manager.get_complaints_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting complaints data: {e}")
            return jsonify({'error': 'Failed to fetch complaints data'}), 500
    
    @app.route('/api/airport/<airport_code>/ai-insights')
    def get_ai_insights(airport_code):
        """Get AI-powered baggage system insights"""
        try:
            data = data_source_manager.get_ai_baggage_insights(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return jsonify({'error': 'Failed to fetch AI insights'}), 500
    
    # Passenger Services Pages
    @app.route('/passenger')
    def passenger_services():
        """Passenger services page"""
        return render_template('passenger_services.html', airports=airports)
    
    @app.route('/staff')
    def staff_portal():
        """Staff portal page - Staff, Manager and Admin only"""
        user = getattr(g, 'current_user', None)
        if not user:
            flash("Please login to access the staff portal.")
            return redirect(url_for('login', next=request.path))
        
        # Only staff, manager and admin can access staff portal
        if user.role not in ['staff', 'manager', 'admin']:
            flash("Staff portal is only available to staff, managers and administrators.")
            return redirect(url_for('passenger_services'))
        
        return render_template('staff_portal.html', airports=airports)

    @app.route('/staff/gate-management')
    def gate_management():
        """Dedicated gate management page for gate staff"""
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ['staff', 'manager', 'admin']:
            flash("Access denied.")
            return redirect(url_for('login', next=request.path))

        if user.role == 'staff':
            if user.work_assignment != 'gates':
                flash("Gate management is only available to gate staff.")
                return redirect(url_for('portal', role=user.role))
            if not user.airport_code:
                flash("You must be assigned to an airport to view gate operations.")
                return redirect(url_for('portal', role=user.role))

        airport_code = user.airport_code if user.role in ['staff', 'manager'] else request.args.get('airport', 'DEL')
        if airport_code not in airports:
            airport_code = 'DEL'

        return render_template(
            'gate_management.html',
            airport=airports[airport_code],
            airport_code=airport_code
        )
    
    # User Management Routes
    @app.route('/manage-users', methods=['GET', 'POST'])
    def manage_users():
        """User management page - Admin and Managers only"""
        user = getattr(g, 'current_user', None)
        if not user:
            flash("Please login to access user management.")
            return redirect(url_for('login', next=request.path))
        
        # Only admin and managers can manage users
        if user.role not in ['admin', 'manager']:
            flash("User management is only available to administrators and managers.")
            return redirect(url_for('passenger_services'))
        
        if request.method == 'POST':
            try:
                action = request.form.get('action')
                
                if action == 'create':
                    # Create new user
                    email = request.form.get('email', '').strip().lower()
                    full_name = request.form.get('full_name', '').strip()
                    role = request.form.get('role', '').strip()
                    password = request.form.get('password', '')
                    airport_code = request.form.get('airport_code', '').strip() or None
                    work_assignment = request.form.get('work_assignment', '').strip() or None
                    
                    # Validation
                    if not email or not full_name or not role or not password:
                        flash("All fields are required.")
                        return redirect(url_for('manage_users'))
                    
                    # Role restrictions
                    if user.role == 'manager':
                        # Managers can only create staff for their airport
                        if role not in ['staff']:
                            flash("Managers can only create staff members.")
                            return redirect(url_for('manage_users'))
                        if airport_code != user.airport_code:
                            flash("Managers can only assign staff to their own airport.")
                            return redirect(url_for('manage_users'))
                        # Staff must have work assignment
                        if role == 'staff' and not work_assignment:
                            flash("Work assignment is required for staff members.")
                            return redirect(url_for('manage_users'))
                    
                    # Admin can create managers and staff
                    if user.role == 'admin' and role not in ['manager', 'staff']:
                        flash("Admin can only create managers and staff.")
                        return redirect(url_for('manage_users'))
                    
                    # Staff must have work assignment
                    if role == 'staff' and not work_assignment:
                        flash("Work assignment is required for staff members.")
                        return redirect(url_for('manage_users'))
                    
                    with db_session() as db:
                        # Check if email already exists
                        existing = db.execute(
                            select(User).where(User.email == email)
                        ).scalar_one_or_none()
                        
                        if existing:
                            flash("Email already exists.")
                            return redirect(url_for('manage_users'))
                        
                        # Create new user
                        new_user = User(
                            email=email,
                            full_name=full_name,
                            role=role,
                            airport_code=airport_code,
                            work_assignment=work_assignment,
                            created_by=user.id
                        )
                        new_user.set_password(password)
                        db.add(new_user)
                        db.commit()
                        
                        # Refresh the user to ensure it's saved
                        db.refresh(new_user)
                        logger.info(f"User created: {email} (role: {role}, airport: {airport_code}, work: {work_assignment})")
                        
                        flash(f"User {full_name} created successfully!")
                
                elif action == 'delete':
                    # Delete user
                    user_id = request.form.get('user_id')
                    if user_id:
                        with db_session() as db:
                            user_to_delete = db.get(User, user_id)
                            if user_to_delete:
                                # Prevent deleting yourself or admin
                                if user_to_delete.id == user.id:
                                    flash("You cannot delete your own account.")
                                elif user_to_delete.role == 'admin':
                                    flash("Cannot delete admin accounts.")
                                else:
                                    # Managers can only delete staff from their airport
                                    if user.role == 'manager' and user_to_delete.airport_code != user.airport_code:
                                        flash("You can only delete staff from your assigned airport.")
                                    else:
                                        db.delete(user_to_delete)
                                        db.commit()
                                        flash("User deleted successfully.")
                
            except Exception as e:
                logger.error(f"Error managing users: {e}")
                flash("An error occurred while managing users.")
        
        # Get users list
        try:
            with db_session() as db:
                if user.role == 'admin':
                    # Admin can see all users
                    all_users = db.execute(select(User).order_by(User.created_at.desc())).scalars().all()
                else:
                    # Managers can only see staff from their airport
                    all_users = db.execute(
                        select(User).where(
                            User.airport_code == user.airport_code,
                            User.role == 'staff'
                        ).order_by(User.created_at.desc())
                    ).scalars().all()
                
                users_list = []
                for u in all_users:
                    users_list.append({
                        'id': u.id,
                        'email': u.email,
                        'full_name': u.full_name,
                        'role': u.role,
                        'airport_code': u.airport_code,
                        'work_assignment': u.work_assignment,
                        'created_at': u.created_at
                    })
                
                logger.info(f"Fetched {len(users_list)} users for {user.role} user {user.email}")
        except Exception as e:
            logger.error(f"Error fetching users: {e}", exc_info=True)
            users_list = []
        
        return render_template('manage_users.html', 
                             users=users_list, 
                             airports=airports,
                             current_user=user)
    
    @app.route('/manager/<airport_code>/baggage-issues')
    def manager_baggage_issues(airport_code):
        """Manager view of baggage issues"""
        user = getattr(g, 'current_user', None)
        if not user or user.role != 'manager' or user.airport_code != airport_code:
            flash("Access denied.")
            return redirect(url_for('portal', role=user.role if user else 'user'))
        
        # Get baggage data from dashboard
        try:
            conveyor_data = data_source_manager.get_live_conveyor_data(airport_code)
            
            # Extract issues and alerts
            issues = []
            for belt in conveyor_data.get('conveyor_belts', []):
                if belt.get('health_status') != 'Good' or belt.get('delay_risk') != 'Low':
                    issues.append({
                        'belt_id': belt.get('belt_id'),
                        'status': belt.get('status'),
                        'health_status': belt.get('health_status'),
                        'delay_risk': belt.get('delay_risk'),
                        'efficiency_score': belt.get('efficiency_score'),
                        'terminal': belt.get('terminal'),
                        'predicted_issues': belt.get('predicted_issues', [])
                    })
            
            alerts = conveyor_data.get('ai_alerts', [])
            
        except Exception as e:
            logger.error(f"Error loading baggage issues: {e}")
            issues = []
            alerts = []
        
        return render_template('manager_baggage_issues.html',
                             airport_code=airport_code,
                             airport=airports.get(airport_code),
                             issues=issues,
                             alerts=alerts,
                             current_user=user)
    
    @app.route('/api/airport/<airport_code>/manager-overview')
    def manager_overview(airport_code):
        """API endpoint for manager overview data"""
        user = getattr(g, 'current_user', None)
        if not user or user.role != 'manager' or user.airport_code != airport_code:
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            with db_session() as db:
                # Count staff
                staff_count = db.execute(
                    select(User).where(
                        User.airport_code == airport_code,
                        User.role == 'staff'
                    )
                ).scalars().all()
                total_staff = len(staff_count)
                
                # Get baggage issues count
                conveyor_data = data_source_manager.get_live_conveyor_data(airport_code)
                active_issues = sum(1 for b in conveyor_data.get('conveyor_belts', []) 
                                  if b.get('health_status') != 'Good')
                baggage_alerts = len(conveyor_data.get('ai_alerts', []))
                
                # Queue status (simplified)
                queue_status = "Normal"
                
                return jsonify({
                    'total_staff': total_staff,
                    'active_issues': active_issues,
                    'baggage_alerts': baggage_alerts,
                    'queue_status': queue_status
                })
        except Exception as e:
            logger.error(f"Error in manager overview: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/airport/<airport_code>/staff-list')
    def airport_staff_list(airport_code):
        """API endpoint to get staff list for an airport"""
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Managers can only see their own airport
        if user.role == 'manager' and user.airport_code != airport_code:
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            with db_session() as db:
                staff_list = db.execute(
                    select(User).where(
                        User.airport_code == airport_code,
                        User.role == 'staff'
                    )
                ).scalars().all()
                
                result = []
                for s in staff_list:
                    result.append({
                        'id': s.id,
                        'full_name': s.full_name,
                        'email': s.email,
                        'work_assignment': s.work_assignment
                    })
                
                return jsonify({'staff': result})
        except Exception as e:
            logger.error(f"Error fetching staff list: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/airport/<airport_code>/gate-operations')
    def gate_operations_data(airport_code):
        """Gate operations data for gate staff"""
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ['staff', 'manager', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        if user.role == 'staff' and user.work_assignment != 'gates':
            return jsonify({'error': 'Unauthorized'}), 403

        try:
            data = data_source_manager.get_gate_operations_data(airport_code)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting gate operations data: {e}")
            return jsonify({'error': 'Failed to fetch gate operations data'}), 500

    def serialize_notification(notification: StaffNotification):
        return {
            'id': notification.id,
            'sender_id': notification.sender_id,
            'recipient_id': notification.recipient_id,
            'airport_code': notification.airport_code,
            'message': notification.message,
            'priority': notification.priority,
            'status': notification.status,
            'attachment_url': notification.attachment_url,
            'created_at': notification.created_at.isoformat() if notification.created_at else None,
            'acknowledged_at': notification.acknowledged_at.isoformat() if notification.acknowledged_at else None,
        }

    @app.route('/api/staff-notifications', methods=['POST'])
    def create_staff_notification():
        """Managers/Admins send notifications to staff"""
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ['manager', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        payload = request.get_json() or {}
        staff_id = (payload.get('staff_id') or '').strip()
        message = (payload.get('message') or '').strip()
        priority = (payload.get('priority') or 'normal').lower()
        attachment_url = (payload.get('attachment_url') or '').strip() or None

        if not staff_id or not message:
            return jsonify({'error': 'Staff member and message are required.'}), 400

        if priority not in ['normal', 'high', 'urgent']:
            priority = 'normal'

        try:
            with db_session() as db:
                staff_member = db.get(User, staff_id)
                if not staff_member or staff_member.role != 'staff':
                    return jsonify({'error': 'Selected staff member not found.'}), 404

                if user.role == 'manager':
                    if not user.airport_code or staff_member.airport_code != user.airport_code:
                        return jsonify({'error': 'You can only notify staff from your airport.'}), 403

                notification = StaffNotification(
                    sender_id=user.id,
                    recipient_id=staff_member.id,
                    airport_code=staff_member.airport_code or user.airport_code,
                    message=message,
                    priority=priority,
                    attachment_url=attachment_url,
                )
                db.add(notification)
                db.commit()
                db.refresh(notification)

                return jsonify({
                    'success': True,
                    'notification': serialize_notification(notification)
                })
        except Exception as e:
            logger.error(f"Error creating staff notification: {e}", exc_info=True)
            return jsonify({'error': 'Failed to send notification'}), 500

    @app.route('/api/staff/notifications')
    def get_staff_notifications():
        """Get notifications for the logged in staff/manager/admin"""
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ['staff', 'manager', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        status_filter = request.args.get('status')
        include_sent = request.args.get('sent') == 'true'

        try:
            with db_session() as db:
                query = select(StaffNotification).where(
                    StaffNotification.recipient_id == user.id
                ).order_by(StaffNotification.created_at.desc())

                if status_filter == 'unread':
                    query = query.where(StaffNotification.status == 'pending')

                notifications = db.execute(query).scalars().all()

                sent_notifications = []
                if include_sent and user.role in ['manager', 'admin']:
                    sent_query = select(StaffNotification).where(
                        StaffNotification.sender_id == user.id
                    ).order_by(StaffNotification.created_at.desc())
                    sent_notifications = db.execute(sent_query).scalars().all()

                return jsonify({
                    'notifications': [serialize_notification(n) for n in notifications],
                    'sent_notifications': [serialize_notification(n) for n in sent_notifications]
                })
        except Exception as e:
            logger.error(f"Error fetching staff notifications: {e}", exc_info=True)
            return jsonify({'error': 'Failed to load notifications'}), 500

    @app.route('/api/staff-notifications/<notification_id>/ack', methods=['POST'])
    def acknowledge_staff_notification(notification_id):
        """Mark a notification as acknowledged by the recipient"""
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ['staff', 'manager', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        try:
            with db_session() as db:
                notification = db.get(StaffNotification, notification_id)
                if not notification:
                    return jsonify({'error': 'Notification not found'}), 404

                if notification.recipient_id != user.id:
                    return jsonify({'error': 'You can only acknowledge your notifications.'}), 403

                notification.status = 'acknowledged'
                notification.acknowledged_at = datetime.utcnow()
                db.add(notification)
                db.commit()

                return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error acknowledging notification: {e}", exc_info=True)
            return jsonify({'error': 'Failed to update notification'}), 500

    @app.route('/api/admin/staff-allocation')
    def admin_staff_allocation():
        """API endpoint for admin to view staff allocation across all airports"""
        user = getattr(g, 'current_user', None)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            with db_session() as db:
                all_users = db.execute(select(User)).scalars().all()
                
                # Group by airport
                airport_data = {}
                for u in all_users:
                    if u.airport_code:
                        if u.airport_code not in airport_data:
                            airport_data[u.airport_code] = {
                                'code': u.airport_code,
                                'name': airports.get(u.airport_code, {}).get('name', u.airport_code),
                                'managers': 0,
                                'total_staff': 0,
                                'work_assignments': set(),
                                'resources': {'belts': 0, 'gates': 0}
                            }
                        
                        if u.role == 'manager':
                            airport_data[u.airport_code]['managers'] += 1
                        elif u.role == 'staff':
                            airport_data[u.airport_code]['total_staff'] += 1
                            if u.work_assignment:
                                airport_data[u.airport_code]['work_assignments'].add(u.work_assignment)
                
                # Get resources for each airport using existing data source manager
                for code in airport_data.keys():
                    try:
                        conveyor_data = data_source_manager.get_live_conveyor_data(code)
                        airport_data[code]['resources']['belts'] = len(conveyor_data.get('conveyor_belts', []))
                        # Gates count (simplified - you can enhance this)
                        airport_data[code]['resources']['gates'] = 20  # Default estimate
                    except Exception as resource_error:
                        logger.warning(f"Failed to enrich resources for {code}: {resource_error}")
                
                # Convert to list and format
                result = []
                for code, data in airport_data.items():
                    result.append({
                        'code': data['code'],
                        'name': data['name'],
                        'managers': data['managers'],
                        'total_staff': data['total_staff'],
                        'work_assignments': list(data['work_assignments']),
                        'resources': data['resources']
                    })
                
                return jsonify({'airports': result})
        except Exception as e:
            logger.error(f"Error in staff allocation: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/verify-admin')
    def verify_admin():
        """Debug route to verify admin user exists"""
        try:
            with db_session() as db:
                admin = db.execute(
                    select(User).where(User.email == "mirsajidd7@gmail.com")
                ).scalar_one_or_none()
                
                if admin:
                    return jsonify({
                        'exists': True,
                        'email': admin.email,
                        'role': admin.role,
                        'full_name': admin.full_name,
                        'password_check': admin.check_password("123456")
                    })
                else:
                    return jsonify({
                        'exists': False,
                        'message': 'Admin user not found.'
                    })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    
    @app.errorhandler(404)
    def not_found(error):
        # If user is passenger, redirect to passenger portal
        user = getattr(g, 'current_user', None)
        if user and user.role == 'user':
            return redirect(url_for('passenger_services'))
        return render_template('index.html', airports=airports, error="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app
