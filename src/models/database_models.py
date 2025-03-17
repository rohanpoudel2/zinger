from datetime import datetime
from typing import List
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum, Index, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy.sql import func
from utils.base import Base

class BookingStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class UserRole(enum.Enum):
    PASSENGER = "passenger"
    ADMIN = "admin"

class RouteType(enum.Enum):
    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_TRAM = 5
    AERIAL_LIFT = 6
    FUNICULAR = 7
    TROLLEYBUS = 11
    MONORAIL = 12

class RouteModel(Base):
    __tablename__ = "routes"
    
    route_id = Column(String(50), primary_key=True)
    route_short_name = Column(String(50))
    route_long_name = Column(String(100))
    route_type = Column(String(20))  # local, express, shuttle
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    
    # Relationships
    buses = relationship("BusModel", back_populates="route_info")

    def __repr__(self):
        return f"<Route {self.route_short_name} - {self.route_long_name}>"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.PASSENGER)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bookings = relationship("BookingModel", back_populates="user", cascade="all, delete-orphan")

class BusModel(Base):
    """Model representing a bus."""
    __tablename__ = 'buses'

    id = Column(Integer, primary_key=True)
    bus_number = Column(String, nullable=False)
    route_id = Column(String, ForeignKey('routes.route_id'))
    route = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    trip_id = Column(String, nullable=True)
    next_stop = Column(String, nullable=True)
    last_updated = Column(DateTime)
    is_active = Column(Boolean, default=True)
    current_location = Column(String, nullable=True)
    available_seats = Column(Integer, default=0)
    total_seats = Column(Integer, default=0)
    fare = Column(Float, default=0.0)
    route_type = Column(String, default='local')
    distance_to_user = Column(Float, default=0.0)  # Distance in km from user's location

    # Indexes for faster querying
    __table_args__ = (
        Index('idx_bus_active_route_distance', 'is_active', 'route', 'distance_to_user'),
    )
    
    # Relationships
    bookings = relationship("BookingModel", back_populates="bus", cascade="all, delete-orphan")
    route_info = relationship("RouteModel", back_populates="buses")

    def get_last_updated_str(self):
        """Get formatted last updated time."""
        if self.last_updated:
            return self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        return None

    def get_next_departure_str(self):
        """Get formatted next departure time."""
        if self.last_updated:
            current_time = datetime.now()
            if self.last_updated > current_time:
                time_diff = self.last_updated - current_time
                if time_diff.total_seconds() < 60:
                    return "Departing now"
                elif time_diff.total_seconds() < 3600:  # Less than an hour
                    minutes = int(time_diff.total_seconds() / 60)
                    return f"In {minutes}m"
                else:
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    return f"In {hours}h {minutes}m"
            else:
                return self.last_updated.strftime("%I:%M %p")
        return "Schedule pending"

class BookingModel(Base):
    """Model representing a booking."""
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    bus_id = Column(Integer, ForeignKey('buses.id'))
    passenger_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    booking_time = Column(DateTime, default=datetime.utcnow)
    seats = Column(Integer, default=1)
    status = Column(String, default='confirmed')
    departure_time = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="bookings")
    bus = relationship("BusModel", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.id} - {self.user_id} to {self.bus_id}>" 