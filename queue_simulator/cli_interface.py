import cmd
from queue_simulator.print_queue import PrintQueueManager
from queue_simulator.simulator import PrintSimulator

class PrintQueueCLI(cmd.Cmd):
    prompt = "(print-queue) "
    
    def __init__(self):
        super().__init__()
        self.queue = PrintQueueManager()
        self.simulator = None
        
    def do_enqueue(self, arg):
        """Add a print job: enqueue <user_id> <job_id> <priority>"""
        try:
            user_id, job_id, priority = arg.split()
            if self.queue.enqueue_job(user_id, job_id, int(priority)):
                print(f"Added job {job_id}")
            else:
                print("Queue is full!")
        except ValueError:
            print("Invalid arguments. Usage: enqueue <user> <job> <priority>")
            
    def do_status(self, arg):
        """Show current queue status"""
        print(self.queue.show_status(detailed=True))
        
    def do_tick(self, arg):
        """Advance time by 1 tick"""
        self.queue.tick()
        self.do_status(None)
        
    def do_history(self, arg):
        """Show event history"""
        for entry in self.queue.get_history():
            print(f"[{entry['timestamp']}] {entry['event']}: {entry.get('job_id', '')}")
            
    def do_simulate(self, arg):
        """Run simulation from file"""
        try:
            import json
            with open(arg) as f:
                events = json.load(f)
                
            self.simulator = PrintSimulator({
                "capacity": 10,
                "aging_interval": 5,
                "expiry_time": 15
            })
            self.simulator.run_simulation(events)
        except Exception as e:
            print(f"Simulation failed: {e}")
            
    def do_quit(self, arg):
        """Exit the program"""
        self.queue.shutdown()
        if self.simulator:
            self.simulator.running = False
        return True