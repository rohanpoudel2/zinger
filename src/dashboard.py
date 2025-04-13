import tkinter as tk
from tkinter import messagebox
import subprocess

class ZingerDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Zinger Bus Reservation System")
        self.root.geometry("500x400")

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.root, text="Zinger Dashboard", font=("Arial", 18, "bold"))
        title.pack(pady=20)

        btn_book = tk.Button(self.root, text="Book Ticket", width=30, command=self.book_ticket)
        btn_book.pack(pady=10)

        btn_view = tk.Button(self.root, text="View Available Buses", width=30, command=self.view_buses)
        btn_view.pack(pady=10)

        btn_cancel = tk.Button(self.root, text="Cancel Ticket", width=30, command=self.cancel_ticket)
        btn_cancel.pack(pady=10)

        btn_exit = tk.Button(self.root, text="Exit", width=30, command=self.root.quit)
        btn_exit.pack(pady=10)

    def book_ticket(self):
        self.run_cli_command("book")

    def view_buses(self):
        self.run_cli_command("view")

    def cancel_ticket(self):
        self.run_cli_command("cancel")

    def run_cli_command(self, command_type):
        try:
            result = subprocess.run(["python", "src/main.py", command_type], capture_output=True, text=True)
            messagebox.showinfo("Result", result.stdout)
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = ZingerDashboard(root)
    root.mainloop()
