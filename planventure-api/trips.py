from datetime import date, datetime

from flask import Blueprint, jsonify, request

from auth import token_required
from database import db
from models import Trip

trip_bp = Blueprint('trips', __name__, url_prefix='/trips')

DATE_FORMAT = '%Y-%m-%d'


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        return None


def generate_default_itinerary(destination: str, start_date: date, end_date: date) -> str:
    days = (end_date - start_date).days + 1
    itinerary_lines = [
        f'Default itinerary for {destination}:',
        f'Stay dates: {start_date.isoformat()} → {end_date.isoformat()}',
    ]
    for day_index in range(1, days + 1):
        itinerary_lines.append(f'Day {day_index}: Add activities for {destination} here.')
    return '\n'.join(itinerary_lines)


def format_trip(trip: Trip) -> dict:
    created_at = getattr(trip, 'created_at', None)
    updated_at = getattr(trip, 'updated_at', None)

    return {
        'id': trip.id,
        'destination': trip.destination,
        'start_date': trip.start_date.isoformat() if trip.start_date else None,
        'end_date': trip.end_date.isoformat() if trip.end_date else None,
        'latitude': trip.latitude,
        'longitude': trip.longitude,
        'itinerary': trip.itinerary,
        'user_id': trip.user_id,
        'created_at': created_at.isoformat() if created_at else None,
        'updated_at': updated_at.isoformat() if updated_at else None,
    }


def get_user_trip(trip_id: int, user_id: int) -> Trip | None:
    return Trip.query.filter_by(id=trip_id, user_id=user_id).first()


@trip_bp.route('', methods=['GET'])
@token_required
def list_trips(current_user, token_payload):
    trips = Trip.query.filter_by(user_id=current_user.id).all()
    return jsonify([format_trip(trip) for trip in trips]), 200


@trip_bp.route('', methods=['POST'])
@token_required
def create_trip(current_user, token_payload):
    payload = request.get_json(silent=True) or {}
    destination = str(payload.get('destination', '')).strip()
    start_date = parse_date(payload.get('start_date'))
    end_date = parse_date(payload.get('end_date'))
    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    itinerary = payload.get('itinerary')

    if not destination:
        return jsonify({'error': 'Destination is required.'}), 400
    if start_date is None or end_date is None:
        return jsonify({'error': 'start_date and end_date must be present in YYYY-MM-DD format.'}), 400
    if end_date < start_date:
        return jsonify({'error': 'end_date must be on or after start_date.'}), 400

    if latitude is not None:
        try:
            latitude = float(latitude)
        except (TypeError, ValueError):
            return jsonify({'error': 'latitude must be a number.'}), 400

    if longitude is not None:
        try:
            longitude = float(longitude)
        except (TypeError, ValueError):
            return jsonify({'error': 'longitude must be a number.'}), 400

    if itinerary is None:
        itinerary = generate_default_itinerary(destination, start_date, end_date)

    trip = Trip(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        latitude=latitude,
        longitude=longitude,
        itinerary=itinerary,
        user_id=current_user.id,
    )
    db.session.add(trip)
    db.session.commit()

    return jsonify({
        'message': 'Trip created successfully.',
        'trip_id': trip.id,
    }), 201


@trip_bp.route('/<int:trip_id>', methods=['GET'])
@token_required
def get_trip(current_user, token_payload, trip_id: int):
    trip = get_user_trip(trip_id, current_user.id)
    if trip is None:
        return jsonify({'error': 'Trip not found.'}), 404
    return jsonify(format_trip(trip)), 200


@trip_bp.route('/<int:trip_id>', methods=['PUT'])
@token_required
def update_trip(current_user, token_payload, trip_id: int):
    trip = get_user_trip(trip_id, current_user.id)
    if trip is None:
        return jsonify({'error': 'Trip not found.'}), 404

    payload = request.get_json(silent=True) or {}
    destination = payload.get('destination')
    start_date = parse_date(payload.get('start_date')) if 'start_date' in payload else trip.start_date
    end_date = parse_date(payload.get('end_date')) if 'end_date' in payload else trip.end_date
    latitude = payload.get('latitude', trip.latitude)
    longitude = payload.get('longitude', trip.longitude)
    itinerary = payload.get('itinerary', trip.itinerary)

    if destination is not None:
        destination = str(destination).strip()
        if destination == '':
            return jsonify({'error': 'destination cannot be empty.'}), 400
        trip.destination = destination

    if start_date is None or end_date is None:
        return jsonify({'error': 'start_date and end_date must be in YYYY-MM-DD format.'}), 400
    if end_date < start_date:
        return jsonify({'error': 'end_date must be on or after start_date.'}), 400

    trip.start_date = start_date
    trip.end_date = end_date

    if latitude is not None:
        try:
            trip.latitude = float(latitude)
        except (TypeError, ValueError):
            return jsonify({'error': 'latitude must be a number.'}), 400

    if longitude is not None:
        try:
            trip.longitude = float(longitude)
        except (TypeError, ValueError):
            return jsonify({'error': 'longitude must be a number.'}), 400

    trip.itinerary = itinerary
    db.session.commit()

    return jsonify(format_trip(trip)), 200


@trip_bp.route('/<int:trip_id>', methods=['DELETE'])
@token_required
def delete_trip(current_user, token_payload, trip_id: int):
    trip = get_user_trip(trip_id, current_user.id)
    if trip is None:
        return jsonify({'error': 'Trip not found.'}), 404

    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': 'Trip deleted successfully.'}), 200
