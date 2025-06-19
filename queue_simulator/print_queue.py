import threading
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class JobStatus(Enum):
    PENDING = "Pending"
    PRINTING = "Printing"
    COMPLETED = "Completed"
    EXPIRED = "Expired"

@dataclass(order=True)
class PrintJob:
    priority: int
    timestamp: float = field(default_factory=time.time)
    waiting_time: int = 0
    user_id: str = field(default="", compare=False)
    job_id: str = field(default="", compare=False)
    status: JobStatus = field(default=JobStatus.PENDING, compare=False)
    
    def __str__(self):
        return (f"Job {self.job_id} (User: {self.user_id}) - "
                f"Priority: {self.priority}, Waiting: {self.waiting_time}s, "
                f"Status: {self.status.value}")

class PrintQueueManager:
    def __init__(self, capacity: int = 10, aging_interval: int = 5, expiry_time: int = 30):
        self.capacity = capacity
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time
        self.queue: List[PrintJob] = []
        self.history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self._shutdown = False
        self.current_time = 0

    # Core Queue Operations (Member 1)
    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def is_full(self) -> bool:
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
            self.queue.append(new_job)
            self._sort_queue()
            self._log_event("enqueue", job_id)
            self.condition.notify_all()
            return True

    def dequeue_job(self) -> Optional[PrintJob]:
        with self.condition:
            while not self._shutdown and self.is_empty():
                self.condition.wait()
                
            if self._shutdown or self.is_empty():
                return None
                
            job = self.queue.pop(0)
            job.status = JobStatus.PRINTING
            self._log_event("dequeue", job.job_id)
            return job

    # Priority & Aging System (Member 2)
    def _sort_queue(self):
        """Sort by priority then waiting time"""
        self.queue.sort(key=lambda x: (x.priority, x.waiting_time))

    def apply_priority_aging(self):
        with self.lock:
            for job in self.queue:
                if job.waiting_time % self.aging_interval == 0:
                    job.priority = max(0, job.priority - 1)
            self._sort_queue()
            self._log_event("aging", None)

    # Job Expiry & Cleanup (Member 3)
    def remove_expired_jobs(self) -> List[PrintJob]:
        expired_jobs = []
        with self.lock:
            remaining_jobs = []
            for job in self.queue:
                if job.waiting_time > self.expiry_time:
                    job.status = JobStatus.EXPIRED
                    expired_jobs.append(job)
                    self._log_event("expire", job.job_id)
                else:
                    remaining_jobs.append(job)
            self.queue = remaining_jobs
        return expired_jobs

    # Concurrent Job Handling (Member 4)
    def handle_simultaneous_submissions(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        results = {"success": 0, "failed": 0}
        for job in jobs:
            if self.enqueue_job(job["user_id"], job["job_id"], job["priority"]):
                results["success"] += 1
            else:
                results["failed"] += 1
        self._log_event("batch_submit", None, extra_data=results)
        return results

    # Time Management (Member 5)
    def tick(self):
        with self.lock:
            self.current_time += 1
            for job in self.queue:
                job.waiting_time += 1
            
            if self.current_time % self.aging_interval == 0:
                self.apply_priority_aging()
                
            expired = self.remove_expired_jobs()
            self._log_event("tick", None, extra_data={
                "current_time": self.current_time,
                "expired_jobs": [j.job_id for j in expired]
            })

    # Visualization & Reporting (Member 6)
    def _log_event(self, event_type: str, job_id: Optional[str], extra_data: Optional[Dict] = None):
        entry = {
            "timestamp": self.current_time,
            "event": event_type,
            "job_id": job_id,
            "queue_size": len(self.queue),
            "queue_state": [str(j) for j in self.queue]
        }
        if extra_data:
            entry.update(extra_data)
        self.history.append(entry)

    def show_status(self, detailed: bool = False) -> str:
        with self.lock:
            status = [
                f"=== Print Queue Status [Time: {self.current_time}] ===",
                f"Capacity: {len(self.queue)}/{self.capacity}",
                f"Jobs in queue: {len(self.queue)}",
                f"Next aging in: {self.aging_interval - (self.current_time % self.aging_interval)} ticks"
            ]
            
            if detailed and self.queue:
                status.append("\nCurrent Queue:")
                for idx, job in enumerate(self.queue, 1):
                    status.append(f"{idx}. {job}")
            
            return "\n".join(status)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history.copy()

    def shutdown(self):
        with self.condition:
            self._shutdown = True
            self.condition.notify_all()