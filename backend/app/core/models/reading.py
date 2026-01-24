from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

@dataclass
class Reading:
    id: int
    user_id: UUID
    day_reading: Decimal
    night_reading: Decimal
    reading_date: date