from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from app.db import db


class ParkingOperator(db.Model):
    __tablename__ = 'parking_operators'

    id = db.Column(db.Integer, primary_key=True)
    operator_name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    parking_floors = db.relationship('ParkingFloor', backref='operator', lazy=True)

class ParkingFloor(db.Model):
    __tablename__ = 'parking_floors'

    id = db.Column(db.Integer, primary_key=True)
    floor_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    parking_bays = db.relationship('ParkingBay', backref='floor', lazy=True)
    devices = db.relationship('Device', backref='floor', lazy=True)  # Fixed: Changed from 'Devices' to 'Device'

    # Foreign key to associate each parking floor with a parking operator
    operator_id = db.Column(db.Integer, db.ForeignKey('parking_operators.id'), nullable=False)


class ParkingBay(db.Model):
    __tablename__ = 'parking_bays'

    id = db.Column(db.Integer, primary_key=True)
    bay_name = db.Column(db.String(255), nullable=True)
    occupied = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


    floor_id = db.Column(db.Integer, db.ForeignKey('parking_floors.id'), nullable=False)

class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    floor_id = db.Column(db.Integer, db.ForeignKey('parking_floors.id'), nullable=False)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    plate_num = db.Column(db.String(255), nullable=True)  # Represents 'plateNum'

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class ParkingSession(db.Model):
    __tablename__ = 'parking_sessions'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)  # Nullable to represent an ongoing session
    space_state = db.Column(db.Integer, nullable=False, default=0)  # e.g., "active", "completed"
    change_state = db.Column(db.Integer, nullable=False, default=0)  # e.g., "active", "completed"

    # Foreign key linking to ParkingBay
    bay_id = db.Column(db.Integer, db.ForeignKey('parking_bays.id'), nullable=False)
    bay = db.relationship('ParkingBay', backref='sessions', lazy=True)

    # Foreign key linking to Vehicle
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    vehicle = db.relationship('Vehicle', backref='sessions', lazy=True)






