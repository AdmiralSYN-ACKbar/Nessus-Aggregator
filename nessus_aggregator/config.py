import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import stat
import subprocess
from pathlib import Path

class Config:
    def __init__(self, nessus_url, access_key, secret_key, output_dir, script_dir, scan_type="current_month", days_back=0):
        self.nessus_url = nessus_url
        self.nessus_access_key = access_key
        self.nessus_secret_key = secret_key
        self.output_dir = output_dir
        self.script_dir = script_dir
        self.scan_type = scan_type
        self.days_back = days_back

class ConfigGenerator:
    def __init__(self, config):
        self.config = config
        self.setup_dir = Path(self.config.script_dir)
        if not self.setup_dir.exists():
            self.setup_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(self.setup_dir, os.W_OK):
            raise Exception(f"No write permission in directory: {self.setup_dir}")

    def generate_env_file(self):
        env_content = [
            "#!/bin/bash",
            f"export NESSUS_ACCESS_KEY='{self.config.nessus_access_key}'",
            f"export NESSUS_SECRET_KEY='{self.config.nessus_secret_key}'",
            f"export NESSUS_URL='{self.config.nessus_url}'",
            f"export NESSUS_OUTPUT_DIR='{self.config.output_dir}'",
            f"export NESSUS_SCAN_TYPE='{self.config.scan_type}'",
            f"export NESSUS_DAYS_BACK='{self.config.days_back}'"
        ]
        env_path = Path.home() / ".nessus_env"
        with open(env_path, 'w') as f:
            f.write('\n'.join(env_content))
        os.chmod(env_path, stat.S_IRUSR | stat.S_IWUSR)

    def generate_run_script(self):
        current_venv = os.environ.get('VIRTUAL_ENV')
        if not current_venv:
            raise Exception("No active virtual environment detected. Please run within a virtual environment.")
        
        nessus_aggregator_path = Path(__file__).parent / "nessus_aggregator.py"
    
        script_content = [
            "#!/bin/bash",
            "source ~/.nessus_env",
            f"source {current_venv}/bin/activate",
            f"python3 {nessus_aggregator_path}",
            "deactivate"
        ]
    
        script_path = self.setup_dir / "run_nessus_aggregator.sh"
        with open(script_path, 'w') as f:
            f.write('\n'.join(script_content))
        os.chmod(script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        return script_path

def generate_config(nessus_url, access_key, secret_key, output_dir, script_dir, scan_type, days_back, output_box, execute_button):
    try:
        config = Config(nessus_url, access_key, secret_key, output_dir, script_dir, scan_type, days_back)
        generator = ConfigGenerator(config)
        generator.generate_env_file()
        script_path = generator.generate_run_script()
        
        output_box.delete('1.0', tk.END)
        output_box.insert(tk.END, 
            f"Setup completed successfully!\n\n"
            f"Configuration file created at: {Path.home() / '.nessus_env'}\n"
            f"Run script location: {script_path}\n\n"
            f"To create aggregated report, run:\n"
            f"   ./run_nessus_aggregator.sh\n"
            f"or select Execute Run Script")
        
        execute_button.config(state=tk.NORMAL, bg="lightgrey", fg="red")
        execute_button.script_path = script_path
    except Exception as e:
        output_box.delete('1.0', tk.END)
        output_box.insert(tk.END, f"Error generating configuration: {str(e)}")

def execute_run_script(button):
    try:
        script_path = button.script_path
        subprocess.run([str(script_path)], check=True)
    except Exception as e:
        messagebox.showerror("Execution Error", f"Failed to execute run script: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Admiral SYN-ACKbar's Nessus Aggregator")
    root.geometry("700x650")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = ttk.Frame(root, padding="10 10 10 10")
    frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(8, weight=1)

    # Title
    title_label1 = ttk.Label(frame, text="Admiral SYN-ACKbar's", font=("Sylfaen", 14, "italic"))
    title_label1.grid(row=0, column=0, columnspan=3)
    title_label2 = ttk.Label(frame, text="Nessus Aggregator", font=("Sylfaen", 15, "bold"))
    title_label2.grid(row=1, column=0, columnspan=3)

    # Nessus Configuration
    nessus_label = ttk.Label(frame, text="Nessus URL:", font=("Sylfaen", 10, "bold"))
    nessus_label.grid(row=2, column=0, sticky=tk.W)
    nessus_url = ttk.Entry(frame, width=30)
    nessus_url.insert(0, "https://localhost:8834")
    nessus_url.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))

    access_label = ttk.Label(frame, text="Access Key:", font=("Sylfaen", 10, "bold"))
    access_label.grid(row=3, column=0, sticky=tk.W)
    access_key = ttk.Entry(frame, width=30, show="*")
    access_key.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E))

    secret_label = ttk.Label(frame, text="Secret Key:", font=("Sylfaen", 10, "bold"))
    secret_label.grid(row=4, column=0, sticky=tk.W)
    secret_key = ttk.Entry(frame, width=30, show="*")
    secret_key.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E))

    # Output Directory
    output_label = ttk.Label(frame, text="Output Directory:", font=("Sylfaen", 10, "bold"))
    output_label.grid(row=5, column=0, sticky=tk.W)
    output_dir = ttk.Entry(frame, width=30)
    output_dir.insert(0, str(Path.home() / "nessus_output"))
    output_dir.grid(row=5, column=1, sticky=(tk.W, tk.E))
    browse_button = ttk.Button(frame, text="Browse", 
                             command=lambda: output_dir.delete(0, tk.END) or output_dir.insert(0, filedialog.askdirectory()))
    browse_button.grid(row=5, column=2, sticky=tk.W)

    # Script Directory
    script_label = ttk.Label(frame, text="Script Location:", font=("Sylfaen", 10, "bold"))
    script_label.grid(row=6, column=0, sticky=tk.W)
    script_dir = ttk.Entry(frame, width=30)
    script_dir.insert(0, str(Path.cwd()))
    script_dir.grid(row=6, column=1, sticky=(tk.W, tk.E))
    script_browse_button = ttk.Button(frame, text="Browse", 
                                    command=lambda: script_dir.delete(0, tk.END) or 
                                    script_dir.insert(0, filedialog.askdirectory()))
    script_browse_button.grid(row=6, column=2, sticky=tk.W)

    # Scan Time Configuration
    scan_time_frame = ttk.LabelFrame(frame, text="Scan Time Range", padding="5 5 5 5")
    scan_time_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    scan_type = tk.StringVar(value="current_month")
    days_back = tk.StringVar(value="30")
    
    ttk.Radiobutton(scan_time_frame, text="Current Month", 
                    variable=scan_type, 
                    value="current_month",
                    command=lambda: days_entry.configure(state="disabled")).grid(row=0, column=0, sticky=tk.W)
    
    prev_days_frame = ttk.Frame(scan_time_frame)
    prev_days_frame.grid(row=1, column=0, sticky=tk.W)
    
    ttk.Radiobutton(prev_days_frame, text="Previous", 
                    variable=scan_type,
                    value="days_back",
                    command=lambda: days_entry.configure(state="normal")).grid(row=0, column=0)
    
    days_entry = ttk.Entry(prev_days_frame, width=5, textvariable=days_back)
    days_entry.grid(row=0, column=1, padx=5)
    days_entry.configure(state="disabled")
    
    ttk.Label(prev_days_frame, text="Days").grid(row=0, column=2)

    # Generate Button
    generate_button = tk.Button(frame, text="ENGAGE", 
                              command=lambda: generate_config(nessus_url.get(), 
                                                           access_key.get(),
                                                           secret_key.get(),
                                                           output_dir.get(),
                                                           script_dir.get(),
                                                           scan_type.get(),
                                                           days_back.get(),
                                                           output_box,
                                                           execute_button),
                              width=20, font=("Sylfaen", 14, "bold"), 
                              foreground="blue")
    generate_button.grid(row=8, column=1, pady=10, padx=(5, 0))

    # Execute Run Script Button
    execute_button = tk.Button(frame, text="Execute Run Script", state=tk.DISABLED, bg="lightgrey", fg="red", 
                               command=lambda: execute_run_script(execute_button))
    execute_button.grid(row=8, column=2, pady=10, padx=(5, 0))

    # Status Box
    status_frame = ttk.LabelFrame(frame, text="Status", padding="5 5 5 5")
    status_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
    status_frame.columnconfigure(0, weight=1)
    status_frame.rowconfigure(0, weight=1)

    output_box = tk.Text(status_frame, width=50, height=10)
    output_box.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

    scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=output_box.yview)
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    output_box.configure(yscrollcommand=scrollbar.set)

    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()