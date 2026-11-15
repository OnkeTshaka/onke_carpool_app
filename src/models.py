# OOP CLASSES (Ride, Booking)
from dataclasses import dataclass, field, asdict
from typing import List
import uuid

@dataclass
class Ride:
    driver_name: str
    origin:str
    destination:str
    departure_time:str
    price_per_seat:float
    total_seats:int
    vehicle:str
    passengers: List[str] = field(default_factory=list)
    ride_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


    @property
    def seats_available(self) -> int:
        return max(0, self.total_seats - len(self.passengers))

    def book_seat(self, passenger_name:str) -> tuple[bool, str]:
        if passenger_name == self.driver_name:
            return False, "You cannot book your own ride."
        if passenger_name == self.passengers:
            return False, "You have already booked a seat on this ride."
        if self.seats_available <= 0:
            return False, "No seats left on this ride"
        self.passengers.append(passenger_name)
        return True, "Seat booked successfully!"


    def cancel_booking(self, passenger_name:str)-> bool:
        if passenger_name in self.passengers:
            self.passengers.remove(passenger_name)
            return True
        return False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data:dict) -> "Ride":
        return cls(**data)
