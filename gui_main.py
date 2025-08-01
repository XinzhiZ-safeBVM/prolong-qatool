import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import webbrowser
from pathlib import Path
import sys
import os
import subprocess

# Import the main processing function
from main import process_raw_data_and_generate_report

class ProlongReportToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Prolong Report Tool - CSV Analysis")
        self.root.geometry("600x580")
        self.root.resizable(True, True)
        
        # Variables
        self.selected_file = tk.StringVar()
        self.is_processing = False
        self.git_hash = self.get_git_hash()
        
        self.setup_ui()
        
    def get_git_hash(self):
        """Get the current git commit hash"""
        # First, try to read from a version file (for PyInstaller builds)
        try:
            version_file = Path(__file__).parent / 'version.txt'
            if version_file.exists():
                with open(version_file, 'r') as f:
                    return f.read().strip()
        except Exception:
            pass
        
        # Fallback to git command (for development)
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Prolong Report Tool - CSV Analysis", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Version info
        version_text = f"Version: {self.git_hash[:8] if self.git_hash else 'Unknown'}"
        version_label = tk.Label(main_frame, text=version_text, 
                                font=("Arial", 9), fg="gray")
        version_label.pack(pady=(0, 15))
        
        # File selection frame
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(file_frame, text="Select CSV File:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        file_select_frame = tk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.file_entry = tk.Entry(file_select_frame, textvariable=self.selected_file, 
                                  state="readonly", font=("Arial", 9))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_button = tk.Button(file_select_frame, text="Browse", 
                                      command=self.browse_file, width=10)
        self.browse_button.pack(side=tk.RIGHT)
        
        # Run analysis button
        self.run_button = tk.Button(main_frame, text="Run Analysis", 
                                   command=self.run_analysis, 
                                   font=("Arial", 12, "bold"),
                                   bg="#4CAF50", fg="white",
                                   height=2, width=15)
        self.run_button.pack(pady=(0, 20))
        
        # Progress and output frame
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(output_frame, text="Processing Output:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Text area for output
        self.output_text = scrolledtext.ScrolledText(output_frame, 
                                                    height=15, 
                                                    font=("Consolas", 9),
                                                    wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def browse_file(self):
        """Open file dialog to select CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir="rawfile_sample" if Path("rawfile_sample").exists() else "."
        )
        
        if file_path:
            self.selected_file.set(file_path)
            self.log_output(f"Selected file: {file_path}")
            
    def log_output(self, message):
        """Add message to output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        
    def set_processing_state(self, processing):
        """Enable/disable UI elements during processing"""
        self.is_processing = processing
        state = tk.DISABLED if processing else tk.NORMAL
        
        self.browse_button.config(state=state)
        self.run_button.config(state=state)
        
        if processing:
            self.status_var.set("Processing...")
            self.run_button.config(text="Processing...", bg="#FF9800")
        else:
            self.status_var.set("Ready")
            self.run_button.config(text="Run Analysis", bg="#4CAF50")
            
    def run_analysis(self):
        """Run the analysis in a separate thread"""
        if not self.selected_file.get():
            messagebox.showerror("Error", "Please select a CSV file first.")
            return
            
        if not Path(self.selected_file.get()).exists():
            messagebox.showerror("Error", "Selected file does not exist.")
            return
            
        # Clear previous output
        self.clear_output()
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_file)
        thread.daemon = True
        thread.start()
        
    def process_file(self):
        """Process the selected file"""
        try:
            self.set_processing_state(True)
            
            file_path = self.selected_file.get()
            self.log_output(f"Starting analysis of: {Path(file_path).name}")
            self.log_output("=" * 50)
            
            # Create custom output directory next to the CSV file
            csv_dir = Path(file_path).parent
            output_dir = csv_dir / "html_report"
            self.log_output(f"Output directory: {output_dir}")
            
            # Redirect stdout to capture print statements
            original_stdout = sys.stdout
            
            class OutputCapture:
                def __init__(self, gui):
                    self.gui = gui
                    
                def write(self, text):
                    if text.strip():  # Only log non-empty lines
                        self.gui.log_output(text.strip())
                    # Don't write to original stdout to avoid duplicate messages
                    
                def flush(self):
                    pass  # No need to flush since we're not writing to stdout
                    
            sys.stdout = OutputCapture(self)
            
            # Run the analysis with custom output directory
            success = process_raw_data_and_generate_report(file_path, str(output_dir))
            
            # Restore stdout
            sys.stdout = original_stdout
            
            if success:
                self.log_output("\n" + "=" * 50)
                self.log_output("✓ Analysis completed successfully!")
                
                # Find and open the HTML report
                self.open_html_report(file_path, str(output_dir))
            else:
                self.log_output("\n" + "=" * 50)
                self.log_output("✗ Analysis failed!")
                messagebox.showerror("Error", "Analysis failed. Check the output for details.")
                
        except Exception as e:
            self.log_output(f"\nError: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Restore stdout if it was changed
            sys.stdout = original_stdout
            self.set_processing_state(False)
            
    def open_html_report(self, raw_file_path, output_dir="output"):
        """Open the generated HTML report in the default browser"""
        try:
            input_filename = Path(raw_file_path).stem
            html_file_path = Path(output_dir) / f"vt_report_{input_filename}.html"
            
            if html_file_path.exists():
                # Convert to absolute path for browser
                abs_path = html_file_path.resolve()
                webbrowser.open(f"file:///{abs_path}")
                self.log_output(f"Opened HTML report: {html_file_path}")
            else:
                self.log_output(f"HTML report not found: {html_file_path}")
                
        except Exception as e:
            self.log_output(f"Error opening HTML report: {str(e)}")

def main():
    root = tk.Tk()
    app = ProlongReportToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()