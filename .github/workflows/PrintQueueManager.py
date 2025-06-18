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

    def is_empty(self) -> bool:
        """Check if the queue is empty"""
        return self.size == 0
    
    def is_full(self) -> bool:
        """Check if the queue is full"""
        return self.size == self.capacity
    
    def enqueue_job(self, user_id: str, job_id: str, priority: int, current_time: int) -> bool:
    
        with self.lock:  # Ensure thread-safe operation
            if self.is_full():
                return False

            new_job = PrintJob(
                user_id=user_id,
                job_id=job_id,
                priority=priority,
                timestamp=current_time
            )

            # For empty queue
            if self.is_empty():
                self.front = self.rear = 0
            else:
                self.rear = (self.rear + 1) % self.capacity

            self.queue[self.rear] = new_job
            self.size += 1
            return True
    
    def dequeue_job(self) -> Optional[PrintJob]:
        with self.lock:  # Ensure thread-safe operation
            if self.is_empty():
                return None

            job = self.queue[self.front]
            
            # If this was the last job
            if self.front == self.rear:
                self.front = self.rear = -1
            else:
                self.front = (self.front + 1) % self.capacity

            self.size -= 1
            return job