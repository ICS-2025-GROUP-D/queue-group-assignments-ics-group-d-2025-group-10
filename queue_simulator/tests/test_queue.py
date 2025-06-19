import unittest
from queue_simulator.print_queue import PrintQueueManager, PrintJob

class TestPrintQueue(unittest.TestCase):
    def setUp(self):
        self.queue = PrintQueueManager(capacity=3)
        
    def test_enqueue_dequeue(self):
        self.assertTrue(self.queue.enqueue_job("user1", "job1", 2))
        self.assertTrue(self.queue.enqueue_job("user2", "job2", 1))
        job = self.queue.dequeue_job()
        self.assertEqual(job.job_id, "job2")  # Higher priority
        
    def test_priority_aging(self):
        self.queue.enqueue_job("user1", "job1", 3)
        for _ in range(5):  # Aging interval
            self.queue.tick()
        self.assertEqual(self.queue.queue[0].priority, 2)
        
    def test_expiry(self):
        self.queue.enqueue_job("user1", "job1", 1)
        for _ in range(31):  # Expiry time
            self.queue.tick()
        self.assertEqual(len(self.queue.queue), 0)