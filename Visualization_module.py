class Visualization:
    def __init__(self):
        pass

    def print_status(self, job_queue):
        print("\n=== Job Queue Status ===")
        print("User ID | Job ID | Priority | Time Left")
        print("---------------------------------------")
        for job in job_queue:
            print(f"{job['user_id']}      | {job['job_id']}    | {job['priority']}       | {job['time_remaining']}")

    def show_status_gui(self, job_queue):
        import tkinter as tk

        root = tk.Tk()
        root.title("Job Queue GUI")

        tk.Label(root, text="User ID | Job ID | Priority | Time Left", font=("Arial", 12, "bold")).pack()

        for job in job_queue:
            line = f"{job['user_id']} | {job['job_id']} | {job['priority']} | {job['time_remaining']}"
            tk.Label(root, text=line, font=("Arial", 11)).pack()

        root.mainloop()
