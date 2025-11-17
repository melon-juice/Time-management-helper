import pickle
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext

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


# Tkinter GUI Class (Modification in sort_and_display)

class TimeManagementApp:
    def __init__(self, root, initial_wants, initial_needs):
        self.master = root 
        self.master.title("⏰ Time Management Helper")
        
        self.master.minsize(900, 500) 
        
        self.wants = initial_wants
        self.needs = initial_needs
        self.current_tasks = [] 
        self.task_tags = {} 

        self.create_widgets()
        self.output_text.tag_config("completed", foreground="green")
        self.output_text.tag_config("heading_ul", underline=1)
        self.sort_and_display()

    def create_widgets(self):
        """Builds all the Tkinter widgets for the application."""
        
        input_frame = tk.LabelFrame(self.master, text="➕ Add New Task", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        
        tk.Label(input_frame, text="Task Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.task_name_entry = tk.Entry(input_frame, width=45) 
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

        # Frame for Task Display (Unchanged)
        display_frame = tk.LabelFrame(self.master, text="Task List (Enter ID to Complete/Delete)", padx=10, pady=10)
        display_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.output_text = tk.Text(display_frame, width=80, height=20, wrap=tk.WORD) 
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True) 
        self.output_text.config(state=tk.DISABLED) 
        
        # Frame for Control Buttons and Completion
        control_frame = tk.LabelFrame(self.master, text="Controls & Complete", padx=10, pady=10)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Completion Input and Button
        tk.Label(control_frame, text="Complete ID:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.completion_id_entry = tk.Entry(control_frame, width=5)
        self.completion_id_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        self.completion_id_entry.bind('<Return>', lambda event: self.complete_task())
        tk.Button(control_frame, text="Delete/Complete Task", command=self.complete_task, width=20, bg="#FFD700").grid(row=0, column=2, padx=5, pady=5) 
        
        # Save/Import Buttons
        tk.Button(control_frame, text="Save Data", command=self.save_current_data, width=15, bg="sky blue").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Sort/Display", command=self.sort_and_display, width=15, bg="yellow").grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(control_frame, text="Import Saved Data", command=self.import_data_manually, width=15, bg="#DDA0DD").grid(row=2, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Exit App", command=self.master.quit, width=15, bg="salmon").grid(row=2, column=1, padx=5, pady=5)
        
    def _perform_task_removal(self, task_to_remove):
        """Internal helper to remove the task from the main lists."""
        task_name = task_to_remove['name']
        task_type = task_to_remove['type']

        def is_match(t, target):
            return (t['name'] == target['name'] and 
                    t['time'] == target['time'] and 
                    t['priority'] == target['priority'])

        if task_type == 'need':
            self.needs[:] = [t for i, t in enumerate(self.needs) if i != next((j for j, item in enumerate(self.needs) if is_match(item, task_to_remove)), -1)]
        elif task_type == 'want':
            self.wants[:] = [t for i, t in enumerate(self.wants) if i != next((j for j, item in enumerate(self.wants) if is_match(item, task_to_remove)), -1)]
        
        self.sort_and_display()

    def complete_task(self):
        """Marks a task for animation, then schedules its removal."""
        
        task_id_str = self.completion_id_entry.get().strip()
        self.completion_id_entry.delete(0, tk.END)

        if not self.current_tasks:
            messagebox.showinfo("Error", "The task list is empty.")
            return

        try:
            task_id = int(task_id_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the Task ID.")
            return

        if 1 <= task_id <= len(self.current_tasks):
            task_to_remove = self.current_tasks[task_id - 1]
            task_tag = f"task_{task_id}" 

            # 1. Apply the red color tag
            self.output_text.config(state=tk.NORMAL)
            # Tag the entire line based on the unique tag index
            self.output_text.tag_add("completed", f"task_{task_id}.first", f"task_{task_id}.last") 
            self.output_text.config(state=tk.DISABLED)

            # 2. Schedule the actual removal and list refresh after 500 milliseconds (0.5s)
            self.master.after(500, lambda: self._perform_task_removal(task_to_remove))
        else:
            messagebox.showerror("Error", f"ID {task_id} is out of range. Please enter an ID from 1 to {len(self.current_tasks)}.")
            
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
        
        self.sort_and_display()

    def sort_and_display(self):
        """Calculates scores, sorts the lists, and updates the display area, hiding the score."""
        
        self.current_tasks = [] 
        task_id = 1
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)

        # NEEDS list processing
        for task in self.needs:
            task["score"] = priority_score(task)
        self.needs.sort(key=lambda task: task["score"], reverse=True)
        
        self.output_text.insert(tk.END, "You need to do:\n","heading_ul")
        for task in self.needs:
            priority_mark = " (!)" if task["priority"] else ""
            line = f" {task_id}. {task['name']} ~ {task['time']} mins{priority_mark}\n"
            
            self.output_text.insert(tk.END, line, f"task_{task_id}")
            
            self.current_tasks.append({'name': task['name'], 'time': task['time'], 'priority': task['priority'], 'type': 'need'})
            task_id += 1
        if not self.needs:
            self.output_text.insert(tk.END, " No Need tasks added.\n")


        # WANTS list processing
        for task in self.wants:
            task["score"] = priority_score(task)
        self.wants.sort(key=lambda task: task["score"], reverse=True)
        
        self.output_text.insert(tk.END, "\nYou want to do:\n","heading_ul")
        for task in self.wants:
            priority_mark = " (!)" if task["priority"] else ""
            line = f" {task_id}. {task['name']} ~ {task['time']} mins{priority_mark}\n"
            
            self.output_text.insert(tk.END, line, f"task_{task_id}")
            
            self.current_tasks.append({'name': task['name'], 'time': task['time'], 'priority': task['priority'], 'type': 'want'})
            task_id += 1
        if not self.wants:
            self.output_text.insert(tk.END, "  No Want tasks added.\n")

        # Update display
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


# Driver Code
if __name__ == "__main__":
    try:
        initial_wants = []
        initial_needs = []
        
        root = tk.Tk()
        root.option_add("*Font", "{Bahnschrift SemiLight} 10")
        app = TimeManagementApp(root, initial_wants, initial_needs) 
        
        root.grid_columnconfigure(1, weight=1) 
        root.grid_rowconfigure(0, weight=1)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Failed to run the application: {e}")
