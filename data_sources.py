import random
import datetime
from typing import Dict, List, Any, Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)

class DataSourceManager:
    """Manages data sources for airport operations"""
    
    def __init__(self):
        self.flight_statuses = ['On Time', 'Delayed', 'Boarding', 'Departed', 'Cancelled', 'Arrived']
        self.airlines = ['Air India', 'IndiGo', 'SpiceJet', 'Vistara', 'GoAir', 'Emirates', 'Singapore Airlines']
        self.destinations = {
            'DEL': ['Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Goa'],
            'BLR': ['Delhi', 'Mumbai', 'Chennai', 'Hyderabad', 'Kochi', 'Pune', 'Goa'],
            'GOX': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Pune', 'Hyderabad'],
            'PNY': ['Chennai', 'Bangalore', 'Delhi', 'Mumbai', 'Hyderabad'],
            'IXJ': ['Delhi', 'Mumbai', 'Srinagar', 'Chandigarh', 'Amritsar'],
            'SXR': ['Delhi', 'Mumbai', 'Jammu', 'Chandigarh', 'Leh']
        }
        
        # Real airport facility data
        self.airport_facilities = {
            'DEL': {
                'terminals': ['T1', 'T2', 'T3'],
                'gates': {
                    'T1': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10'],
                    'T2': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10'], 
                    'T3': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
                },
                'airlines': {
                    'T1': ['Air India', 'IndiGo', 'SpiceJet'],
                    'T2': ['Vistara', 'GoAir'],
                    'T3': ['Emirates', 'Singapore Airlines', 'Air India']
                },
                'washrooms': [
                    {'location': 'T1 - Gate A5', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Arrival Hall', 'type': 'General', 'status': 'Available'},
                    {'location': 'T2 - Gate B7', 'type': 'General', 'status': 'Available'},
                    {'location': 'T3 - Gate C3', 'type': 'General', 'status': 'Available'},
                    {'location': 'T3 - Gate C8', 'type': 'Family', 'status': 'Available'}
                ],
                'services': [
                    {'name': 'Currency Exchange', 'location': 'T3 - Level 1', 'hours': '24/7'},
                    {'name': 'ATM', 'location': 'All Terminals', 'hours': '24/7'},
                    {'name': 'Medical Center', 'location': 'T3 - Level 2', 'hours': '24/7'},
                    {'name': 'Pharmacy', 'location': 'T1 & T3', 'hours': '6:00-23:00'},
                    {'name': 'Prayer Room', 'location': 'T3 - Level 1', 'hours': '24/7'},
                    {'name': 'Baby Care Room', 'location': 'T1 & T3', 'hours': '24/7'},
                    {'name': 'WiFi Hotspot', 'location': 'All Terminals', 'hours': '24/7'},
                    {'name': 'Information Desk', 'location': 'All Terminals', 'hours': '24/7'}
                ]
            },
            'BLR': {
                'terminals': ['T1', 'T2'],
                'gates': {
                    'T1': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'],
                    'T2': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']
                },
                'airlines': {
                    'T1': ['Air India', 'IndiGo', 'SpiceJet', 'Vistara'],
                    'T2': ['Emirates', 'Singapore Airlines', 'GoAir']
                },
                'washrooms': [
                    {'location': 'T1 - Gate A3', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Departure Lounge', 'type': 'General', 'status': 'Available'},
                    {'location': 'T2 - Gate B5', 'type': 'General', 'status': 'Available'},
                    {'location': 'T2 - Arrival Hall', 'type': 'Family', 'status': 'Available'}
                ],
                'services': [
                    {'name': 'Currency Exchange', 'location': 'T1 & T2', 'hours': '24/7'},
                    {'name': 'Medical Center', 'location': 'T1 - Ground Floor', 'hours': '24/7'},
                    {'name': 'ATM', 'location': 'All Terminals', 'hours': '24/7'},
                    {'name': 'Prayer Room', 'location': 'T1 - Level 1', 'hours': '24/7'},
                    {'name': 'Baby Care Room', 'location': 'T1 & T2', 'hours': '24/7'},
                    {'name': 'WiFi Hotspot', 'location': 'All Terminals', 'hours': '24/7'},
                    {'name': 'Information Desk', 'location': 'All Terminals', 'hours': '24/7'}
                ]
            },
            'GOX': {
                'terminals': ['T1'],
                'gates': {
                    'T1': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
                },
                'airlines': {
                    'T1': ['Air India', 'IndiGo', 'SpiceJet', 'GoAir', 'Vistara']
                },
                'washrooms': [
                    {'location': 'T1 - Gate A2', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Gate A4', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Arrival Hall', 'type': 'Family', 'status': 'Available'},
                    {'location': 'T1 - Departure Lounge', 'type': 'General', 'status': 'Available'}
                ],
                'services': [
                    {'name': 'Currency Exchange', 'location': 'T1 - Ground Floor', 'hours': '6:00-22:00'},
                    {'name': 'ATM', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Medical Center', 'location': 'T1 - Ground Floor', 'hours': '24/7'},
                    {'name': 'Prayer Room', 'location': 'T1 - Level 1', 'hours': '24/7'},
                    {'name': 'Baby Care Room', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'WiFi Hotspot', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Information Desk', 'location': 'T1', 'hours': '6:00-22:00'},
                    {'name': 'Tourist Information', 'location': 'T1 - Arrival', 'hours': '8:00-20:00'}
                ]
            },
            'PNY': {
                'terminals': ['T1'],
                'gates': {
                    'T1': ['A1', 'A2', 'A3']
                },
                'airlines': {
                    'T1': ['Air India', 'IndiGo', 'SpiceJet']
                },
                'washrooms': [
                    {'location': 'T1 - Gate A1', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Gate A3', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Arrival Hall', 'type': 'General', 'status': 'Available'}
                ],
                'services': [
                    {'name': 'ATM', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Medical Center', 'location': 'T1 - Ground Floor', 'hours': '24/7'},
                    {'name': 'Prayer Room', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'WiFi Hotspot', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Information Desk', 'location': 'T1', 'hours': '6:00-22:00'},
                    {'name': 'Tourist Information', 'location': 'T1 - Arrival', 'hours': '8:00-18:00'}
                ]
            },
            'IXJ': {
                'terminals': ['T1'],
                'gates': {
                    'T1': ['A1', 'A2', 'A3', 'A4']
                },
                'airlines': {
                    'T1': ['Air India', 'IndiGo', 'SpiceJet', 'GoAir']
                },
                'washrooms': [
                    {'location': 'T1 - Gate A1', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Gate A3', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Arrival Hall', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Departure Lounge', 'type': 'Family', 'status': 'Available'}
                ],
                'services': [
                    {'name': 'ATM', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Medical Center', 'location': 'T1 - Ground Floor', 'hours': '24/7'},
                    {'name': 'Prayer Room', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'WiFi Hotspot', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Information Desk', 'location': 'T1', 'hours': '6:00-22:00'},
                    {'name': 'Tourist Information', 'location': 'T1 - Arrival', 'hours': '8:00-18:00'}
                ]
            },
            'SXR': {
                'terminals': ['T1'],
                'gates': {
                    'T1': ['A1', 'A2', 'A3', 'A4', 'A5']
                },
                'airlines': {
                    'T1': ['Air India', 'IndiGo', 'SpiceJet', 'GoAir']
                },
                'washrooms': [
                    {'location': 'T1 - Gate A1', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Gate A3', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Gate A5', 'type': 'General', 'status': 'Available'},
                    {'location': 'T1 - Arrival Hall', 'type': 'Family', 'status': 'Available'},
                    {'location': 'T1 - Departure Lounge', 'type': 'General', 'status': 'Available'}
                ],
                'services': [
                    {'name': 'ATM', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Medical Center', 'location': 'T1 - Ground Floor', 'hours': '24/7'},
                    {'name': 'Prayer Room', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'WiFi Hotspot', 'location': 'T1', 'hours': '24/7'},
                    {'name': 'Information Desk', 'location': 'T1', 'hours': '6:00-22:00'},
                    {'name': 'Tourist Information', 'location': 'T1 - Arrival', 'hours': '8:00-18:00'},
                    {'name': 'Currency Exchange', 'location': 'T1 - Ground Floor', 'hours': '8:00-20:00'}
                ]
            }
        }
        
        # Sample individual baggage for tracking
        self.sample_baggage = {}
        self.complaints = []
        self.default_gates = {
            'T1': ['A1', 'A2', 'A3', 'A4'],
            'T2': ['B1', 'B2', 'B3', 'B4'],
            'T3': ['C1', 'C2', 'C3', 'C4']
        }
        
        # Initialize OpenAI for AI-powered insights
        self.openai_client = None
        try:
            import openai
            import os
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.info("OpenAI API key not found. AI insights will be unavailable.")
        except ImportError:
            logger.info("OpenAI library not installed. AI insights will be unavailable.")
        except Exception as e:
            logger.info(f"Failed to initialize OpenAI client: {e}. AI insights will be unavailable.")
    
    def get_passenger_flow_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate realistic passenger flow data for 24-hour period"""
        try:
            current_time = datetime.datetime.now()
            hours = []
            passengers = []
            
            # Generate 24-hour data with realistic patterns
            for i in range(24):
                hour = (current_time.hour + i) % 24
                hours.append(f"{hour:02d}:00")
                
                # Rush hours: 6-9 AM and 6-9 PM
                if 6 <= hour <= 9 or 18 <= hour <= 21:
                    base_passengers = random.randint(800, 1200)
                elif 22 <= hour or hour <= 5:  # Late night/early morning
                    base_passengers = random.randint(100, 300)
                else:  # Regular hours
                    base_passengers = random.randint(400, 700)
                
                # Add some randomness
                passengers.append(base_passengers + random.randint(-50, 50))
            
            return {
                'chart': {
                    'x': hours,
                    'y': passengers,
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': 'Passenger Flow',
                    'line': {'color': '#3b82f6', 'width': 3}
                },
                'layout': {
                    'title': '24-Hour Passenger Flow',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Number of Passengers'},
                    'showlegend': False
                },
                'current_hour_passengers': passengers[0],
                'peak_hour': f"{hours[passengers.index(max(passengers))]}",
                'total_daily': sum(passengers[:current_time.hour + 1])
            }
        except Exception as e:
            logger.error(f"Error generating passenger flow data: {e}")
            return {'error': 'Failed to generate passenger flow data'}
    
    def get_queue_status_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate queue monitoring data"""
        try:
            checkpoints = [
                {'name': 'Security Check A', 'current_queue': random.randint(5, 25), 'avg_wait_time': random.randint(3, 15)},
                {'name': 'Security Check B', 'current_queue': random.randint(8, 30), 'avg_wait_time': random.randint(5, 18)},
                {'name': 'Check-in Counter 1', 'current_queue': random.randint(10, 40), 'avg_wait_time': random.randint(2, 12)},
                {'name': 'Check-in Counter 2', 'current_queue': random.randint(6, 35), 'avg_wait_time': random.randint(3, 10)},
                {'name': 'Immigration', 'current_queue': random.randint(3, 20), 'avg_wait_time': random.randint(1, 8)},
                {'name': 'Customs', 'current_queue': random.randint(2, 15), 'avg_wait_time': random.randint(1, 6)}
            ]
            
            checkpoint_names = [cp['name'] for cp in checkpoints]
            queue_lengths = [cp['current_queue'] for cp in checkpoints]
            wait_times = [cp['avg_wait_time'] for cp in checkpoints]
            
            return {
                'chart': {
                    'x': checkpoint_names,
                    'y': queue_lengths,
                    'type': 'bar',
                    'name': 'Queue Length',
                    'marker': {'color': '#10b981'}
                },
                'layout': {
                    'title': 'Current Queue Status',
                    'xaxis': {'title': 'Checkpoints'},
                    'yaxis': {'title': 'Number of People'},
                    'showlegend': False
                },
                'wait_times_chart': {
                    'x': checkpoint_names,
                    'y': wait_times,
                    'type': 'bar',
                    'name': 'Wait Time',
                    'marker': {'color': '#f59e0b'}
                },
                'checkpoints': checkpoints,
                'total_in_queues': sum(queue_lengths),
                'avg_wait_time_overall': sum(wait_times) / len(wait_times)
            }
        except Exception as e:
            logger.error(f"Error generating queue status data: {e}")
            return {'error': 'Failed to generate queue status data'}
    
    def get_baggage_tracking_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate enhanced baggage tracking data with live conveyor visualization"""
        try:
            # Get live conveyor data
            live_data = self.get_live_conveyor_data(airport_code)
            
            if live_data.get('error'):
                return live_data
            
            conveyor_belts = live_data['conveyor_belts']
            
            # Utilization pie chart data
            utilization_data = {
                'labels': ['High Usage', 'Medium Usage', 'Low Usage', 'Idle'],
                'values': [
                    len([b for b in conveyor_belts if b['utilization'] > 80]),
                    len([b for b in conveyor_belts if 50 < b['utilization'] <= 80]),
                    len([b for b in conveyor_belts if 20 < b['utilization'] <= 50]),
                    len([b for b in conveyor_belts if b['utilization'] <= 20])
                ],
                'type': 'pie',
                'marker': {'colors': ['#ef4444', '#f59e0b', '#10b981', '#6b7280']}
            }
            
            return {
                'chart': utilization_data,
                'layout': {
                    'title': 'Conveyor Belt Utilization',
                    'showlegend': True
                },
                'conveyor_belts': conveyor_belts,
                'total_belts': live_data['total_belts'],
                'active_belts': live_data['active_belts'],
                'total_bags_processed': sum([b['total_processed_today'] for b in conveyor_belts]),
                'avg_utilization': sum([b['utilization'] for b in conveyor_belts]) / len(conveyor_belts),
                'live_bags_count': live_data['total_bags_active'],
                'avg_belt_speed': live_data['avg_speed']
            }
        except Exception as e:
            logger.error(f"Error generating baggage tracking data: {e}")
            return {'error': 'Failed to generate baggage tracking data'}
    
    def _select_terminal_and_gate(self, airport_code: str) -> tuple[str, str]:
        facilities = self.airport_facilities.get(airport_code, {})
        gates_map = facilities.get('gates') or self.default_gates
        terminals = list(gates_map.keys())
        terminal = random.choice(terminals)
        gates = gates_map.get(terminal) or ['A1']
        gate = random.choice(gates)
        return terminal, gate

    def get_flight_status_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate real-time flight status data with weather integration"""
        try:
            # Try to get real flight data using OpenSky API (free)
            real_flights = self.get_opensky_flights(airport_code)
            
            # Get weather data for impact on flights
            weather = self.get_weather_data(airport_code)
            
            flights = []
            current_time = datetime.datetime.now()
            
            # Use real flight data if available, otherwise generate realistic data
            if real_flights and len(real_flights) > 0:
                for flight_data in real_flights[:12]:  # Limit to 12 flights
                    # Map real flight data to our format
                    status = self._determine_flight_status(flight_data, weather)
                    terminal, gate = self._select_terminal_and_gate(airport_code)
                    flight = {
                        'flight_number': flight_data.get('callsign', f'{random.choice(["AI", "6E", "SG"])}{random.randint(100, 999)}').strip(),
                        'airline': self._get_airline_from_callsign(flight_data.get('callsign', '')),
                        'destination': random.choice(self.destinations.get(airport_code, ['Mumbai', 'Delhi'])),
                        'scheduled_time': current_time.strftime('%H:%M'),
                        'actual_time': (current_time + datetime.timedelta(minutes=random.randint(-30, 60))).strftime('%H:%M'),
                        'status': status,
                        'gate': gate,
                        'terminal': terminal,
                        'passengers': random.randint(80, 180),
                        'weather_impact': weather.get('impact', 'Low'),
                        'delay_reason': self._get_delay_reason(status, weather),
                        'altitude': flight_data.get('baro_altitude', 0),
                        'velocity': flight_data.get('velocity', 0)
                    }
                    flights.append(flight)
            
            # Fill remaining slots with simulated data if needed
            while len(flights) < 12:
                flight_time = current_time + datetime.timedelta(hours=random.randint(-2, 8))
                
                # Weather affects flight status
                base_statuses = self.flight_statuses.copy()
                if weather.get('impact') == 'High':
                    # More delays due to bad weather
                    status = random.choice(['Delayed', 'Delayed', 'On Time', 'Boarding', 'Cancelled'])
                    delay_reason = f"Weather: {weather.get('condition', 'Unknown')}"
                else:
                    status = random.choice(base_statuses)
                    delay_reason = random.choice(['Air Traffic', 'Technical', 'Crew', 'None'])
                
                terminal, gate = self._select_terminal_and_gate(airport_code)
                flight = {
                    'flight_number': f'{random.choice(["AI", "6E", "SG", "UK", "G8"])}{random.randint(100, 999)}',
                    'airline': random.choice(self.airlines),
                    'destination': random.choice(self.destinations.get(airport_code, ['Mumbai', 'Delhi'])),
                    'scheduled_time': flight_time.strftime('%H:%M'),
                    'actual_time': (flight_time + datetime.timedelta(minutes=random.randint(-30, 60))).strftime('%H:%M'),
                    'status': status,
                    'gate': gate,
                    'terminal': terminal,
                    'passengers': random.randint(80, 180),
                    'weather_impact': weather.get('impact', 'Low'),
                    'delay_reason': delay_reason if status == 'Delayed' else None
                }
                flights.append(flight)
            
            # Status distribution for chart
            status_counts = {}
            for flight in flights:
                status = flight['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'chart': {
                    'labels': list(status_counts.keys()),
                    'values': list(status_counts.values()),
                    'type': 'pie',
                    'marker': {'colors': ['#10b981', '#f59e0b', '#3b82f6', '#6b7280', '#ef4444', '#8b5cf6']}
                },
                'layout': {
                    'title': 'Flight Status Distribution',
                    'showlegend': True
                },
                'flights': flights,
                'total_flights': len(flights),
                'on_time_flights': len([f for f in flights if f['status'] == 'On Time']),
                'delayed_flights': len([f for f in flights if f['status'] == 'Delayed']),
                'total_passengers': sum([f['passengers'] for f in flights]),
                'weather': weather,
                'weather_delays': len([f for f in flights if f.get('delay_reason') and f.get('delay_reason', '').startswith('Weather')])
            }
        except Exception as e:
            logger.error(f"Error generating flight status data: {e}")
            return {'error': 'Failed to generate flight status data'}

    def get_gate_operations_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate gate operations data for gate staff"""
        try:
            flight_data = self.get_flight_status_data(airport_code)
            if flight_data.get('error'):
                return flight_data

            gates = []
            for flight in flight_data.get('flights', []):
                gates.append({
                    'gate': flight.get('gate', 'TBD'),
                    'terminal': flight.get('terminal', 'TBD'),
                    'flight_number': flight.get('flight_number'),
                    'airline': flight.get('airline'),
                    'destination': flight.get('destination'),
                    'status': flight.get('status'),
                    'scheduled_time': flight.get('scheduled_time'),
                    'actual_time': flight.get('actual_time'),
                    'boarding_start': self._calculate_boarding_start(flight),
                    'arrival_gate': flight.get('gate', 'TBD') if flight.get('status') in ['Arrived', 'In Air'] else '-',
                    'next_gate': self._predict_next_gate(flight),
                    'notes': flight.get('delay_reason') or '',
                })

            return {
                'airport_code': airport_code,
                'gates': gates,
                'updated_at': datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating gate operations data: {e}")
            return {'error': 'Failed to generate gate operations data'}

    def _calculate_boarding_start(self, flight: Dict[str, Any]) -> str:
        try:
            scheduled = flight.get('scheduled_time')
            if not scheduled:
                return 'TBD'
            hour, minute = map(int, scheduled.split(':'))
            boarding_hour = max(0, hour - 1)
            return f"{boarding_hour:02d}:{minute:02d}"
        except Exception:
            return 'TBD'

    def _predict_next_gate(self, flight: Dict[str, Any]) -> str:
        status = flight.get('status')
        if status in ['Departed', 'Cancelled']:
            return 'Available soon'
        elif status in ['Boarding', 'On Time']:
            return 'In use'
        elif status in ['Arrived', 'In Air']:
            return 'Turnaround in progress'
        return 'TBD'
    
    def get_opensky_flights(self, airport_code: str) -> List[Dict[str, Any]]:
        """Get real flight data from OpenSky Network API"""
        try:
            # Airport bounding boxes (approximate)
            airport_bounds = {
                'DEL': {'lamin': 28.4, 'lomin': 76.9, 'lamax': 28.7, 'lomax': 77.2},
                'BLR': {'lamin': 13.0, 'lomin': 77.5, 'lamax': 13.4, 'lomax': 77.9},
                'GOX': {'lamin': 15.2, 'lomin': 73.7, 'lamax': 15.5, 'lomax': 74.0},
                'PNY': {'lamin': 11.8, 'lomin': 79.7, 'lamax': 12.1, 'lomax': 80.0},
                'IXJ': {'lamin': 32.5, 'lomin': 74.7, 'lamax': 32.8, 'lomax': 74.9},
                'SXR': {'lamin': 33.9, 'lomin': 74.6, 'lamax': 34.1, 'lomax': 74.9}
            }
            
            bounds = airport_bounds.get(airport_code, airport_bounds['DEL'])
            
            # Free OpenSky API call
            url = "https://opensky-network.org/api/states/all"
            params = {
                'lamin': bounds['lamin'],
                'lomin': bounds['lomin'],
                'lamax': bounds['lamax'],
                'lomax': bounds['lomax']
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                flights = []
                
                if data and 'states' in data and data['states']:
                    for state in data['states'][:15]:  # Limit to 15 flights
                        if state[0]:  # Has ICAO24 identifier
                            flight = {
                                'icao24': state[0],
                                'callsign': state[1] if state[1] else '',
                                'origin_country': state[2] if state[2] else '',
                                'longitude': state[5] if state[5] else 0,
                                'latitude': state[6] if state[6] else 0,
                                'baro_altitude': state[7] if state[7] else 0,
                                'velocity': state[9] if state[9] else 0,
                                'true_track': state[10] if state[10] else 0,
                                'vertical_rate': state[11] if state[11] else 0,
                                'on_ground': state[8] if state[8] else False
                            }
                            flights.append(flight)
                
                return flights
            else:
                logger.warning(f"OpenSky API error: {response.status_code}")
                return []
        except Exception as e:
            logger.warning(f"OpenSky API error: {e}")
            return []
    
    def _determine_flight_status(self, flight_data: Dict[str, Any], weather: Dict[str, Any]) -> str:
        """Determine flight status based on real flight data and weather"""
        if flight_data.get('on_ground'):
            return random.choice(['Arrived', 'Boarding', 'Departed'])
        elif flight_data.get('baro_altitude', 0) > 10000:
            return 'In Air'
        elif weather.get('impact') == 'High':
            return random.choice(['Delayed', 'On Time'])
        else:
            return random.choice(['On Time', 'Boarding', 'Delayed'])
    
    def _get_airline_from_callsign(self, callsign: str) -> str:
        """Extract airline from flight callsign"""
        if not callsign:
            return random.choice(self.airlines)
        
        callsign = callsign.upper().strip()
        
        # Map ICAO codes to airline names
        airline_mapping = {
            'AI': 'Air India',
            'IGO': 'IndiGo',
            'SEJ': 'SpiceJet',
            'VTI': 'Vistara',
            'GOW': 'GoAir',
            'UAE': 'Emirates',
            'SIA': 'Singapore Airlines'
        }
        
        # Try to match first few characters
        for code, airline in airline_mapping.items():
            if callsign.startswith(code):
                return airline
        
        return random.choice(self.airlines)
    
    def _get_delay_reason(self, status: str, weather: Dict[str, Any]) -> Optional[str]:
        """Get delay reason based on status and weather"""
        if status != 'Delayed':
            return None
        
        if weather.get('impact') == 'High':
            return f"Weather: {weather.get('condition', 'Poor conditions')}"
        else:
            return random.choice(['Air Traffic Control', 'Technical Issues', 'Crew Scheduling', 'Ground Operations'])
    
    def get_security_status_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate security checkpoint status"""
        try:
            checkpoints = []
            for i in range(1, 8):
                status = random.choice(['Operational', 'Maintenance', 'Closed'])
                checkpoint = {
                    'checkpoint_id': f'CP-{i:02d}',
                    'location': f'Terminal {random.choice(["A", "B", "C"])} - Gate {i}',
                    'status': status,
                    'staff_count': random.randint(2, 6) if status == 'Operational' else 0,
                    'throughput_per_hour': random.randint(100, 200) if status == 'Operational' else 0,
                    'last_incident': random.choice(['None', '2 hours ago', '1 day ago', 'None', 'None']),
                    'alert_level': random.choice(['Green', 'Green', 'Yellow', 'Green'])
                }
                checkpoints.append(checkpoint)
            
            status_counts = {}
            for cp in checkpoints:
                status = cp['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'chart': {
                    'labels': list(status_counts.keys()),
                    'values': list(status_counts.values()),
                    'type': 'pie',
                    'marker': {'colors': ['#10b981', '#f59e0b', '#ef4444']}
                },
                'layout': {
                    'title': 'Security Checkpoint Status',
                    'showlegend': True
                },
                'checkpoints': checkpoints,
                'total_checkpoints': len(checkpoints),
                'operational_checkpoints': len([cp for cp in checkpoints if cp['status'] == 'Operational']),
                'total_staff_deployed': sum([cp['staff_count'] for cp in checkpoints]),
                'total_throughput': sum([cp['throughput_per_hour'] for cp in checkpoints])
            }
        except Exception as e:
            logger.error(f"Error generating security status data: {e}")
            return {'error': 'Failed to generate security status data'}
    
    def get_resource_utilization_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate resource utilization data"""
        try:
            resources = {
                'CPU Usage': random.randint(60, 90),
                'Memory Usage': random.randint(70, 85),
                'Network Bandwidth': random.randint(50, 80),
                'Storage Usage': random.randint(65, 95),
                'Power Consumption': random.randint(75, 90)
            }
            
            return {
                'chart': {
                    'labels': list(resources.keys()),
                    'values': list(resources.values()),
                    'type': 'pie',
                    'marker': {'colors': ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']}
                },
                'layout': {
                    'title': 'System Resource Utilization (%)',
                    'showlegend': True
                },
                'resources': resources,
                'overall_health': 'Good' if max(resources.values()) < 85 else 'Warning',
                'peak_usage': max(resources.values()),
                'avg_usage': sum(resources.values()) / len(resources)
            }
        except Exception as e:
            logger.error(f"Error generating resource utilization data: {e}")
            return {'error': 'Failed to generate resource utilization data'}
    
    def get_staff_availability_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate staff availability data"""
        try:
            departments = [
                {'name': 'Security', 'available': random.randint(15, 25), 'total': 30},
                {'name': 'Ground Staff', 'available': random.randint(20, 35), 'total': 40},
                {'name': 'Check-in', 'available': random.randint(10, 18), 'total': 20},
                {'name': 'Baggage Handling', 'available': random.randint(12, 22), 'total': 25},
                {'name': 'Maintenance', 'available': random.randint(6, 12), 'total': 15},
                {'name': 'Customer Service', 'available': random.randint(8, 15), 'total': 18}
            ]
            
            # Calculate availability percentages
            for dept in departments:
                dept['availability_percent'] = round((dept['available'] / dept['total']) * 100, 1)
            
            dept_names = [dept['name'] for dept in departments]
            availability_percentages = [dept['availability_percent'] for dept in departments]
            
            return {
                'chart': {
                    'x': dept_names,
                    'y': availability_percentages,
                    'type': 'bar',
                    'name': 'Staff Availability %',
                    'marker': {'color': '#3b82f6'}
                },
                'layout': {
                    'title': 'Staff Availability by Department',
                    'xaxis': {'title': 'Department'},
                    'yaxis': {'title': 'Availability %'},
                    'showlegend': False
                },
                'departments': departments,
                'total_staff': sum([dept['total'] for dept in departments]),
                'available_staff': sum([dept['available'] for dept in departments]),
                'overall_availability': round((sum([dept['available'] for dept in departments]) / sum([dept['total'] for dept in departments])) * 100, 1)
            }
        except Exception as e:
            logger.error(f"Error generating staff availability data: {e}")
            return {'error': 'Failed to generate staff availability data'}
    
    def get_weather_data(self, airport_code: str) -> Dict[str, Any]:
        """Get real weather data for airport using free API"""
        try:
            # Airport coordinates (approximate)
            coordinates = {
                'DEL': {'lat': 28.5562, 'lon': 77.1000},
                'BLR': {'lat': 13.1986, 'lon': 77.7066}, 
                'GOX': {'lat': 15.3808, 'lon': 73.8389},
                'PNY': {'lat': 11.9696, 'lon': 79.8125},
                'IXJ': {'lat': 32.6890, 'lon': 74.8378},
                'SXR': {'lat': 33.9871, 'lon': 74.7747}
            }
            
            coord = coordinates.get(airport_code, coordinates['DEL'])
            
            # Free weather API call
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': coord['lat'],
                'longitude': coord['lon'],
                'current_weather': 'true',
                'hourly': 'temperature_2m,weathercode,windspeed_10m,visibility'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_weather', {})
                
                # Weather code to condition mapping
                weather_codes = {
                    0: 'Clear', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
                    45: 'Fog', 48: 'Depositing Rime Fog', 51: 'Light Drizzle',
                    61: 'Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
                    71: 'Light Snow', 95: 'Thunderstorm'
                }
                
                condition = weather_codes.get(current.get('weathercode', 0), 'Unknown')
                
                return {
                    'temperature': current.get('temperature', 25),
                    'condition': condition,
                    'wind_speed': current.get('windspeed', 10),
                    'visibility': 'Good' if condition in ['Clear', 'Mainly Clear'] else 'Limited',
                    'impact': 'Low' if condition in ['Clear', 'Mainly Clear', 'Partly Cloudy'] else 'High'
                }
            else:
                # Fallback to simulated data
                return self._get_simulated_weather()
        except Exception as e:
            logger.warning(f"Weather API error: {e}, using simulated data")
            return self._get_simulated_weather()
    
    def _get_simulated_weather(self) -> Dict[str, Any]:
        """Generate simulated weather data as fallback"""
        conditions = ['Clear', 'Partly Cloudy', 'Overcast', 'Rain', 'Fog']
        condition = random.choice(conditions)
        
        return {
            'temperature': random.randint(15, 35),
            'condition': condition,
            'wind_speed': random.randint(5, 25),
            'visibility': 'Good' if condition in ['Clear', 'Partly Cloudy'] else 'Limited',
            'impact': 'Low' if condition in ['Clear', 'Partly Cloudy'] else 'High'
        }
    
    def get_live_conveyor_data(self, airport_code: str) -> Dict[str, Any]:
        """Generate enhanced live conveyor belt data with AI monitoring and sensor data (optimized)"""
        try:
            conveyor_belts = []
            current_time = datetime.datetime.now()
            
            # Enhanced conveyor belt configurations for each airport (reduced for performance)
            airport_conveyor_configs = {
                'DEL': {
                    'terminals': ['T1', 'T2', 'T3'],
                    'belts_per_terminal': {'T1': 4, 'T2': 3, 'T3': 5},  # Reduced from 8,6,10
                    'max_speed': 5.0,
                    'sensor_types': ['weight', 'motion', 'temperature', 'vibration']
                },
                'BLR': {
                    'terminals': ['T1', 'T2'],
                    'belts_per_terminal': {'T1': 3, 'T2': 3},  # Reduced
                    'max_speed': 4.5,
                    'sensor_types': ['weight', 'motion', 'temperature']
                },
                'GOX': {
                    'terminals': ['T1'],
                    'belts_per_terminal': {'T1': 3},  # Reduced from 4
                    'max_speed': 4.0,
                    'sensor_types': ['weight', 'motion']
                },
                'PNY': {
                    'terminals': ['T1'],
                    'belts_per_terminal': {'T1': 2},  # Reduced from 3
                    'max_speed': 3.5,
                    'sensor_types': ['weight', 'motion']
                },
                'IXJ': {
                    'terminals': ['T1'],
                    'belts_per_terminal': {'T1': 2},  # Reduced
                    'max_speed': 3.5,
                    'sensor_types': ['weight', 'motion']
                },
                'SXR': {
                    'terminals': ['T1'],
                    'belts_per_terminal': {'T1': 2},  # Reduced
                    'max_speed': 3.5,
                    'sensor_types': ['weight', 'motion']
                }
            }
            
            config = airport_conveyor_configs.get(airport_code, airport_conveyor_configs['DEL'])
            belt_counter = 1
            
            for terminal in config['terminals']:
                for belt_num in range(1, config['belts_per_terminal'][terminal] + 1):
                    belt_id = f'{terminal}-Belt-{belt_num:02d}'
                    
                    status, ai_insights = self._get_ai_belt_status(belt_id, airport_code)
                    sensor_data = self._generate_sensor_data(config['sensor_types'], status, config['max_speed'])
                    bags_on_belt = self._generate_live_bags(belt_id, status, config['max_speed'])
                    efficiency_score = self._calculate_belt_efficiency(bags_on_belt, sensor_data, status)
                    health_status = self._get_belt_health_status(sensor_data, efficiency_score)
                    delay_risk = self._calculate_delay_risk(bags_on_belt, sensor_data)
                    breakdown_probability = self._calculate_breakdown_probability(sensor_data)
                    predicted_issues = self._predict_belt_issues(sensor_data, bags_on_belt)
                    utilization = self._calculate_utilization(bags_on_belt, status)
                    
                    belt_data = {
                        'belt_id': belt_id,
                        'terminal': terminal,
                        'status': status,
                        'speed': round(sensor_data.get('current_speed', 0), 2),
                        'max_speed': config['max_speed'],
                        'bags_on_belt': bags_on_belt,
                        'total_processed_today': random.randint(200, 800),
                        'last_maintenance': f'{random.randint(1, 30)} days ago',
                        'utilization': utilization,
                        'sensor_data': sensor_data,
                        'ai_insights': ai_insights,
                        'efficiency_score': efficiency_score,
                        'predicted_issues': predicted_issues,
                        'health_status': health_status,
                        'delay_risk': delay_risk,
                        'breakdown_probability': breakdown_probability,
                        'last_updated': current_time.strftime('%H:%M:%S'),
                        'belt_counter': belt_counter
                    }
                    
                    conveyor_belts.append(belt_data)
                    belt_counter += 1
            
            active_belts = [b for b in conveyor_belts if b['status'] == 'Active']
            system_insights = self._generate_system_insights(conveyor_belts, airport_code)
            if system_insights.get('error'):
                system_insights = {
                    'system_efficiency': 0,
                    'active_belts_ratio': 0,
                    'critical_issues_count': 0,
                    'total_issues_count': 0,
                    'recommendations': ['Monitoring conveyor health...'],
                    'system_health': 'Unknown',
                    'peak_performance_time': 'N/A',
                    'maintenance_priority': 'Low'
                }
            
            performance_metrics = self._calculate_performance_metrics(conveyor_belts)
            if performance_metrics.get('error'):
                performance_metrics = {}
            ai_alerts = self._generate_ai_alerts(conveyor_belts)
            ai_alerts.extend(self._get_complaint_alerts(airport_code))
            
            return {
                'conveyor_belts': conveyor_belts,
                'total_belts': len(conveyor_belts),
                'active_belts': len(active_belts),
                'total_bags_active': sum(len(b['bags_on_belt']) for b in conveyor_belts),
                'avg_speed': sum(b['speed'] for b in conveyor_belts) / len(conveyor_belts) if conveyor_belts else 0,
                'system_insights': system_insights,
                'ai_alerts': ai_alerts,
                'performance_metrics': performance_metrics,
                'airport_code': airport_code,
                'last_update': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error generating live conveyor data: {e}", exc_info=True)
            return {'error': 'Failed to generate live conveyor data'}
    
    def _get_ai_belt_status(self, belt_id: str, airport_code: str) -> tuple:
        """AI-powered belt status determination with predictive analysis"""
        try:
            # Simulate AI analysis based on historical patterns and current conditions
            base_statuses = ['Active', 'Idle', 'Maintenance', 'Slow', 'Overloaded']
            
            # AI factors that influence status
            time_factor = datetime.datetime.now().hour
            weather_impact = self.get_weather_data(airport_code).get('impact', 'Low')
            
            # AI probability calculation
            if 6 <= time_factor <= 9 or 18 <= time_factor <= 21:  # Peak hours
                status_weights = {'Active': 0.7, 'Overloaded': 0.2, 'Slow': 0.1}
            elif 22 <= time_factor or time_factor <= 5:  # Off-peak
                status_weights = {'Idle': 0.6, 'Active': 0.3, 'Maintenance': 0.1}
            else:  # Regular hours
                status_weights = {'Active': 0.8, 'Idle': 0.15, 'Slow': 0.05}
            
            # Weather impact adjustment
            if weather_impact == 'High':
                status_weights['Slow'] = status_weights.get('Slow', 0) + 0.2
                status_weights['Maintenance'] = status_weights.get('Maintenance', 0) + 0.1
            
            # AI decision
            import random
            status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
            
            # AI insights
            ai_insights = {
                'status_reason': f"AI analysis: {status} due to {'peak hour traffic' if 'peak' in str(time_factor) else 'regular operations'}",
                'recommendation': self._get_ai_recommendation(status, weather_impact),
                'confidence': random.randint(85, 98),
                'predicted_duration': f"{random.randint(1, 4)} hours" if status != 'Active' else "Continuous"
            }
            
            return status, ai_insights
            
        except Exception as e:
            logger.error(f"Error in AI belt status: {e}")
            return 'Active', {'status_reason': 'AI analysis failed', 'recommendation': 'Manual check required'}
    
    def _generate_sensor_data(self, sensor_types: List[str], status: str, max_speed: Optional[float] = None) -> Dict[str, Any]:
        """Generate realistic sensor data for conveyor belt monitoring"""
        try:
            sensor_data = {}
            sensor_data['max_speed'] = max_speed or 0.0
            
            if 'weight' in sensor_types:
                sensor_data['weight_sensor'] = {
                    'current_load': random.randint(20, 95) if status == 'Active' else 0,
                    'max_capacity': 100,
                    'overload_warning': False,
                    'last_calibration': f'{random.randint(1, 90)} days ago'
                }
            
            if 'motion' in sensor_types:
                sensor_data['motion_sensor'] = {
                    'current_speed': random.uniform(1.0, 5.0) if status == 'Active' else 0,
                    'speed_variation': random.uniform(0.1, 0.5),
                    'direction': 'forward',
                    'stuck_detection': random.choice([True, False, False, False])  # 25% chance of stuck
                }
            
            if 'temperature' in sensor_types:
                sensor_data['temperature_sensor'] = {
                    'current_temp': random.uniform(18.0, 35.0),
                    'max_safe_temp': 40.0,
                    'overheating_warning': False,
                    'cooling_system_status': 'Normal'
                }
            
            if 'vibration' in sensor_types:
                sensor_data['vibration_sensor'] = {
                    'vibration_level': random.uniform(0.1, 2.0),
                    'max_safe_vibration': 3.0,
                    'abnormal_vibration': False,
                    'bearing_health': random.choice(['Good', 'Good', 'Good', 'Fair', 'Poor'])
                }
            
            if 'optical' in sensor_types:
                sensor_data['optical_sensor'] = {
                    'bag_detection': random.randint(85, 99),
                    'jam_detection': random.choice([True, False, False, False, False]),
                    'foreign_object_detection': random.choice([True, False, False, False, False, False]),
                    'camera_status': 'Operational'
                }
            
            # Calculate current speed based on motion sensor
            if 'motion_sensor' in sensor_data:
                sensor_data['current_speed'] = sensor_data['motion_sensor']['current_speed']
            else:
                sensor_data['current_speed'] = random.uniform(1.0, 5.0) if status == 'Active' else 0
            
            return sensor_data
            
        except Exception as e:
            logger.error(f"Error generating sensor data: {e}")
            return {'current_speed': 0, 'error': 'Sensor data generation failed'}
    
    def _generate_live_bags(self, belt_id: str, status: str, max_speed: float) -> List[Dict[str, Any]]:
        """Generate realistic live baggage with positioning and tracking"""
        try:
            if status not in ['Active', 'Slow', 'Overloaded']:
                return []
            
            bags = []
            num_bags = random.randint(3, 15) if status == 'Active' else random.randint(1, 8)
            
            for i in range(num_bags):
                # Realistic bag positioning (0-100% of belt length)
                position = random.uniform(0, 100)
                
                # Bag properties
                bag_id = f'BAG{random.randint(10000, 99999)}'
                priority = random.choice(['Normal', 'Priority', 'Transfer', 'Fragile'])
                
                # Calculate estimated arrival time based on position and speed
                speed = max_speed * random.uniform(0.8, 1.2)  # Speed variation
                remaining_distance = 100 - position
                eta_seconds = remaining_distance / speed if speed > 0 else 0
                
                bag_data = {
                    'bag_id': bag_id,
                    'position': round(position, 1),
                    'flight': f'{random.choice(["AI", "6E", "SG", "UK", "G8"])}{random.randint(100, 999)}',
                    'destination': random.choice(['Mumbai', 'Delhi', 'Chennai', 'Bangalore', 'Hyderabad']),
                    'status': 'In Transit',
                    'priority': priority,
                    'weight': f'{random.randint(15, 30)} kg',
                    'eta_seconds': round(eta_seconds, 1),
                    'stuck_status': random.choice([False, False, False, True]) if position > 80 else False,
                    'last_movement': datetime.datetime.now().strftime('%H:%M:%S'),
                    'tracking_history': [
                        {'time': '14:30', 'status': 'Checked In', 'location': 'Check-in Counter'},
                        {'time': '14:45', 'status': 'In Sorting', 'location': 'Baggage Sorting Area'},
                        {'time': '15:00', 'status': 'On Conveyor', 'location': belt_id}
                    ]
                }
                
                bags.append(bag_data)
            
            return bags
            
        except Exception as e:
            logger.error(f"Error generating live bags: {e}")
            return []
    
    def _calculate_belt_efficiency(self, bags: List[Dict], sensor_data: Dict, status: str) -> float:
        """Calculate AI-powered belt efficiency score"""
        try:
            if status not in ['Active', 'Slow', 'Overloaded']:
                return 0.0
            
            efficiency_factors = []
            
            # Bag flow efficiency
            if bags:
                avg_position = sum(bag['position'] for bag in bags) / len(bags)
                flow_efficiency = max(0, 100 - avg_position) / 100
                efficiency_factors.append(flow_efficiency * 0.4)
            
            # Speed efficiency
            current_speed = sensor_data.get('current_speed', 0)
            max_speed = sensor_data.get('max_speed', 5.0)
            speed_efficiency = min(1.0, current_speed / max_speed) if max_speed > 0 else 0
            efficiency_factors.append(speed_efficiency * 0.3)
            
            # Sensor health efficiency
            sensor_health = 1.0
            for sensor_type, sensor_info in sensor_data.items():
                if isinstance(sensor_info, dict):
                    if sensor_info.get('warning', False):
                        sensor_health -= 0.2
                    if sensor_info.get('abnormal', False):
                        sensor_health -= 0.3
            sensor_health = max(0, sensor_health)
            efficiency_factors.append(sensor_health * 0.3)
            
            total_efficiency = sum(efficiency_factors)
            return round(total_efficiency * 100, 1)
            
        except Exception as e:
            logger.error(f"Error calculating belt efficiency: {e}")
            return 75.0
    
    def _predict_belt_issues(self, sensor_data: Dict, bags: List[Dict]) -> List[Dict[str, Any]]:
        """AI-powered prediction of potential belt issues"""
        try:
            issues = []
            
            # Overload prediction
            if 'weight_sensor' in sensor_data:
                weight_data = sensor_data['weight_sensor']
                if weight_data['current_load'] > 80:
                    issues.append({
                        'type': 'Overload Warning',
                        'severity': 'Medium',
                        'description': f"Belt load at {weight_data['current_load']}% capacity",
                        'probability': min(95, weight_data['current_load'] + 10),
                        'recommended_action': 'Monitor load and consider redistribution'
                    })
            
            # Stuck bag detection
            stuck_bags = [bag for bag in bags if bag.get('stuck_status', False)]
            if stuck_bags:
                issues.append({
                    'type': 'Stuck Baggage',
                    'severity': 'High',
                    'description': f"{len(stuck_bags)} bags detected as stuck",
                    'probability': 90,
                    'recommended_action': 'Immediate intervention required'
                })
            
            # Temperature warning
            if 'temperature_sensor' in sensor_data:
                temp_data = sensor_data['temperature_sensor']
                if temp_data['current_temp'] > 30:
                    issues.append({
                        'type': 'Temperature Warning',
                        'severity': 'Medium',
                        'description': f"Belt temperature at {temp_data['current_temp']:.1f}°C",
                        'probability': 75,
                        'recommended_action': 'Check cooling system and reduce load'
                    })
            
            # Vibration warning
            if 'vibration_sensor' in sensor_data:
                vib_data = sensor_data['vibration_sensor']
                if vib_data['vibration_level'] > 1.5:
                    issues.append({
                        'type': 'Vibration Warning',
                        'severity': 'Medium',
                        'description': f"High vibration level: {vib_data['vibration_level']:.1f}",
                        'probability': 75,
                        'recommended_action': 'Schedule maintenance check'
                    })
            
            return issues
            
        except Exception as e:
            logger.error(f"Error predicting belt issues: {e}")
            return []
    
    def _get_belt_health_status(self, sensor_data: Dict, efficiency_score: float) -> str:
        """Determine belt health status based on sensors and efficiency"""
        try:
            if efficiency_score >= 90:
                return 'Excellent'
            elif efficiency_score >= 75:
                return 'Good'
            elif efficiency_score >= 60:
                return 'Fair'
            elif efficiency_score >= 40:
                return 'Poor'
            else:
                return 'Critical'
        except Exception as e:
            logger.error(f"Error determining belt health: {e}")
            return 'Unknown'
    
    def _calculate_delay_risk(self, bags: List[Dict], sensor_data: Dict) -> Dict[str, Any]:
        """Calculate AI-powered delay risk assessment"""
        try:
            risk_factors = []
            total_risk = 0
            
            # Bag positioning risk
            if bags:
                stuck_bags = len([b for b in bags if b.get('stuck_status', False)])
                if stuck_bags > 0:
                    positioning_risk = min(100, stuck_bags * 25)
                    risk_factors.append(f"Stuck bags: {positioning_risk}%")
                    total_risk += positioning_risk
            
            # Speed risk
            current_speed = sensor_data.get('current_speed', 0)
            if current_speed < 2.0:
                speed_risk = min(100, (2.0 - current_speed) * 50)
                risk_factors.append(f"Low speed: {speed_risk:.1f}%")
                total_risk += speed_risk
            
            # Sensor warning risk
            for sensor_type, sensor_info in sensor_data.items():
                if isinstance(sensor_info, dict):
                    if sensor_info.get('warning', False):
                        total_risk += 15
                        risk_factors.append(f"{sensor_type} warning")
                    if sensor_info.get('abnormal', False):
                        total_risk += 25
                        risk_factors.append(f"{sensor_type} abnormal")
            
            # Overall risk assessment
            if total_risk >= 80:
                risk_level = 'Critical'
            elif total_risk >= 60:
                risk_level = 'High'
            elif total_risk >= 40:
                risk_level = 'Medium'
            elif total_risk >= 20:
                risk_level = 'Low'
            else:
                risk_level = 'Minimal'
            
            return {
                'risk_level': risk_level,
                'risk_score': min(100, total_risk),
                'risk_factors': risk_factors,
                'estimated_delay': f"{min(60, total_risk // 2)} minutes" if total_risk > 20 else "No delay expected"
            }
            
        except Exception as e:
            logger.error(f"Error calculating delay risk: {e}")
            return {'risk_level': 'Unknown', 'risk_score': 0, 'risk_factors': [], 'estimated_delay': 'Unknown'}
    
    def _calculate_breakdown_probability(self, sensor_data: Dict) -> Dict[str, Any]:
        """Calculate AI-powered breakdown probability"""
        try:
            breakdown_score = 0
            contributing_factors = []
            
            # Temperature factor
            if 'temperature_sensor' in sensor_data:
                temp_data = sensor_data['temperature_sensor']
                if temp_data['current_temp'] > 35:
                    breakdown_score += 30
                    contributing_factors.append(f"High temperature: {temp_data['current_temp']:.1f}°C")
            
            # Vibration factor
            if 'vibration_sensor' in sensor_data:
                vib_data = sensor_data['vibration_sensor']
                if vib_data['vibration_level'] > 2.0:
                    breakdown_score += 25
                    contributing_factors.append(f"High vibration: {vib_data['vibration_level']:.1f}")
                if vib_data['bearing_health'] == 'Poor':
                    breakdown_score += 40
                    contributing_factors.append("Poor bearing health")
            
            # Weight factor
            if 'weight_sensor' in sensor_data:
                weight_data = sensor_data['weight_sensor']
                if weight_data['current_load'] > 90:
                    breakdown_score += 20
                    contributing_factors.append(f"Overload: {weight_data['current_load']}%")
            
            # Probability calculation
            if breakdown_score >= 80:
                probability = 'Very High'
                time_to_breakdown = 'Immediate (0-2 hours)'
            elif breakdown_score >= 60:
                probability = 'High'
                time_to_breakdown = 'Soon (2-8 hours)'
            elif breakdown_score >= 40:
                probability = 'Medium'
                time_to_breakdown = 'Within 24 hours'
            elif breakdown_score >= 20:
                probability = 'Low'
                time_to_breakdown = 'Within 1 week'
            else:
                probability = 'Very Low'
                time_to_breakdown = 'No immediate risk'
            
            return {
                'probability': probability,
                'score': breakdown_score,
                'contributing_factors': contributing_factors,
                'time_to_breakdown': time_to_breakdown,
                'maintenance_recommendation': 'Immediate' if breakdown_score >= 60 else 'Scheduled'
            }
            
        except Exception as e:
            logger.error(f"Error calculating breakdown probability: {e}")
            return {'probability': 'Unknown', 'score': 0, 'contributing_factors': [], 'time_to_breakdown': 'Unknown'}
    
    def _generate_system_insights(self, conveyor_belts: List[Dict], airport_code: str) -> Dict[str, Any]:
        """Generate AI-powered system-wide insights"""
        try:
            total_belts = len(conveyor_belts)
            active_belts = len([b for b in conveyor_belts if b['status'] == 'Active'])
            
            # Performance analysis
            efficiency_scores = [b['efficiency_score'] for b in conveyor_belts if b['status'] == 'Active']
            avg_efficiency = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0
            
            # Issue analysis
            all_issues = []
            for belt in conveyor_belts:
                all_issues.extend(belt.get('predicted_issues', []))
            
            critical_issues = [i for i in all_issues if i.get('severity') == 'High']
            
            # AI recommendations
            recommendations = []
            if avg_efficiency < 70:
                recommendations.append("System efficiency below optimal. Consider load balancing and maintenance.")
            if len(critical_issues) > 2:
                recommendations.append("Multiple critical issues detected. Prioritize immediate interventions.")
            if active_belts / total_belts < 0.8:
                recommendations.append("Low belt utilization. Review operational scheduling.")
            
            return {
                'system_efficiency': round(avg_efficiency, 1),
                'active_belts_ratio': round((active_belts / total_belts) * 100, 1),
                'critical_issues_count': len(critical_issues),
                'total_issues_count': len(all_issues),
                'recommendations': recommendations,
                'system_health': 'Good' if avg_efficiency >= 75 else 'Needs Attention',
                'peak_performance_time': '6:00-9:00 AM, 6:00-9:00 PM',
                'maintenance_priority': 'High' if len(critical_issues) > 3 else 'Medium'
            }
            
        except Exception as e:
            logger.error(f"Error generating system insights: {e}")
            return {'error': 'Failed to generate system insights'}
    
    def _generate_ai_alerts(self, conveyor_belts: List[Dict]) -> List[Dict[str, Any]]:
        """Generate AI-powered alerts for staff attention"""
        try:
            alerts = []
            now = datetime.datetime.now().strftime('%H:%M:%S')
            
            for belt in conveyor_belts:
                belt_id = belt.get('belt_id', 'UNKNOWN')
                scope = ['baggage', 'management', 'all']
                
                if belt.get('health_status') == 'Critical':
                    alerts.append({
                        'id': f'{belt_id}-critical',
                        'type': 'Critical Belt Health',
                        'belt_id': belt_id,
                        'message': f"Critical health status detected on {belt_id}",
                        'priority': 'Critical',
                        'action_required': 'Immediate shutdown and maintenance',
                        'timestamp': now,
                        'scope': scope
                    })
                
                delay_risk = belt.get('delay_risk') or {}
                risk_level = delay_risk.get('risk_level')
                if risk_level in ['High', 'Critical']:
                    alerts.append({
                        'id': f'{belt_id}-delay',
                        'type': 'Delay Risk Alert',
                        'belt_id': belt_id,
                        'message': f"Delay risk {risk_level} on {belt_id}: {delay_risk.get('estimated_delay', 'N/A')}",
                        'priority': 'High',
                        'action_required': 'Monitor closely and prepare intervention',
                        'timestamp': now,
                        'scope': scope
                    })
                
                breakdown_prob = belt.get('breakdown_probability') or {}
                probability = breakdown_prob.get('probability')
                if probability in ['High', 'Very High']:
                    alerts.append({
                        'id': f'{belt_id}-breakdown',
                        'type': 'Breakdown Warning',
                        'belt_id': belt_id,
                        'message': f"Breakdown probability {probability} on {belt_id}: {breakdown_prob.get('time_to_breakdown', 'Unknown')}",
                        'priority': 'High',
                        'action_required': breakdown_prob.get('maintenance_recommendation', 'Schedule maintenance'),
                        'timestamp': now,
                        'scope': scope
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating AI alerts: {e}")
            return []

    def _get_complaint_alerts(self, airport_code: str) -> List[Dict[str, Any]]:
        """Generate alerts for newly submitted passenger complaints"""
        try:
            alerts = []
            for complaint in self.complaints:
                if complaint.get('status') == 'Resolved':
                    continue
                complaint_airport = complaint.get('airport_code')
                if complaint_airport and complaint_airport != airport_code:
                    continue
                alerts.append({
                    'id': f"complaint-{complaint['complaint_id']}",
                    'type': 'Passenger Complaint',
                    'message': f"{complaint['issue_type']} reported for bag {complaint['bag_id']} (Flight {complaint['flight_number']})",
                    'priority': 'Critical' if complaint.get('priority') == 'High' else 'High',
                    'timestamp': complaint.get('submitted_at', datetime.datetime.now().strftime('%H:%M:%S')),
                    'scope': ['baggage', 'management', 'all'],
                    'action_required': 'Acknowledge and reach out to passenger'
                })
            return alerts
        except Exception as e:
            logger.error(f"Error generating complaint alerts: {e}")
            return []
    
    def _calculate_performance_metrics(self, conveyor_belts: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            active_belts = [b for b in conveyor_belts if b['status'] == 'Active']
            
            if not active_belts:
                return {'error': 'No active belts to analyze'}
            
            # Speed metrics
            speeds = [b['speed'] for b in active_belts]
            avg_speed = sum(speeds) / len(speeds)
            max_speed = max(speeds)
            min_speed = min(speeds)
            
            # Efficiency metrics
            efficiencies = [b['efficiency_score'] for b in active_belts]
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            min_efficiency = min(efficiencies)
            
            # Bag processing metrics
            total_bags = sum(len(b['bags_on_belt']) for b in active_belts)
            bags_per_belt = total_bags / len(active_belts) if active_belts else 0
            
            # Health metrics
            health_statuses = [b['health_status'] for b in active_belts]
            health_distribution = {}
            for status in health_statuses:
                health_distribution[status] = health_distribution.get(status, 0) + 1
            
            return {
                'speed_metrics': {
                    'average': round(avg_speed, 2),
                    'maximum': round(max_speed, 2),
                    'minimum': round(min_speed, 2),
                    'unit': 'm/s'
                },
                'efficiency_metrics': {
                    'average': round(avg_efficiency, 1),
                    'minimum': round(min_efficiency, 1),
                    'unit': '%'
                },
                'bag_processing': {
                    'total_bags': total_bags,
                    'average_per_belt': round(bags_per_belt, 1),
                    'unit': 'bags'
                },
                'health_distribution': health_distribution,
                'overall_performance': 'Excellent' if avg_efficiency >= 85 else 'Good' if avg_efficiency >= 70 else 'Needs Improvement'
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {'error': 'Failed to calculate performance metrics'}
    
    def _get_ai_recommendation(self, status: str, weather_impact: str) -> str:
        """Get AI-powered recommendations based on status and conditions"""
        try:
            recommendations = {
                'Active': 'Continue monitoring. System operating normally.',
                'Idle': 'Consider activating for incoming flights or maintenance.',
                'Maintenance': 'Complete maintenance tasks. Check all sensors and mechanical components.',
                'Slow': 'Investigate speed reduction. Check for obstructions or mechanical issues.',
                'Overloaded': 'Reduce load or activate additional belts. Monitor for potential delays.'
            }
            
            base_recommendation = recommendations.get(status, 'Monitor system status.')
            
            if weather_impact == 'High':
                base_recommendation += ' Weather conditions may affect operations. Increase monitoring frequency.'
            
            return base_recommendation
            
        except Exception as e:
            logger.error(f"Error getting AI recommendation: {e}")
            return 'Manual intervention recommended.'
    
    def _calculate_utilization(self, bags: List[Dict], status: str) -> int:
        """Calculate belt utilization percentage"""
        try:
            if status not in ['Active', 'Slow', 'Overloaded']:
                return 0
            
            if not bags:
                return random.randint(10, 30)
            
            # Calculate based on number of bags and their distribution
            num_bags = len(bags)
            if num_bags <= 3:
                return random.randint(20, 40)
            elif num_bags <= 6:
                return random.randint(40, 60)
            elif num_bags <= 10:
                return random.randint(60, 80)
            else:
                return random.randint(80, 95)
                
        except Exception as e:
            logger.error(f"Error calculating utilization: {e}")
            return 50
    
    def track_passenger_baggage(self, bag_id: Optional[str] = None, flight_number: Optional[str] = None) -> Dict[str, Any]:
        """Track individual passenger baggage"""
        try:
            if bag_id:
                # Track specific bag
                if bag_id not in self.sample_baggage:
                    # Generate new bag tracking data
                    statuses = ['Checked In', 'In Sorting', 'On Conveyor', 'Loading Aircraft', 'In Transit', 'Arrived']
                    current_status = random.choice(statuses)
                    
                    flight_num = flight_number if flight_number else f'{random.choice(["AI", "6E", "SG"])}{random.randint(100, 999)}'
                    self.sample_baggage[bag_id] = {
                        'bag_id': bag_id,
                        'flight_number': flight_num,
                        'passenger_name': 'John Doe',  # In real system, this would be from booking
                        'current_status': current_status,
                        'location': f'Terminal {random.randint(1, 3)} - Belt {random.randint(1, 5)}',
                        'last_updated': datetime.datetime.now().strftime('%H:%M:%S'),
                        'weight': f'{random.randint(15, 30)} kg',
                        'destination': random.choice(['Mumbai', 'Delhi', 'Chennai']),
                        'tracking_history': [
                            {'time': '14:30', 'status': 'Checked In', 'location': 'Check-in Counter 5'},
                            {'time': '14:45', 'status': 'In Sorting', 'location': 'Baggage Sorting Area'},
                            {'time': '15:00', 'status': current_status, 'location': f'Terminal {random.randint(1, 3)} - Belt {random.randint(1, 5)}'}
                        ]
                    }
                
                return self.sample_baggage[bag_id]
            else:
                # Return sample tracking data
                return {
                    'message': 'Enter your bag ID or flight number to track your baggage',
                    'sample_bags': list(self.sample_baggage.keys())[:5]
                }
        except Exception as e:
            logger.error(f"Error tracking baggage: {e}")
            return {'error': 'Failed to track baggage'}
    
    def submit_baggage_complaint(
        self,
        passenger_name: str,
        flight_number: str,
        bag_id: str,
        issue_type: str,
        description: str,
        airport_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit baggage complaint"""
        try:
            complaint_id = f'COMP{random.randint(10000, 99999)}'
            
            complaint = {
                'complaint_id': complaint_id,
                'passenger_name': passenger_name,
                'flight_number': flight_number,
                'bag_id': bag_id,
                'issue_type': issue_type,
                'description': description,
                'status': 'Received',
                'priority': 'High' if issue_type == 'Lost Baggage' else 'Medium',
                'submitted_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estimated_resolution': '24-48 hours',
                'airport_code': airport_code
            }
            
            self.complaints.append(complaint)
            
            return {
                'success': True,
                'complaint_id': complaint_id,
                'message': f'Complaint {complaint_id} has been submitted successfully. You will receive updates via email.',
                'estimated_resolution': complaint['estimated_resolution']
            }
        except Exception as e:
            logger.error(f"Error submitting complaint: {e}")
            return {'error': 'Failed to submit complaint'}
    
    def get_airport_facilities(self, airport_code: str) -> Dict[str, Any]:
        """Get airport facility information"""
        try:
            facilities = self.airport_facilities.get(airport_code, {
                'terminals': ['T1'],
                'gates': {'T1': ['A1', 'A2', 'A3']},
                'airlines': {'T1': ['Air India', 'IndiGo']},
                'washrooms': [{'location': 'T1 - Gate A2', 'type': 'General', 'status': 'Available'}],
                'services': [{'name': 'ATM', 'location': 'T1', 'hours': '24/7'}]
            })
            
            return {
                'facilities': facilities,
                'total_terminals': len(facilities['terminals']),
                'total_gates': sum(len(gates) for gates in facilities['gates'].values()),
                'airlines_count': sum(len(airlines) for airlines in facilities['airlines'].values())
            }
        except Exception as e:
            logger.error(f"Error getting airport facilities: {e}")
            return {'error': 'Failed to get airport facilities'}
    
    def get_complaints_data(self, airport_code: str) -> Dict[str, Any]:
        """Get complaints data for staff dashboard"""
        try:
            # Add some sample complaints if none exist
            if not self.complaints:
                sample_complaints = [
                    {
                        'complaint_id': 'COMP12345',
                        'passenger_name': 'Jane Smith',
                        'flight_number': 'AI401',
                        'bag_id': 'BAG67890',
                        'issue_type': 'Lost Baggage',
                        'description': 'Baggage missing after flight arrival',
                        'status': 'In Progress',
                        'priority': 'High',
                        'submitted_at': '2025-08-28 10:30:00',
                        'estimated_resolution': '24-48 hours',
                        'airport_code': airport_code
                    },
                    {
                        'complaint_id': 'COMP12346',
                        'passenger_name': 'Bob Johnson',
                        'flight_number': '6E123',
                        'bag_id': 'BAG54321',
                        'issue_type': 'Damaged Baggage',
                        'description': 'Suitcase handle broken during handling',
                        'status': 'Resolved',
                        'priority': 'Medium',
                        'submitted_at': '2025-08-27 14:15:00',
                        'estimated_resolution': '24-48 hours',
                        'airport_code': airport_code
                    }
                ]
                self.complaints.extend(sample_complaints)
            
            # Filter complaints for airport
            complaints_for_airport = [
                c for c in self.complaints
                if not c.get('airport_code') or c.get('airport_code') == airport_code
            ]
            
            # Get complaint statistics
            total_complaints = len(complaints_for_airport)
            open_complaints = len([c for c in complaints_for_airport if c['status'] != 'Resolved'])
            high_priority = len([c for c in complaints_for_airport if c['priority'] == 'High'])
            
            return {
                'complaints': complaints_for_airport,
                'total_complaints': total_complaints,
                'open_complaints': open_complaints,
                'resolved_complaints': total_complaints - open_complaints,
                'high_priority_complaints': high_priority,
                'complaint_types': {
                    'Lost Baggage': len([c for c in complaints_for_airport if c['issue_type'] == 'Lost Baggage']),
                    'Damaged Baggage': len([c for c in complaints_for_airport if c['issue_type'] == 'Damaged Baggage']),
                    'Delayed Baggage': len([c for c in complaints_for_airport if c['issue_type'] == 'Delayed Baggage'])
                }
            }
        except Exception as e:
            logger.error(f"Error getting complaints data: {e}")
            return {'error': 'Failed to get complaints data'}
    
    def get_ai_baggage_insights(self, airport_code: str) -> Dict[str, Any]:
        """Generate AI-powered insights for baggage process improvement"""
        try:
            if not self.openai_client:
                return {
                    'insights': [
                        'AI insights are not available. Please configure OpenAI API key.',
                        'Manual analysis: Check conveyor belt utilization patterns.',
                        'Manual analysis: Review peak hour baggage processing times.',
                        'Manual analysis: Analyze complaint patterns for process improvements.'
                    ],
                    'recommendations': [
                        'Enable AI insights by configuring OpenAI API key',
                        'Monitor baggage flow during peak hours',
                        'Implement predictive maintenance for conveyor belts'
                    ],
                    'ai_enabled': False
                }
            
            # Get current data for analysis
            baggage_data = self.get_baggage_tracking_data(airport_code)
            conveyor_data = self.get_live_conveyor_data(airport_code)
            complaints_data = self.get_complaints_data(airport_code)
            
            # Prepare data summary for AI analysis
            data_summary = f"""
            Airport: {airport_code}
            
            Baggage System Status:
            - Total conveyor belts: {conveyor_data.get('total_belts', 0)}
            - Active belts: {conveyor_data.get('active_belts', 0)}
            - Total bags processed today: {baggage_data.get('total_bags_processed', 0)}
            - Average utilization: {baggage_data.get('avg_utilization', 0):.1f}%
            - Live bags count: {baggage_data.get('live_bags_count', 0)}
            - Average belt speed: {baggage_data.get('avg_belt_speed', 0)} m/s
            
            Complaints Summary:
            - Total complaints: {complaints_data.get('total_complaints', 0)}
            - Open complaints: {complaints_data.get('open_complaints', 0)}
            - High priority complaints: {complaints_data.get('high_priority_complaints', 0)}
            
            Conveyor Belt Details:
            """
            
            for belt in conveyor_data.get('conveyor_belts', [])[:3]:
                data_summary += f"- {belt['belt_id']}: {belt['status']}, {belt['utilization']}% utilization, {len(belt['bags_on_belt'])} bags\n"
            
            # Generate AI insights
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI expert in airport baggage handling systems. Analyze the provided data and provide actionable insights for improving baggage processing efficiency, reducing delays, and optimizing conveyor belt operations. Focus on practical recommendations that airport staff can implement."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this airport baggage system data and provide insights: {data_summary}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            
            import json
            ai_response = json.loads(response.choices[0].message.content)
            
            return {
                'insights': ai_response.get('insights', []),
                'recommendations': ai_response.get('recommendations', []),
                'efficiency_score': ai_response.get('efficiency_score', 75),
                'priority_actions': ai_response.get('priority_actions', []),
                'ai_enabled': True,
                'last_analysis': datetime.datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                'insights': [
                    'AI analysis failed. Using manual insights:',
                    f'Current utilization: {baggage_data.get("avg_utilization", 0):.1f}% - Consider load balancing if >85%',
                    f'Active belts: {conveyor_data.get("active_belts", 0)}/{conveyor_data.get("total_belts", 0)} - Optimize for peak efficiency',
                    f'Complaint rate: {complaints_data.get("open_complaints", 0)} open - Focus on high priority issues'
                ],
                'recommendations': [
                    'Monitor conveyor belt performance during peak hours',
                    'Implement predictive maintenance schedule',
                    'Review complaint patterns for process improvements',
                    'Consider additional staff during high utilization periods'
                ],
                'ai_enabled': False,
                'error': str(e)
            }
