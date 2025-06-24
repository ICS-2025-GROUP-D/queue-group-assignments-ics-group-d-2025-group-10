import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class PrintJob:
    user_id: str
    job_id: str
    priority: Priority
    arrival_time: int
    waiting_time: int = 0

class QueueFullException(Exception):
    pass

class CircularQueue:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue: List[Optional[PrintJob]] = [None] * capacity
        self.front = self.rear = -1
        self.lock = threading.Lock()

    def is_empty(self) -> bool:
        return self.front == -1

    def is_full(self) -> bool:
        return (self.rear + 1) % self.capacity == self.front

    def enqueue(self, job: PrintJob) -> None:
        with self.lock:
            if self.is_full():
                raise QueueFullException()
            if self.is_empty():
                self.front = self.rear = 0
            else:
                self.rear = (self.rear + 1) % self.capacity
            self.queue[self.rear] = job

    def dequeue(self) -> Optional[PrintJob]:
        with self.lock:
            if self.is_empty():
                return None

            job = self.queue[self.front]
            if self.front == self.rear:
                self.front = self.rear = -1
            else:
                self.front = (self.front + 1) % self.capacity
            return job

    def status(self) -> List[Optional[PrintJob]]:
        with self.lock:
            if self.is_empty():
                return []
            
            if self.front <= self.rear:
                return self.queue[self.front:self.rear+1]
            else:
                return self.queue[self.front:] + self.queue[:self.rear+1]

class PrintQueueManager:
    def __init__(self, capacity: int = 10, aging_interval: int = 5, expiry_time: int = 30):
        self.queue = CircularQueue(capacity)
        self.aging_interval = aging_interval
        self.expiry_time = expiry_time
        self.time_elapsed = 0
        self.print_lock = threading.Lock()
        self.job_counter = 0

    # Module 1: Core Queue Management
    def enqueue_job(self, user_id: str, priority: Priority) -> str:
        """Add a new print job to the queue"""
        job_id = f"job-{self.job_counter}"
        self.job_counter += 1
        
        try:
            job = PrintJob(user_id, job_id, priority, self.time_elapsed)
            self.queue.enqueue(job)
            return f"Job {job_id} enqueued successfully"
        except QueueFullException:
            return f"Queue is full. Job {job_id} rejected"

    def print_job(self) -> Optional[PrintJob]:
        """Remove and return the highest priority job for printing"""
        jobs = self.queue.status()
        if not jobs:
            return None

        # Find job with highest priority (and oldest if tie)
        highest_priority_job = max(
            (job for job in jobs if job is not None),
            key=lambda j: (j.priority.value, -j.waiting_time)
        )
        
        # Dequeue all jobs until we find the highest priority one
        dequeued_jobs = []
        target_job = None
        while True:
            job = self.queue.dequeue()
            if job is None:
                break
            if job.job_id == highest_priority_job.job_id:
                target_job = job
                break
            dequeued_jobs.append(job)
        
        # Re-enqueue the other jobs
        for job in dequeued_jobs:
            self.queue.enqueue(job)
        
        return target_job

    # Module 2: Priority & Aging System
    def apply_priority_aging(self) -> None:
        """Increase priority of waiting jobs based on aging interval"""
        jobs = self.queue.status()
        for job in jobs:
            if job and self.time_elapsed > 0 and self.time_elapsed % self.aging_interval == 0:
                if job.priority != Priority.HIGH:
                    job.priority = Priority(job.priority.value + 1)

    # Module 3: Job Expiry & Cleanup
    def remove_expired_jobs(self) -> List[PrintJob]:
        """Remove jobs that have exceeded their expiry time"""
        jobs = self.queue.status()
        expired_jobs = [
            job for job in jobs 
            if job and (self.time_elapsed - job.arrival_time) >= self.expiry_time
        ]
        
        # Remove expired jobs from queue
        remaining_jobs = [job for job in jobs if job not in expired_jobs]
        
        # Rebuild the queue with remaining jobs
        self.queue = CircularQueue(self.queue.capacity)
        for job in remaining_jobs:
            self.queue.enqueue(job)
        
        return expired_jobs

    # Module 4: Concurrent Job Submission Handling
    def handle_simultaneous_submissions(self, submissions: List[tuple]) -> List[str]:
        """Handle multiple job submissions at once"""
        results = []
        for user_id, priority in submissions:
            results.append(self.enqueue_job(user_id, Priority(priority)))
        return results

    # Module 5: Event Simulation & Time Management
    def tick(self) -> None:
        """Advance the simulation time by one unit"""
        self.time_elapsed += 1
        
        # Update waiting time for all jobs
        for job in self.queue.status():
            if job:
                job.waiting_time = self.time_elapsed - job.arrival_time
        
        # Apply aging and expiry
        self.apply_priority_aging()
        expired = self.remove_expired_jobs()
        
        if expired:
            print(f"Time {self.time_elapsed}: Expired jobs - {[j.job_id for j in expired]}")

    # Module 6: Visualization & Reporting
    def show_status(self) -> None:
        """Display the current state of the print queue"""
        jobs = self.queue.status()
        if not jobs:
            print(f"Time {self.time_elapsed}: Queue is empty")
            return

        print(f"\nTime {self.time_elapsed}: Print Queue Status")
        print("=" * 40)
        print("{:<10} {:<10} {:<10} {:<10} {:<10}".format(
            "Position", "Job ID", "User", "Priority", "Wait Time"))
        print("-" * 40)
        
        for i, job in enumerate(jobs):
            if job:
                print("{:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    i, job.job_id, job.user_id, job.priority.name, job.waiting_time))
            else:
                print("{:<10} {:<10}".format(i, "Empty"))
        print("=" * 40)

def simulation_test():
    """Test function to demonstrate the print queue simulation"""
    pq = PrintQueueManager(capacity=5, aging_interval=3, expiry_time=8)
    
    # Initial submissions
    print(pq.enqueue_job("user1", Priority.LOW))
    print(pq.enqueue_job("user2", Priority.MEDIUM))
    pq.show_status()
    
    # Simultaneous submissions
    print("\nSimultaneous submissions:")
    results = pq.handle_simultaneous_submissions([
        ("user3", 1), ("user4", 3), ("user5", 2)
    ])
    for result in results:
        print(result)
    pq.show_status()
    
    # Time progression with ticks
    for _ in range(10):
        pq.tick()
        if _ % 2 == 0:
            # Try to print a job every 2 ticks
            job = pq.print_job()
            if job:
                print(f"\nPrinting job: {job.job_id} (Priority: {job.priority.name})")
        pq.show_status()

if __name__ == "__main__":
    simulation_test()