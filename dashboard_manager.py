import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DashboardManager:
    """Manages dashboard configuration and widgets"""
    
    def __init__(self):
        self.widget_types = {
            'passenger_flow': {
                'name': 'Passenger Flow',
                'description': '24-hour passenger traffic visualization',
                'chart_type': 'line'
            },
            'queue_status': {
                'name': 'Queue Status',
                'description': 'Real-time queue monitoring',
                'chart_type': 'bar'
            },
            'baggage_tracking': {
                'name': 'Baggage Tracking',
                'description': 'Live conveyor belt status',
                'chart_type': 'gauge'
            },
            'flight_status': {
                'name': 'Flight Status',
                'description': 'Comprehensive flight information',
                'chart_type': 'table'
            },
            'security_status': {
                'name': 'Security Status',
                'description': 'Checkpoint monitoring',
                'chart_type': 'status'
            },
            'resource_utilization': {
                'name': 'Resource Utilization',
                'description': 'System resource usage',
                'chart_type': 'pie'
            },
            'staff_availability': {
                'name': 'Staff Availability',
                'description': 'Personnel deployment metrics',
                'chart_type': 'bar'
            }
        }
    
    def get_widget_configuration(self, widget_type):
        """Get configuration for a specific widget type"""
        return self.widget_types.get(widget_type, {})
    
    def get_all_widget_types(self):
        """Get all available widget types"""
        return self.widget_types
    
    def create_dashboard_layout(self, airport_code):
        """Create default dashboard layout for an airport"""
        layout = {
            'airport_code': airport_code,
            'created_at': datetime.now().isoformat(),
            'widgets': [
                {'type': 'passenger_flow', 'position': {'row': 1, 'col': 1, 'span': 2}},
                {'type': 'queue_status', 'position': {'row': 1, 'col': 3, 'span': 1}},
                {'type': 'baggage_tracking', 'position': {'row': 2, 'col': 1, 'span': 1}},
                {'type': 'flight_status', 'position': {'row': 2, 'col': 2, 'span': 2}},
                {'type': 'security_status', 'position': {'row': 3, 'col': 1, 'span': 1}},
                {'type': 'resource_utilization', 'position': {'row': 3, 'col': 2, 'span': 1}},
                {'type': 'staff_availability', 'position': {'row': 3, 'col': 3, 'span': 1}}
            ]
        }
        return layout
    
    def validate_widget_data(self, widget_type, data):
        """Validate widget data structure"""
        try:
            widget_config = self.get_widget_configuration(widget_type)
            if not widget_config:
                return False, "Unknown widget type"
            
            # Basic validation - ensure data is not empty
            if not data:
                return False, "Empty data"
            
            return True, "Valid"
        except Exception as e:
            logger.error(f"Error validating widget data: {e}")
            return False, str(e)
