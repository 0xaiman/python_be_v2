# app/models.py
from app.db import db


class ParkingLog(db.Model):
    __tablename__ = 'parking_logs'

    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer)  # New column
    floor_id = db.Column(db.Integer) 
    event = db.Column(db.String(100), nullable=True)
    device = db.Column(db.String(50), nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    report_type = db.Column(db.String(50), nullable=True)
    resolution_w = db.Column(db.Integer, nullable=True)
    resolution_h = db.Column(db.Integer, nullable=True)
    channel = db.Column(db.Integer, nullable=True)
    bay_name = db.Column(db.String(50), nullable=True)
    # bay_id = db.Column(db.Integer, nullable=True)
    occupancy = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    license_plate = db.Column(db.String(50), nullable=True)
    plate_color = db.Column(db.String(50), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_color = db.Column(db.String(50), nullable=True)
    vehicle_brand = db.Column(db.String(50), nullable=True)
    coordinate_x1 = db.Column(db.Integer, nullable=True)
    coordinate_y1 = db.Column(db.Integer, nullable=True)
    coordinate_x2 = db.Column(db.Integer, nullable=True)
    coordinate_y2 = db.Column(db.Integer, nullable=True)
    snapshot = db.Column(db.Text, nullable=True)
