import tkinter as tk
from tkinter import simpledialog, messagebox


class PersistentEntryDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)

        # Make this window stay on top
        self.transient(parent)
        self.grab_set()

        # Set window properties
        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # Create and place widgets
        tk.Label(self, text=prompt).pack(padx=10, pady=10)

        # Use Entry widget for single-line input
        self.entry = tk.Entry(self, width=40)
        self.entry.pack(padx=10, pady=10)

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(padx=10, pady=10)

        # OK and Cancel buttons
        tk.Button(button_frame, text="OK", width=10, command=self.ok).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Cancel", width=10, command=self.cancel).pack(
            side=tk.LEFT, padx=5
        )

        # Set focus to the entry
        self.entry.focus_set()

        # Center the window
        self.center_window()

        # Initialize result
        self.result = None

        # Wait for the window to be destroyed
        self.wait_window(self)

    def ok(self):
        # Get the text from the entry
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        # Set result to None and destroy the window
        self.result = None
        self.destroy()

    def center_window(self):
        # Update to ensure the window size is calculated
        self.update_idletasks()

        # Get the window size and screen dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the window position
        self.geometry(f"{width}x{height}+{x}+{y}")


def get_manual_data(
    root, title="Manual Entry", prompt="Please enter the data manually:"
):
    """
    Show a dialog to get manual data entry from the user.
    Returns the entered data or None if cancelled.
    """
    dialog = PersistentEntryDialog(root, title, prompt)
    return dialog.result


# Example usage:
if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    root.title("Form Scraper")
    root.geometry("400x300")
    root.attributes("-topmost", True)

    def simulate_error():
        # Simulate an error and ask for manual data entry
        data = get_manual_data(
            root,
            "Error Occurred",
            "The form data could not be scraped. Please enter it manually:",
        )
        if data:
            messagebox.showinfo("Data Received", f"Manual data entered: {data}")
        else:
            messagebox.showinfo("Cancelled", "Data entry was cancelled")

    # Add a button to simulate an error
    tk.Button(root, text="Simulate Error", command=simulate_error).pack(pady=20)

    # Start the main loop
    root.mainloop()
