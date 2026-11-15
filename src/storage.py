import json
import os
from typing import List, Optional
from models import Ride


class CarpoolManager:
    def __init__(self, filepath: str = "carpool_data.json"):
        self.filepath = filepath
        self.rides: List[Ride] = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            self._seed_sample_data()
            self.save()
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                self.rides = [Ride.from_dict(item) for item in raw_data]
        except (json.JSONDecodeError, KeyError):
            self.rides = []

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in self.rides], f, indent=2)

    def add_ride(self, ride: Ride):
        self.rides.insert(0, ride)
        self.save()

    def get_ride(self, ride_id: str) -> Optional[Ride]:
        for ride in self.rides:
            if ride.ride_id == ride_id:
                return ride
        return None

    def search_rides(self, origin: str = "", destination: str = "") -> List[Ride]:
        o_query = origin.strip().lower()
        d_query = destination.strip().lower()
        return [
            r for r in self.rides
            if (not o_query or o_query in r.origin.lower())
            and (not d_query or d_query in r.destination.lower())
        ]

    def _seed_sample_data(self):
        self.rides = [
            Ride(
                driver_name="Thabo M.",
                origin="Sandton Gautrain",
                destination="Pretoria CBD",
                departure_time="07:30 AM",
                price_per_seat=65.00,
                total_seats=3,
                vehicle="VW Polo Vivo (Silver)",
                passengers=["Lerato K."],
            ),
            Ride(
                driver_name="Sarah N.",
                origin="Rondebosch",
                destination="Cape Town City Bowl",
                departure_time="08:00 AM",
                price_per_seat=40.00,
                total_seats=2,
                vehicle="Toyota Corolla Quest (White)",
                passengers=[],
            ),
            Ride(
                driver_name="Devon P.",
                origin="Umhlanga Rocks",
                destination="Durban North Campus",
                departure_time="08:15 AM",
                price_per_seat=35.00,
                total_seats=4,
                vehicle="Hyundai i20 (Blue)",
                passengers=["Amahle D.", "Liam S."],
            ),
        ]
