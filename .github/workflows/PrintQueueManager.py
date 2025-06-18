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
class PrintQueueManager:
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.queue: List[Optional[PrintJob]] = [None] * capacity
        self.front = -1  # Index of front element
        self.rear = -1   # Index of rear element
        self.size = 0    # Current number of jobs in queue
        self.lock = threading.Lock()  # For thread safety