from flask import Blueprint, request, jsonify
from models import db, Opportunity
import jwt
import datetime
import functools
import os

opportunities_bp = Blueprint('opportunities', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            from models import Admin
            current_admin = Admin.query.get(data['admin_id'])
            if not current_admin:
                raise
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(current_admin, *args, **kwargs)
    return decorated

@opportunities_bp.route('/api/opportunities', methods=['GET'])
@token_required
def get_opportunities(current_admin):
    opps = Opportunity.query.filter_by(admin_id=current_admin.id).all()
    result = []
    for opp in opps:
        result.append({
            'id': opp.id,
            'name': opp.name,
            'duration': opp.duration,
            'start_date': opp.start_date.isoformat(),
            'description': opp.description,
            'skills': opp.skills,
            'category': opp.category,
            'max_applicants': opp.max_applicants,
            'future_opportunities': opp.future_opportunities
        })
    return jsonify(result), 200

@opportunities_bp.route('/api/opportunities', methods=['POST'])
@token_required
def add_opportunity(current_admin):
    data = request.get_json()
    name = data.get('name')
    duration = data.get('duration')
    start_date_str = data.get('start_date')
    description = data.get('description')
    skills = data.get('skills')  # list or string
    category = data.get('category')
    future_opportunities = data.get('future_opportunities')
    max_applicants = data.get('max_applicants')

    if not all([name, duration, start_date_str, description, skills, category, future_opportunities]):
        return jsonify({'error': 'All required fields must be provided'}), 400

    try:
        start_date = datetime.datetime.fromisoformat(start_date_str).date()
    except:
        return jsonify({'error': 'Invalid start date'}), 400

    if isinstance(skills, list):
        skills = ','.join(skills)

    opp = Opportunity(
        name=name,
        duration=duration,
        start_date=start_date,
        description=description,
        skills=skills,
        category=category,
        max_applicants=max_applicants,
        future_opportunities=future_opportunities,
        admin_id=current_admin.id
    )
    db.session.add(opp)
    db.session.commit()

    return jsonify({'message': 'Opportunity created successfully', 'id': opp.id}), 201

@opportunities_bp.route('/api/opportunities/<int:id>', methods=['PUT'])
@token_required
def edit_opportunity(current_admin, id):
    opp = Opportunity.query.get_or_404(id)
    if opp.admin_id != current_admin.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    opp.name = data.get('name', opp.name)
    opp.duration = data.get('duration', opp.duration)
    start_date_str = data.get('start_date')
    if start_date_str:
        try:
            opp.start_date = datetime.datetime.fromisoformat(start_date_str).date()
        except:
            return jsonify({'error': 'Invalid start date'}), 400
    opp.description = data.get('description', opp.description)
    skills = data.get('skills')
    if skills:
        if isinstance(skills, list):
            opp.skills = ','.join(skills)
        else:
            opp.skills = skills
    opp.category = data.get('category', opp.category)
    opp.max_applicants = data.get('max_applicants', opp.max_applicants)
    opp.future_opportunities = data.get('future_opportunities', opp.future_opportunities)

    db.session.commit()
    return jsonify({'message': 'Opportunity updated successfully'}), 200

@opportunities_bp.route('/api/opportunities/<int:id>', methods=['DELETE'])
@token_required
def delete_opportunity(current_admin, id):
    opp = Opportunity.query.get_or_404(id)
    if opp.admin_id != current_admin.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted successfully'}), 200

@opportunities_bp.route('/api/opportunities/<int:id>', methods=['GET'])
@token_required
def get_opportunity(current_admin, id):
    opp = Opportunity.query.get_or_404(id)
    if opp.admin_id != current_admin.id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': opp.id,
        'name': opp.name,
        'duration': opp.duration,
        'start_date': opp.start_date.isoformat(),
        'description': opp.description,
        'skills': opp.skills.split(',') if opp.skills else [],
        'category': opp.category,
        'max_applicants': opp.max_applicants,
        'future_opportunities': opp.future_opportunities
    }), 200