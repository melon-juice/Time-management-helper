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
            
        if not imported_data: #"No recovery data found."
            return [], [], []

        return imported_data["wants_list"], imported_data["needs_list"], imported_data['date']

    except FileNotFoundError: #"Save file not found."
        return [], [], []
    
    except Exception: #"Save data file is corrupted."
        return [], [], []

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


# Tkinter GUI Class
class TimeManagementApp:
    def __init__(self, root, initial_wants, initial_needs):
        self.master = root
        self.master.title("Time Management Helper")
        
        self.master.minsize(900, 500)
        self.master.geometry("1200x500")
        
        self.wants = initial_wants
        self.needs = initial_needs
        self.current_tasks = []
        self.task_tags = {}
        
        self.create_widgets()
        self.output_text.tag_config("completed", foreground="green", font="{Yu Gothic} 11 bold")
        self.output_text.tag_config("heading_ul", underline=1)
        self.sort_and_display()

    def exit_application(self):
        """Asks the user if they want to save before closing."""
        
        response = messagebox.askyesnocancel(
            "Exit App", 
            "Do you want to save your current task list before exiting?"
        )
        
        if response is True:
            #User chose 'Yes' (save)
            self.save_current_data()
            self.master.destroy() 
        elif response is False:
            #User chose 'No' (don't save)
            self.master.destroy() 
        #If response is None (Cancel), the window stays open
        
    def create_widgets(self):
        """Tkinter GUI used for the application"""
        
        input_frame = tk.LabelFrame(self.master, text="  Add New Task  ", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        
        tk.Label(input_frame, text="Task Name:").grid(row=0, column=0, pady=2, sticky="w")
        self.task_name_entry = tk.Entry(input_frame, width=25)
        self.task_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Time (mins):").grid(row=1, column=0, sticky="w", pady=2)
        self.task_time_entry = tk.Entry(input_frame, width=10)
        self.task_time_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        self.priority_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="High Priority?", variable=self.priority_var).grid(row=2, column=0, sticky="w", pady=5)
        
        self.type_var = tk.StringVar(value="need")
        tk.Radiobutton(input_frame, text="Need to do", variable=self.type_var, value="need").grid(row=3, column=0, sticky="w")
        tk.Radiobutton(input_frame, text="Want to do", variable=self.type_var, value="want").grid(row=3, column=1, sticky="w")
        
        tk.Button(input_frame, text="Add Task", command=self.add_task, bg="#0C8F96",fg="white").grid(row=4, column=0, columnspan=2, pady=10)

        # Frame for Task Display
        display_frame = tk.LabelFrame(self.master, text="  Task List  ", padx=10, pady=10)
        display_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.output_text = tk.Text(display_frame, width=65, height=20, wrap=tk.WORD)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
        
        # ADDED: Time Summary Label
        self.time_summary_label = tk.Label(display_frame, text="Estimated Time: 0 mins", anchor="w", font="{Bahnschrift SemiLight} 10")
        self.time_summary_label.pack(pady=(5, 0), fill=tk.X)
    

        # Frame for Control Buttons and Completion
        control_frame = tk.LabelFrame(self.master, text="  Controls  ", padx=10, pady=10)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Completion Input and Button
        tk.Label(control_frame, text="Completed Task ID:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.completion_id_entry = tk.Entry(control_frame, width=8)
        self.completion_id_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        self.completion_id_entry.bind('<Return>', lambda event: self.complete_task())

        tk.Button(control_frame, text="Tick off!", command=self.complete_task, width=15, bg="#354871", fg="white").grid(row=0, column=2, padx=15, pady=5, sticky="e")
        control_frame.grid_columnconfigure(2, weight=1)

        # Edit Task Input and Button
        tk.Label(control_frame, text="Edit Task ID:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.edit_id_entry = tk.Entry(control_frame, width=8)
        self.edit_id_entry.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        self.edit_id_entry.bind('<Return>', lambda event: self.edit_task())
        
        tk.Button(control_frame, text="Edit Task", command=self.edit_task, width=15, bg="#B0C4DE").grid(row=1, column=2, padx=15, pady=5, sticky="e")

        separator = tk.Frame(control_frame, height=2, bd=1, relief=tk.SUNKEN, bg="light grey")
        separator.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 5))
        
        tk.Button(control_frame, text="Save Current Data", command=self.save_current_data, width=20, bg="#7D3096", fg="white").grid(row=3, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Clear Tasks", command=self.clear_all_data, width=15, bg="#AA1730", fg="white").grid(row=3, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Import Previous Data", command=self.import_data_manually, width=20,bg="#E488DF", fg="black").grid(row=4, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Exit App", command=self.exit_application, width=15, bg="#FA8072").grid(row=4, column=1, padx=5, pady=5)

    def clear_all_data(self):
        """Clears all tasks (wants and needs) from the current session."""
        
        if not (self.wants or self.needs):
            messagebox.showinfo("Info", "The task lists are already empty.")
            return
            
        response = messagebox.askyesno(
            "Confirm Clear",
            """WARNING: This will DELETE all tasks within the task window\n
You may want to save before proceeding!)\nDo you want to proceed?"""
        )
        
        if response:
            self.wants.clear()
            self.needs.clear()
            self.sort_and_display()
            messagebox.showinfo("Success", "Task window cleared.")
            
    def _perform_task_removal(self, task_to_remove):
        """Internal helper to remove the task from the main lists."""
        task_name = task_to_remove['name']
        task_type = task_to_remove['type']
        
        def is_match(t, target):
            return (t['name'] == target['name'] and 
                    t['time'] == target['time'] and 
                    t['priority'] == target['priority'])

        # Find the index of the first matching task
        target_list = self.needs if task_type == 'need' else self.wants
        try:
            index_to_remove=next(i for i, item in enumerate(target_list) if is_match(item, task_to_remove))
            del target_list[index_to_remove]
        except StopIteration:
            # Should not happen if called correctly, but handles case where task is missing
            pass
        
        self.sort_and_display()

    def edit_task(self):
        """Prepares to edit a task based on its ID."""
        task_id_str = self.edit_id_entry.get().strip()
        self.edit_id_entry.delete(0, tk.END)

        if not self.current_tasks:
            messagebox.showinfo("Error", "The task list is empty. Nothing to edit.")
            return

        try:
            task_id = int(task_id_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the Task ID to edit.")
            return

        if 1 <= task_id <= len(self.current_tasks):
            task_to_edit = self.current_tasks[task_id - 1]
            # Open the edit pop-up window
            self._open_edit_window(task_to_edit, task_id)
        else:
            messagebox.showerror("Error", f"ID {task_id} is out of range. Please enter an ID from 1 to {len(self.current_tasks)}.")
    
    def _open_edit_window(self, task, original_id):
        """Creates a new window for editing a task."""
        edit_window = tk.Toplevel(self.master)
        edit_window.title(f"Edit Task {original_id}")
        edit_window.grab_set() # Modal window
        edit_window.transient(self.master)

        edit_frame = tk.LabelFrame(edit_window, text=f"Edit Task: {task['name']}", padx=10, pady=10)
        edit_frame.pack(padx=20, pady=20)

        # Name
        tk.Label(edit_frame, text="Task Name:").grid(row=0, column=0, pady=2, sticky="ew")
        edit_name_var = tk.StringVar(value=task['name'])
        tk.Entry(edit_frame, width=25, textvariable=edit_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Time
        tk.Label(edit_frame, text="Time (mins):").grid(row=1, column=0, sticky="w", pady=2)
        edit_time_var = tk.StringVar(value=str(task['time']))
        tk.Entry(edit_frame, width=10, textvariable=edit_time_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Priority
        edit_priority_var = tk.BooleanVar(value=task['priority'])
        tk.Checkbutton(edit_frame, text="High Priority?", variable=edit_priority_var).grid(row=2, column=0, sticky="w", pady=5)
        
        # Type (Need/Want)
        edit_type_var = tk.StringVar(value=task['type'])
        tk.Radiobutton(edit_frame, text="Need to do", variable=edit_type_var, value="need").grid(row=3, column=0, sticky="w")
        tk.Radiobutton(edit_frame, text="Want to do", variable=edit_type_var, value="want").grid(row=3, column=1, sticky="w")
        
        # Save Button
        tk.Button(edit_frame, text="Save Changes", bg="#98FB98", 
                  command=lambda: self._save_edited_task(original_id, edit_name_var.get(), 
                                                        edit_time_var.get(), edit_priority_var.get(), 
                                                        edit_type_var.get(), edit_window)).grid(row=4, column=0, columnspan=2, pady=10)
        
    def _save_edited_task(self, original_id, new_name, new_time_str, new_priority, new_type, edit_window):
        """Validates and saves the edited task."""

        new_name = new_name.strip()
        if not new_name:
            messagebox.showerror("Input Error", "Please enter a Task Name.", parent=edit_window)
            return
        
        try:
            new_time = int(new_time_str)
            if not 1 <= new_time <= 300:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a whole number between 1 and 300 for Time (minutes).", parent=edit_window)
            return

        # 1. Remove the original task from its list using its data from current_tasks
        old_task_data = self.current_tasks[original_id - 1]
        
        # Determine the correct list and index to remove from self.needs or self.wants
        target_list = self.needs if old_task_data['type'] == 'need' else self.wants
        
        def is_match(t, target):
            return (t['name'] == target['name'] and 
                    t['time'] == target['time'] and 
                    t['priority'] == target['priority'])
            
        try:
            index_to_remove = next(i for i, item in enumerate(target_list) if is_match(item, old_task_data))
            del target_list[index_to_remove]
        except StopIteration:
            messagebox.showwarning("Warning", "Original task could not be found for removal.", parent=edit_window)
            
        # 2. Create and add the new/edited task
        new_task = {
            "time": new_time,
            "priority": new_priority,
            "name": new_name
        }

        if new_type == "need":
            self.needs.append(new_task)
        else:
            self.wants.append(new_task)

        # 3. Close window and refresh
        edit_window.destroy()
        self.sort_and_display()
        messagebox.showinfo("Success", f"Task {original_id} successfully updated.")

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
            
            # Apply the color tag for the visual confirmation
            self.output_text.config(state=tk.NORMAL)
            insert_index = f"task_{task_id}.first"
            self.output_text.insert(insert_index, "✅ ")
            # Tag the entire line based on the unique tag index
            self.output_text.tag_add("completed", f"task_{task_id}.first", f"task_{task_id}.last")
            self.output_text.config(state=tk.DISABLED)

            # Schedule the actual removal and list refresh after 1 second (1000 milliseconds)
            self.master.after(1000, lambda: self._perform_task_removal(task_to_remove))
        else:
            messagebox.showerror("Error", f"ID {task_id} is out of range. Please enter an ID from 1 to {len(self.current_tasks)}.")
            
    def import_data_manually(self):
        """Allows user to import previous save data, overwriting current lists."""
        wants, needs, date = get_save_data()

        if self.wants==wants and self.needs==needs:
            response = messagebox.showinfo(
            "Importing Save Data",
            f"Import Unecessary.\nThe save data (from:{date}) is identical to your current tasks.")

        else:

            if date:
                response = messagebox.askyesno(
                "Importing Save Data",
                f"Data found from {date}.\nDo you want to proceed?\n\nWarning: this will replace currently added tasks.")
                                
                if response:
                    self.wants=wants
                    self.needs=needs
                    self.sort_and_display()
                    #messagebox.showinfo("Import Success","Successfully imported data.")
            else:
                messagebox.showerror("Import Failed.","Could not import data.")

        
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
        """Calculates scores, sorts the lists, updates the display area, and updates the time summary."""
        
        self.current_tasks = []
        task_id = 1
        total_need_time = 0
        total_want_time = 0
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)

        # NEEDS list processing
        for task in self.needs:
            task["score"] = priority_score(task)
            total_need_time += task['time']
        self.needs.sort(key=lambda task: task["score"], reverse=True)
        
        self.output_text.insert(tk.END, "You need to do:\n","heading_ul")
        for task in self.needs:
            priority_mark = " (!)" if task["priority"] else ""
            line = f" {task_id}. {task['name']} ~ {task['time']} mins{priority_mark}\n"
            
            self.output_text.insert(tk.END, line, f"task_{task_id}")
            
            # Store full task details for removal/editing
            self.current_tasks.append({'name': task['name'], 'time': task['time'], 'priority': task['priority'], 'type': 'need'})
            task_id += 1
        if not self.needs:
            self.output_text.insert(tk.END, " No Need tasks added.\n")


        # WANTS list processing
        for task in self.wants:
            task["score"] = priority_score(task)
            total_want_time += task['time']
        self.wants.sort(key=lambda task: task["score"], reverse=True)
        
        self.output_text.insert(tk.END, "\nYou want to do:\n","heading_ul")
        for task in self.wants:
            priority_mark = " (!)" if task["priority"] else ""
            line = f" {task_id}. {task['name']} ~ {task['time']} mins{priority_mark}\n"
            
            self.output_text.insert(tk.END, line, f"task_{task_id}")
            
            # Store full task details for removal/editing
            self.current_tasks.append({'name': task['name'], 'time': task['time'], 'priority': task['priority'], 'type': 'want'})
            task_id += 1
        if not self.wants:
            self.output_text.insert(tk.END, "  No Want tasks added.\n")

        # Update display
        self.output_text.config(state=tk.DISABLED)
        
        total_time_mins = total_need_time + total_want_time
        
        def convert_minutes_to_h_m(total_minutes):
            """Converts total minutes into a string format: X hours Y minutes."""
            if total_minutes < 60:
                return f"{total_minutes} mins"
            
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            h_label = "hour" if hours == 1 else "hours"
            m_label = "min" if minutes == 1 else "mins"
            
            if minutes == 0:
                return f"{hours} {h_label}"
            else:
                return f"{hours} {h_label}, {minutes} {m_label}"

        total_time_h_m = convert_minutes_to_h_m(total_time_mins)
        need_time_h_m = convert_minutes_to_h_m(total_need_time)
        want_time_h_m = convert_minutes_to_h_m(total_want_time)
        
        summary_text = f"Estimated Time: Needs: {need_time_h_m} | Wants: {want_time_h_m} | Total: {total_time_h_m}"
        self.time_summary_label.config(text=summary_text)


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
        root.option_add("*Font", "{Bahnschrift SemiLight} 12")
        app = TimeManagementApp(root, initial_wants, initial_needs)
        
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        
        root.mainloop()
        
    except Exception as e:
        print(f"Failed to run the application: {e}")
