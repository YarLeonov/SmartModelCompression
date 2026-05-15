#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path

# Import our refactored logic
from compress import run_compression
from decompress import run_decompression

class GeomodelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Geomodel Compression Tool")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam' looks a bit better than 'alt' or 'default'
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.create_compression_tab()
        self.create_decompression_tab()
        
    def create_compression_tab(self):
        self.comp_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.comp_tab, text="Compression")
        
        # Input Directory
        ttk.Label(self.comp_tab, text="Model Directory:").grid(row=0, column=0, sticky="w", padx=10, pady=(20, 5))
        self.comp_input_var = tk.StringVar()
        ttk.Entry(self.comp_tab, textvariable=self.comp_input_var, width=50).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(self.comp_tab, text="Browse...", command=self.browse_comp_input).grid(row=1, column=1, padx=5, pady=5)
        
        # Output File
        ttk.Label(self.comp_tab, text="Destination Archive (.tar.gz):").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 5))
        self.comp_output_var = tk.StringVar()
        ttk.Entry(self.comp_tab, textvariable=self.comp_output_var, width=50).grid(row=3, column=0, padx=10, pady=5)
        ttk.Button(self.comp_tab, text="Save As...", command=self.browse_comp_output).grid(row=3, column=1, padx=5, pady=5)
        
        # Progress
        self.comp_progress_var = tk.DoubleVar()
        self.comp_progress_bar = ttk.Progressbar(self.comp_tab, variable=self.comp_progress_var, maximum=100)
        self.comp_progress_bar.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=20)
        
        self.comp_status_var = tk.StringVar(value="Ready")
        ttk.Label(self.comp_tab, textvariable=self.comp_status_var).grid(row=5, column=0, columnspan=2, padx=10)
        
        # Start Button
        self.comp_btn = ttk.Button(self.comp_tab, text="Start Compression", command=self.start_compression)
        self.comp_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def create_decompression_tab(self):
        self.decomp_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.decomp_tab, text="Decompression")
        
        # Input File
        ttk.Label(self.decomp_tab, text="Compressed Model (.tar.gz):").grid(row=0, column=0, sticky="w", padx=10, pady=(20, 5))
        self.decomp_input_var = tk.StringVar()
        ttk.Entry(self.decomp_tab, textvariable=self.decomp_input_var, width=50).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(self.decomp_tab, text="Browse...", command=self.browse_decomp_input).grid(row=1, column=1, padx=5, pady=5)
        
        # Output Directory
        ttk.Label(self.decomp_tab, text="Extraction Directory:").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 5))
        self.decomp_output_var = tk.StringVar()
        ttk.Entry(self.decomp_tab, textvariable=self.decomp_output_var, width=50).grid(row=3, column=0, padx=10, pady=5)
        ttk.Button(self.decomp_tab, text="Browse...", command=self.browse_decomp_output).grid(row=3, column=1, padx=5, pady=5)
        
        # Progress
        self.decomp_progress_var = tk.DoubleVar()
        self.decomp_progress_bar = ttk.Progressbar(self.decomp_tab, variable=self.decomp_progress_var, maximum=100)
        self.decomp_progress_bar.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=20)
        
        self.decomp_status_var = tk.StringVar(value="Ready")
        ttk.Label(self.decomp_tab, textvariable=self.decomp_status_var).grid(row=5, column=0, columnspan=2, padx=10)
        
        # Start Button
        self.decomp_btn = ttk.Button(self.decomp_tab, text="Start Decompression", command=self.start_decompression)
        self.decomp_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def browse_comp_input(self):
        path = filedialog.askdirectory()
        if path: self.comp_input_var.set(path)
        
    def browse_comp_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".tar.gz", filetypes=[("Archive files", "*.tar.gz")])
        if path: self.comp_output_var.set(path)
        
    def browse_decomp_input(self):
        path = filedialog.askopenfilename(filetypes=[("Archive files", "*.tar.gz")])
        if path: self.decomp_input_var.set(path)
        
    def browse_decomp_output(self):
        path = filedialog.askdirectory()
        if path: self.decomp_output_var.set(path)

    def update_progress(self, current, total, message, progress_var, status_var):
        percent = (current / total) * 100
        progress_var.set(percent)
        status_var.set(f"{message}... ({int(percent)}%)")
        self.root.update_idletasks()

    def start_compression(self):
        input_path = self.comp_input_var.get()
        output_path = self.comp_output_var.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input directory and output file.")
            return
            
        self.comp_btn.config(state="disabled")
        threading.Thread(target=self.run_comp_thread, args=(input_path, output_path), daemon=True).start()
        
    def run_comp_thread(self, input_path, output_path):
        try:
            run_compression(input_path, output_path, 
                           lambda c, t, m: self.update_progress(c, t, m, self.comp_progress_var, self.comp_status_var))
            messagebox.showinfo("Success", "Compression completed successfully!")
            self.comp_status_var.set("Ready")
            self.comp_progress_var.set(0)
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {str(e)}")
        finally:
            self.comp_btn.config(state="normal")

    def start_decompression(self):
        input_path = self.decomp_input_var.get()
        output_path = self.decomp_output_var.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input file and output directory.")
            return
            
        self.decomp_btn.config(state="disabled")
        threading.Thread(target=self.run_decomp_thread, args=(input_path, output_path), daemon=True).start()
        
    def run_decomp_thread(self, input_path, output_path):
        try:
            run_decompression(input_path, output_path, 
                             lambda c, t, m: self.update_progress(c, t, m, self.decomp_progress_var, self.decomp_status_var))
            messagebox.showinfo("Success", "Decompression completed successfully!")
            self.decomp_status_var.set("Ready")
            self.decomp_progress_var.set(0)
        except Exception as e:
            messagebox.showerror("Error", f"Decompression failed: {str(e)}")
        finally:
            self.decomp_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeomodelGUI(root)
    root.mainloop()
