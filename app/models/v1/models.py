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
