from datetime import datetime
from typing import List
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum, Index, Column, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum
from sqlalchemy.sql import func

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

class Base(DeclarativeBase):
    pass

class RouteModel(Base):
    __tablename__ = "routes"
    
    route_id = Column(String(50), primary_key=True)
    agency_id = Column(String(50), nullable=False)
    route_short_name = Column(String(50))
    route_long_name = Column(String(255))
    route_desc = Column(String(255))
    route_type = Column(SQLEnum(RouteType))
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    last_updated = Column(DateTime, default=func.now())
    
    # Relationships
    buses = relationship("BusModel", back_populates="route_info")

    def __repr__(self):
        return f"<Route {self.route_short_name} - {self.route_long_name}>"

class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    bookings: Mapped[List["BookingModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class BusModel(Base):
    __tablename__ = "buses"
    
    bus_number = Column(String(50), primary_key=True)  # CTTransit vehicle ID
    route = Column(String(100), nullable=False)  # Route name
    route_id = Column(String(50), ForeignKey("routes.route_id"), index=True)  # CTTransit route ID
    departure = Column(DateTime, nullable=True)  # Made nullable for real-time tracking
    fare = Column(Float, nullable=True)  # Made nullable for real-time tracking
    is_active = Column(Boolean, default=True)
    capacity = Column(Integer, default=30)
    current_location = Column(String(100))
    route_type = Column(String(50))  # local, express, shuttle
    agency_id = Column(String(50), default="CTTRANSIT")
    last_updated = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # Additional CTTransit fields
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)  # meters per second
    bearing = Column(Float)  # degrees from true north
    trip_id = Column(String(50))  # CTTransit trip ID
    next_stop = Column(String(100))
    
    # Relationships
    bookings = relationship("BookingModel", back_populates="bus", cascade="all, delete-orphan")
    booked_seats = relationship("BookedSeatModel", back_populates="bus", cascade="all, delete-orphan")
    route_info = relationship("RouteModel", back_populates="buses")

    def __repr__(self):
        return f"<Bus {self.bus_number} - {self.route}>"
        
    def get_departure_str(self):
        """Get formatted departure time or 'Real-time' if None."""
        if self.departure is None:
            return "Real-time"
        try:
            return self.departure.strftime("%I:%M %p")
        except:
            return "Real-time"
            
    def get_last_updated_str(self):
        """Get formatted last_updated time or None if not available."""
        if self.last_updated is None:
            return None
        try:
            return self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        except:
            return None

class BookingModel(Base):
    __tablename__ = "bookings"
    
    booking_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    bus_number: Mapped[str] = mapped_column(String(10), ForeignKey("buses.bus_number"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    passenger_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    seat: Mapped[str] = mapped_column(String(5))
    status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)
    booking_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    bus: Mapped[BusModel] = relationship(back_populates="bookings")
    user: Mapped[UserModel] = relationship(back_populates="bookings")

    __table_args__ = (
        Index('idx_booking_status_time', 'status', 'booking_time'),
    )

class BookedSeatModel(Base):
    __tablename__ = "booked_seats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bus_number: Mapped[str] = mapped_column(String(10), ForeignKey("buses.bus_number"), index=True)
    seat: Mapped[str] = mapped_column(String(5))
    booking_id: Mapped[str] = mapped_column(String(20), ForeignKey("bookings.booking_id"), nullable=True)
    
    # Relationships
    bus: Mapped[BusModel] = relationship(back_populates="booked_seats")

    __table_args__ = (
        Index('idx_bus_seat', 'bus_number', 'seat', unique=True),
    )

    class Config:
        orm_mode = True 