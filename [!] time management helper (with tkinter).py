import pickle
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext

# --- Application Logic Functions (Unchanged) ---
def priority_score(task):
    """Calculates the priority score for a task."""
    priority_multiplier = 5 if task["priority"] else 1
    dampener = 5
    time = task["time"] + dampener
    score = round(priority_multiplier / time, 3)
    return score

def get_save_data():
    """Attempts to load previous data from pickle file."""
    try:
        with open("ProductivitySaveData.pkl", "rb") as file:
            imported_data = pickle.load(file)
        if not imported_data:
            return [], [], "No recovery data found."
        return imported_data["wants_list"], imported_data["needs_list"], f"Data found from {imported_data['date']}"
    except FileNotFoundError:
        return [], [], "Save file not found."
    except Exception:
        return [], [], "Save data file is corrupted."

def save_data(wants, needs):
    """Saves the current wants and needs lists to a pickle file."""
    now = datetime.now()
    save_date = now.strftime("%d/%m/%Y at %H:%M")
    
    dump_data = {"date": save_date, "wants_list": wants, "needs_list": needs}
    try:
        with open("ProductivitySaveData.pkl", "wb") as file:
            pickle.dump(dump_data, file)
        return "Save successful!"
    except Exception:
        return "ERROR: Could not save data to file."


# --- Tkinter GUI Class ---

class TimeManagementApp:
    def __init__(self, root, initial_wants, initial_needs):
        self.master = root 
        self.master.title("⏰ Time Management Helper")
        
        # Set minimum size for the window (900 pixels wide)
        self.master.minsize(900, 500) 
        
        # Initialize with the passed lists (which will be empty on startup)
        self.wants = initial_wants
        self.needs = initial_needs

        self.create_widgets()
        self.sort_and_display()

    def create_widgets(self):
        """Builds all the Tkinter widgets for the application."""
        
        # --- Frame for Task Input ---
        input_frame = tk.LabelFrame(self.master, text="➕ Add New Task", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new") 
        
        tk.Label(input_frame, text="Task Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.task_name_entry = tk.Entry(input_frame, width=30)
        self.task_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(input_frame, text="Time (mins 1-300):").grid(row=1, column=0, sticky="w", pady=2)
        self.task_time_entry = tk.Entry(input_frame, width=10)
        self.task_time_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        self.priority_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="High Priority (!)", variable=self.priority_var).grid(row=2, column=0, sticky="w", pady=5)
        
        self.type_var = tk.StringVar(value="need") 
        tk.Radiobutton(input_frame, text="Need to do", variable=self.type_var, value="need").grid(row=3, column=0, sticky="w")
        tk.Radiobutton(input_frame, text="Want to do", variable=self.type_var, value="want").grid(row=3, column=1, sticky="w")
        
        tk.Button(input_frame, text="Add Task", command=self.add_task, bg="light green").grid(row=4, column=0, columnspan=2, pady=10)

        # --- Frame for Task Display ---
        display_frame = tk.LabelFrame(self.master, text="📋 Task List (Sorted by Score)", padx=10, pady=10)
        display_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # WIDENED THE DISPLAY: width=80
        self.output_text = scrolledtext.ScrolledText(display_frame, width=80, height=20, wrap=tk.WORD) 
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True) 
        self.output_text.config(state=tk.DISABLED) 
        
        # --- Frame for Control Buttons ---
        control_frame = tk.LabelFrame(self.master, text="💾 Controls", padx=10, pady=10)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        tk.Button(control_frame, text="Save Data", command=self.save_current_data, width=15, bg="sky blue").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Sort/Display Tasks", command=self.sort_and_display, width=15, bg="yellow").grid(row=0, column=1, padx=5, pady=5)
        
        # MANUAL IMPORT BUTTON (STILL FUNCTIONAL)
        tk.Button(control_frame, text="Import Saved Data", command=self.import_data_manually, width=15, bg="#DDA0DD").grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(control_frame, text="Exit App", command=self.master.quit, width=15, bg="salmon").grid(row=1, column=1, padx=5, pady=5)
        
    def import_data_manually(self):
        """Allows manual import via button click, overwriting current lists."""
        
        response = messagebox.askyesno(
            "Manual Import",
            "This action will **REPLACE** all currently added tasks with the saved data.\nDo you want to proceed?"
        )

        if response:
            wants, needs, message = get_save_data()
            
            if message.startswith("Data found"):
                self.wants = wants
                self.needs = needs
                self.sort_and_display()
                messagebox.showinfo("Import Success", f"Successfully imported data. {message}")
            else:
                messagebox.showerror("Import Failed", f"Could not import data. {message}")


    def add_task(self):
        """Validates input, creates a task dictionary, and adds it to the list."""
        task_name = self.task_name_entry.get().strip().title()
        task_time_str = self.task_time_entry.get().strip()
        task_type = self.type_var.get()
        priority = self.priority_var.get()

        if not task_name:
            messagebox.showerror("Input Error", "Please enter a Task Name.")
            return

        try:
            task_time = int(task_time_str)
            if not 1 <= task_time <= 300:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a whole number between 1 and 300 for Time (minutes).")
            return

        new_task = {
            "time": task_time,
            "priority": priority,
            "name": task_name
        }

        if task_type == "need":
            self.needs.append(new_task)
        else:
            self.wants.append(new_task)

        self.task_name_entry.delete(0, tk.END)
        self.task_time_entry.delete(0, tk.END)
        self.priority_var.set(False)
        
        messagebox.showinfo("Task Added", f"Task '{task_name}' added successfully!")
        self.sort_and_display()

    def sort_and_display(self):
        """Calculates scores, sorts the lists, and updates the display area."""
        
        for task in self.needs:
            task["score"] = priority_score(task)
        for task in self.wants:
            task["score"] = priority_score(task)
            
        self.needs.sort(key=lambda task: task["score"], reverse=True)
        self.wants.sort(key=lambda task: task["score"], reverse=True)
        
        output = ""
        
        if self.needs:
            output += "--- NEEDS (High Priority) ---\n"
            for task in self.needs:
                priority_mark = " (!)" if task["priority"] else ""
                output += f"  {task['name']} ~ {task['time']} mins{priority_mark} (Score: {task['score']})\n"
        else:
            output += "--- NEEDS (High Priority) ---\n  No Need tasks added.\n"

        if self.wants:
            output += "\n--- WANTS (Lower Priority) ---\n"
            for task in self.wants:
                priority_mark = " (!)" if task["priority"] else ""
                output += f"  {task['name']} ~ {task['time']} mins{priority_mark} (Score: {task['score']})\n"
        else:
            output += "\n--- WANTS (Lower Priority) ---\n  No Want tasks added.\n"

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

    def save_current_data(self):
        """Handles the save button click."""
        response = messagebox.askyesno(
            "Confirm Save", 
            "WARNING: This will overwrite your previous save data.\nAre you sure you want to save the current task list?"
        )
        if response:
            result = save_data(self.wants, self.needs)
            if result.startswith("ERROR"):
                messagebox.showerror("Save Error", result)
            else:
                messagebox.showinfo("Save Status", result)


# --- Main Execution Block (No initial prompt) ---
if __name__ == "__main__":
    try:
        # 1. Start with empty lists - no data is loaded automatically
        initial_wants = []
        initial_needs = []
        
        # 2. Initialize the main root window
        root = tk.Tk() 
        
        # 3. Instantiate the app, passing the root window and empty data
        app = TimeManagementApp(root, initial_wants, initial_needs) 
        
        root.grid_columnconfigure(1, weight=1) 
        root.grid_rowconfigure(0, weight=1)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Failed to run the application: {e}")
