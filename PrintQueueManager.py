from dataclasses import dataclass

@dataclass
class PrintJob:
    user_id: str
    job_id: str
    priority: int
    waiting_time: int = 0

class PrintQueueManager:
    def __init__(self, expiry_limit=5):
        self.queue = []
        self.expiry_limit = expiry_limit

    def enqueue_job(self, user_id, job_id, priority):
        job = PrintJob(user_id=user_id, job_id=job_id, priority=priority)
        self.queue.append(job)
        print(f"Enqueued Job {job.job_id} by User {job.user_id} with Priority {job.priority}.")

    def tick(self):
        for job in self.queue:
            job.waiting_time += 1
        print("Tick: Time has passed. Updating job timers...")
        self.remove_expired_jobs()

    def remove_expired_jobs(self):
        print("Checking for expired jobs...")
        remaining_jobs = []
        for job in self.queue:
            if job.waiting_time >= self.expiry_limit:
                print(f"❌ Job {job.job_id} by user {job.user_id} has expired and is removed.")
            else:
                remaining_jobs.append(job)
        self.queue = remaining_jobs

    def show_status(self):
        print("\n📄 Current Queue Status:")
        if not self.queue:
            print("Queue is empty.")
            return
        for job in self.queue:
            print(f"Job {job.job_id} | User: {job.user_id} | Priority: {job.priority} | Waiting: {job.waiting_time}")
        print()
