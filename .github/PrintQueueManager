class PrintQueueManager:
    def __init__(self, aging_interval=5):
        self.priority_queue = []
        self.aging_interval = aging_interval  # ticks between aging updates
        self.tick_counter = 0
        def _prioritize_jobs(self):
        """Sort jobs by priority (highest first) and waiting time (longest first for ties)"""
        self.priority_queue.sort(key=lambda job: (-job['priority'], job['wait_time']))
        def apply_priority_aging(self):
        """Increment priority of waiting jobs after aging interval"""
        self.tick_counter += 1
        if self.tick_counter >= self.aging_interval:
            self.tick_counter = 0
            for job in self.priority_queue:
                if job['priority'] > 0:  # Don't age jobs that are already max priority
                    job['priority'] -= 1  # Higher priority = lower number in our system
            self._prioritize_jobs()
        def enqueue_job(self, user_id, job_id, priority):
        """Add new job with proper priority handling"""
        new_job = {
            'user_id': user_id,
            'job_id': job_id,
            'priority': priority,
            'wait_time': 0,
            'arrival_time': self.current_time
        }
        self.priority_queue.append(new_job)
        self._prioritize_jobs()
        def dequeue_job(self):
        """Remove and return the highest priority job"""
        if not self.priority_queue:
            return None
        return self.priority_queue.pop(0)