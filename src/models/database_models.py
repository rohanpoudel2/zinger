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

class Base(DeclarativeBase):
    pass

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
    
    bus_number = Column(String(50), primary_key=True)
    route = Column(String(100), nullable=False)
    departure = Column(DateTime, nullable=False)
    fare = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    capacity = Column(Integer, default=30)
    current_location = Column(String(100))
    route_type = Column(String(50))  # local, express, shuttle
    agency_id = Column(String(50), default="CTTRANSIT")
    last_updated = Column(DateTime, default=func.now())
    
    # Relationships
    bookings = relationship("BookingModel", back_populates="bus", cascade="all, delete-orphan")
    booked_seats = relationship("BookedSeatModel", back_populates="bus", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bus {self.bus_number} - {self.route}>"

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