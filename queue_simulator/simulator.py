import time
from typing import Dict, List, Any
from queue_simulator.print_queue import PrintQueueManager, PrintJob, JobStatus

class PrintSimulator:
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the print simulator with configuration
        
        Args:
            config: Dictionary containing simulation parameters:
                   - capacity: Maximum queue size
                   - aging_interval: Ticks between priority updates
                   - expiry_time: Ticks before jobs expire
        """
        config = config or {}
        self.queue = PrintQueueManager(
            capacity=config.get("capacity", 10),
            aging_interval=config.get("aging_interval", 5),
            expiry_time=config.get("expiry_time", 30)
        )
        self.running = False
        self.current_event = None

    def run_simulation(self, events: List[Dict[str, Any]], delay: float = 0.5):
        """
        Run the simulation with a list of events
        
        Args:
            events: List of event dictionaries
            delay: Seconds between events for visualization
        """
        self.running = True
        print("=== Starting Simulation ===")
        
        try:
            for event in events:
                if not self.running:
                    break
                    
                self.current_event = event
                self._handle_event(event)
                print("\n" + self.queue.show_status(detailed=True))
                time.sleep(delay)
                
        except Exception as e:
            print(f"Simulation error: {e}")
        finally:
            self.queue.shutdown()
            print("=== Simulation Ended ===")

    def _handle_event(self, event: Dict[str, Any]):
        """Process a single simulation event"""
        event_type = event.get("type")
        
        if event_type == "enqueue":
            self._handle_enqueue(
                event.get("user_id"),
                event.get("job_id"),
                event.get("priority", 0)
            )
        elif event_type == "batch_submit":
            self._handle_batch_submit(event.get("jobs", []))
        elif event_type == "tick":
            self._handle_tick(event.get("ticks", 1))
        elif event_type == "print":
            self._handle_print()
        else:
            print(f"Warning: Unknown event type '{event_type}'")

    def _handle_enqueue(self, user_id: str, job_id: str, priority: int):
        """Handle single job submission"""
        if not all([user_id, job_id]):
            print("Error: Missing user_id or job_id in enqueue event")
            return
            
        if self.queue.enqueue_job(user_id, job_id, priority):
            print(f"Added job {job_id} from {user_id} (priority {priority})")
        else:
            print(f"Queue full! Could not add job {job_id}")

    def _handle_batch_submit(self, jobs: List[Dict[str, Any]]):
        """Handle multiple simultaneous submissions"""
        if not jobs:
            print("Warning: Empty batch submission")
            return
            
        result = self.queue.handle_simultaneous_submissions(jobs)
        print(f"Batch submit: {result['success']} succeeded, {result['failed']} failed")

    def _handle_tick(self, ticks: int):
        """Advance simulation time"""
        for _ in range(ticks):
            self.queue.tick()
        print(f"Advanced time by {ticks} tick(s)")

    def _handle_print(self):
        """Process next print job"""
        job = self.queue.dequeue_job()
        if job:
            job.status = JobStatus.COMPLETED
            print(f"Printed job {job.job_id} from {job.user_id}")
        else:
            print("No jobs available to print")

    def stop(self):
        """Gracefully stop the simulation"""
        self.running = False
        self.queue.shutdown()