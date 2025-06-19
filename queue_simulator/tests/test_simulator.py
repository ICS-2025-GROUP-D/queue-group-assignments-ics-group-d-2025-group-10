import unittest
import time
from queue_simulator.simulator import PrintSimulator
from queue_simulator.print_queue import PrintJob, JobStatus

class TestPrintSimulator(unittest.TestCase):
    def setUp(self):
        """Create a fresh simulator instance for each test"""
        self.simulator = PrintSimulator({
            "capacity": 5,
            "aging_interval": 3,
            "expiry_time": 10
        })
        self.sample_events = [
            {"type": "enqueue", "user_id": "user1", "job_id": "doc1", "priority": 2},
            {"type": "enqueue", "user_id": "user2", "job_id": "doc2", "priority": 1},
            {"type": "tick", "ticks": 2},
            {"type": "print"},
            {"type": "batch_submit", "jobs": [
                {"user_id": "user3", "job_id": "doc3", "priority": 3},
                {"user_id": "user4", "job_id": "doc4", "priority": 0}
            ]},
            {"type": "tick", "ticks": 5},
            {"type": "print"}
        ]

    def test_initialization(self):
        """Test simulator initializes with correct configuration"""
        self.assertEqual(self.simulator.queue.capacity, 5)
        self.assertEqual(self.simulator.queue.aging_interval, 3)
        self.assertEqual(self.simulator.queue.expiry_time, 10)
        self.assertFalse(self.simulator.running)

    def test_enqueue_handling(self):
        """Test single job enqueue event handling"""
        event = {"type": "enqueue", "user_id": "user1", "job_id": "doc1", "priority": 1}
        self.simulator._handle_event(event)
        
        self.assertEqual(len(self.simulator.queue.queue), 1)
        self.assertEqual(self.simulator.queue.queue[0].job_id, "doc1")
        self.assertEqual(self.simulator.queue.queue[0].priority, 1)

    def test_invalid_enqueue(self):
        """Test handling of invalid enqueue events"""
        # Missing user_id
        event = {"type": "enqueue", "job_id": "doc1", "priority": 1}
        self.simulator._handle_event(event)
        self.assertEqual(len(self.simulator.queue.queue), 0)
        
        # Missing job_id
        event = {"type": "enqueue", "user_id": "user1", "priority": 1}
        self.simulator._handle_event(event)
        self.assertEqual(len(self.simulator.queue.queue), 0)
        
        # Invalid priority
        event = {"type": "enqueue", "user_id": "user1", "job_id": "doc1", "priority": "high"}
        self.simulator._handle_event(event)
        self.assertEqual(len(self.simulator.queue.queue), 0)

    def test_batch_submit(self):
        """Test batch job submission handling"""
        event = {
            "type": "batch_submit",
            "jobs": [
                {"user_id": "user1", "job_id": "doc1", "priority": 1},
                {"user_id": "user2", "job_id": "doc2", "priority": 2},
                {"user_id": "user3", "job_id": "doc3", "priority": 3}
            ]
        }
        self.simulator._handle_event(event)
        
        self.assertEqual(len(self.simulator.queue.queue), 3)
        self.assertEqual(self.simulator.queue.queue[0].job_id, "doc1")  # Highest priority

    def test_empty_batch_submit(self):
        """Test handling of empty batch submissions"""
        event = {"type": "batch_submit", "jobs": []}
        self.simulator._handle_event(event)
        self.assertEqual(len(self.simulator.queue.queue), 0)

    def test_tick_handling(self):
        """Test time advancement and its effects"""
        # Add a job first
        self.simulator._handle_event(
            {"type": "enqueue", "user_id": "user1", "job_id": "doc1", "priority": 2}
        )
        
        initial_time = self.simulator.queue.current_time
        initial_wait = self.simulator.queue.queue[0].waiting_time
        
        # Advance time by 3 ticks (should trigger aging)
        self.simulator._handle_event({"type": "tick", "ticks": 3})
        
        self.assertEqual(self.simulator.queue.current_time, initial_time + 3)
        self.assertEqual(self.simulator.queue.queue[0].waiting_time, initial_wait + 3)
        self.assertEqual(self.simulator.queue.queue[0].priority, 1)  # Aged once

    def test_print_handling(self):
        """Test job printing and dequeue"""
        # Add two jobs with different priorities
        self.simulator._handle_event(
            {"type": "enqueue", "user_id": "user1", "job_id": "doc1", "priority": 2}
        )
        self.simulator._handle_event(
            {"type": "enqueue", "user_id": "user2", "job_id": "doc2", "priority": 1}
        )
        
        # Should print higher priority job (doc2)
        self.simulator._handle_event({"type": "print"})
        
        self.assertEqual(len(self.simulator.queue.queue), 1)
        self.assertEqual(self.simulator.queue.queue[0].job_id, "doc1")

    def test_print_empty_queue(self):
        """Test printing from empty queue"""
        self.simulator._handle_event({"type": "print"})
        self.assertEqual(len(self.simulator.queue.queue), 0)

    def test_expiry_handling(self):
        """Test job expiry after waiting too long"""
        self.simulator._handle_event(
            {"type": "enqueue", "user_id": "user1", "job_id": "doc1", "priority": 1}
        )
        
        # Advance time beyond expiry (10 ticks)
        self.simulator._handle_event({"type": "tick", "ticks": 11})
        
        self.assertEqual(len(self.simulator.queue.queue), 0)
        self.assertEqual(len(self.simulator.queue.history[-1]["expired_jobs"]), 1)

    def test_full_simulation(self):
        """Test complete simulation with multiple events"""
        # Queue should be empty initially
        self.assertEqual(len(self.simulator.queue.queue), 0)
        
        # Run the full simulation
        self.simulator.run_simulation(self.sample_events, delay=0)
        
        # Verify final state
        self.assertEqual(len(self.simulator.queue.queue), 2)
        self.assertEqual(self.simulator.queue.current_time, 8)  # 2 + 5 + 1 implicit tick
        
        # Check that high priority job (doc4) was printed
        printed_jobs = [e for e in self.simulator.queue.history if e["event"] == "dequeue"]
        self.assertEqual(len(printed_jobs), 2)
        self.assertEqual(printed_jobs[0]["job_id"], "doc2")  # First print
        self.assertEqual(printed_jobs[1]["job_id"], "doc4")  # Second print

    def test_simulation_stop(self):
        """Test early termination of simulation"""
        self.simulator.running = True
        self.simulator.stop()
        
        self.assertFalse(self.simulator.running)
        self.assertTrue(self.simulator.queue._shutdown)

    def test_unknown_event_type(self):
        """Test handling of unknown event types"""
        with self.assertLogs(level='WARNING'):
            self.simulator._handle_event({"type": "unknown_event"})
        self.assertEqual(len(self.simulator.queue.queue), 0)

if __name__ == "__main__":
    unittest.main()