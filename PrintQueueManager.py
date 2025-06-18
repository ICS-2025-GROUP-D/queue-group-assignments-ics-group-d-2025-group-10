import threading
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time

@dataclass(order=True)
class PrintJob:
    """Class to store metadata for each print job with sorting support"""
    # Note: priority is first to enable proper sorting
    priority: int
    timestamp: float = field(default_factory=time.time, compare=False)
    waiting_time: int = field(default=0, compare=False)
    user_id: str = field(default="", compare=False)
    job_id: str = field(default="", compare=False)
    
    def __str__(self):
        return (f"Job {self.job_id} (User: {self.user_id}) - "
                f"Priority: {self.priority}, Waiting: {self.waiting_time}s")

class PrintQueueManager:
    def __init__(self, capacity: int = 10):
        
        self.capacity = capacity
        self.queue: List[PrintJob] = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self._shutdown = False

    def is_empty(self) -> bool:
        """Check if the queue is empty"""
        return len(self.queue) == 0

    def is_full(self) -> bool:
        """Check if the queue is full"""
        return len(self.queue) >= self.capacity

    def enqueue_job(self, user_id: str, job_id: str, priority: int) -> bool:
        
        with self.condition:
            if self.is_full():
                return False

            new_job = PrintJob(
                priority=priority,
                user_id=user_id,
                job_id=job_id
            )
            
            # Insert in priority order (lower priority numbers first)
            self.queue.append(new_job)
            self.queue.sort()  # Sorts by priority (defined in PrintJob)
            
            self.condition.notify_all()
            return True

    def dequeue_job(self, blocking: bool = True) -> Optional[PrintJob]:
       
        with self.condition:
            if not blocking and self.is_empty():
                return None
                
            while not self._shutdown and self.is_empty():
                self.condition.wait()
                
            if self._shutdown:
                return None
                
            return self.queue.pop(0)  # Remove from front (highest priority)

    def get_queue_status(self) -> Dict[str, Any]:
        
        with self.lock:
            return {
                'capacity': self.capacity,
                'current_size': len(self.queue),
                'is_full': self.is_full(),
                'jobs': [{
                    'user_id': job.user_id,
                    'job_id': job.job_id,
                    'priority': job.priority,
                    'waiting_time': job.waiting_time,
                    'timestamp': job.timestamp
                } for job in self.queue]
            }

    def update_waiting_times(self) -> None:

        with self.lock:
            for job in self.queue:
                job.waiting_time += 1

    def shutdown(self) -> None:
        
        with self.condition:
            self._shutdown = True
            self.condition.notify_all()

    def __str__(self) -> str:
        
        with self.lock:
            status = self.get_queue_status()
            output = [
                f"Print Queue Status (Size: {status['current_size']}/{status['capacity']})",
                "=" * 40
            ]
            
            if self.is_empty():
                output.append("Queue is empty")
            else:
                for idx, job in enumerate(self.queue, 1):
                    output.append(f"{idx}. {job}")
                    
            return "\n".join(output)