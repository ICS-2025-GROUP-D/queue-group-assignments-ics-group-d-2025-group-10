import threading
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class PrintJob:
    """Class to store metadata for each print job"""
    user_id: str
    job_id: str
    priority: int
    waiting_time: int = 0
    timestamp: int = 0