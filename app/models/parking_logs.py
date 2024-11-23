# app/models.py
from app.db import db


class ParkingLog(db.Model):
    __tablename__ = 'parking_logs'

    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer)  # New column
    floor_id = db.Column(db.Integer) 
    event = db.Column(db.String(100), nullable=False)
    device = db.Column(db.String(50), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    resolution_w = db.Column(db.Integer, nullable=False)
    resolution_h = db.Column(db.Integer, nullable=False)
    channel = db.Column(db.Integer, nullable=False)
    bay_name = db.Column(db.String(50), nullable=False)
    bay_id = db.Column(db.Integer, nullable=False)
    occupancy = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=True)
    license_plate = db.Column(db.String(50), nullable=True)
    plate_color = db.Column(db.String(50), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_color = db.Column(db.String(50), nullable=True)
    vehicle_brand = db.Column(db.String(50), nullable=True)
    coordinate_x1 = db.Column(db.Integer, nullable=False)
    coordinate_y1 = db.Column(db.Integer, nullable=False)
    coordinate_x2 = db.Column(db.Integer, nullable=False)
    coordinate_y2 = db.Column(db.Integer, nullable=False)
    snapshot = db.Column(db.Text, nullable=True)
