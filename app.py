from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Alert(db.Model):
    """Model representing an emergency alert."""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='active')

with app.app_context():
    db.create_all()

@app.route('/alerts', methods=['POST'])
def create_alert():
    """Create a new alert.
    Args:
        JSON body with 'type', 'description', 'severity', 'location'.
    Returns:
        JSON: {'message': 'Alert created', 'id': int} with 201 status.
        JSON: {'error': 'Missing required fields'} with 400 status if invalid.
    """
    data = request.get_json()
    if not data or not all(key in data for key in ['type', 'description', 'severity', 'location']):
        return jsonify({'error': 'Missing required fields'}), 400
    new_alert = Alert(
        type=data['type'],
        description=data['description'],
        severity=data['severity'],
        location=data['location']
    )
    db.session.add(new_alert)
    db.session.commit()
    return jsonify({'message': 'Alert created', 'id': new_alert.id}), 201

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Retrieve all alerts.
    Returns:
        JSON: List of all alerts with their details.
    """
    alerts = Alert.query.all()
    return jsonify([{
        'id': a.id,
        'type': a.type,
        'description': a.description,
        'severity': a.severity,
        'location': a.location,
        'timestamp': a.timestamp.isoformat(),
        'status': a.status
    } for a in alerts])

@app.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    """Retrieve a specific alert by ID.
    Args:
        id (int): The alert ID.
    Returns:
        JSON: Alert details if found.
        404: If alert not found.
    """
    alert = Alert.query.get_or_404(id)
    return jsonify({
        'id': alert.id,
        'type': alert.type,
        'description': alert.description,
        'severity': alert.severity,
        'location': alert.location,
        'timestamp': alert.timestamp.isoformat(),
        'status': alert.status
    })

@app.route('/alerts/<int:id>', methods=['PUT'])
def update_alert(id):
    """Update an existing alert by ID.
    Args:
        id (int): The alert ID.
        JSON body with optional 'type', 'description', 'severity', 'location', 'status'.
    Returns:
        JSON: {'message': 'Alert updated'}.
        404: If alert not found.
    """
    alert = Alert.query.get_or_404(id)
    data = request.get_json()
    if 'type' in data:
        alert.type = data['type']
    if 'description' in data:
        alert.description = data['description']
    if 'severity' in data:
        alert.severity = data['severity']
    if 'location' in data:
        alert.location = data['location']
    if 'status' in data:
        alert.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Alert updated'})

@app.route('/alerts/<int:id>', methods=['DELETE'])
def delete_alert(id):
    """Delete an alert by ID.
    Args:
        id (int): The alert ID.
    Returns:
        JSON: {'message': 'Alert deleted'}.
        404: If alert not found.
    """
    alert = Alert.query.get_or_404(id)
    db.session.delete(alert)
    db.session.commit()
    return jsonify({'message': 'Alert deleted'})

if __name__ == '__main__':
    app.run(debug=True)