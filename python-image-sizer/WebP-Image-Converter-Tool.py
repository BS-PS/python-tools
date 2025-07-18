"""
Description: WebP Image Converter Tool
Author: Brian Stephens
Date: 18/07/2024
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
from PIL import Image, ImageTk
import threading
from pathlib import Path
import math




class WebPConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("WEBP Image Converter")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.quality = tk.IntVar(value=80)
        self.size_reduction = tk.IntVar(value=0)
        self.resize_mode = tk.StringVar(value="percentage")  # "percentage" or "preset"
        self.preset_size = tk.StringVar(value="1200x800")
        self.selected_files = []
        self.output_folder = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="WEBP Image Converter", 
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#2563eb'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Convert your images to optimized WebP format",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        subtitle_label.pack()
        
        # Settings Frame
        settings_frame = tk.LabelFrame(
            self.root, 
            text="Conversion Settings", 
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        settings_frame.pack(pady=10, padx=20, fill='x')
        
        # Quality setting
        quality_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        quality_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(
            quality_frame, 
            text="Quality:", 
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w')
        
        quality_control_frame = tk.Frame(quality_frame, bg='#f0f0f0')
        quality_control_frame.pack(fill='x', pady=5)
        
        self.quality_scale = tk.Scale(
            quality_control_frame,
            from_=10,
            to=100,
            orient='horizontal',
            variable=self.quality,
            bg='#f0f0f0',
            fg='#333333',
            highlightthickness=0
        )
        self.quality_scale.pack(side='left', fill='x', expand=True)
        
        self.quality_label = tk.Label(
            quality_control_frame,
            text="80%",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#2563eb',
            width=5
        )
        self.quality_label.pack(side='right', padx=(10, 0))
        
        self.quality.trace('w', self.update_quality_label)
        
        # Size reduction setting
        size_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        size_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(
            size_frame, 
            text="Resize Options:", 
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w')
        
        # Radio buttons for resize mode
        resize_mode_frame = tk.Frame(size_frame, bg='#f0f0f0')
        resize_mode_frame.pack(fill='x', pady=5)
        
        percentage_radio = tk.Radiobutton(
            resize_mode_frame,
            text="Percentage Reduction",
            variable=self.resize_mode,
            value="percentage",
            command=self.toggle_resize_mode,
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        percentage_radio.pack(side='left', padx=(0, 20))
        
        preset_radio = tk.Radiobutton(
            resize_mode_frame,
            text="Preset Dimensions",
            variable=self.resize_mode,
            value="preset",
            command=self.toggle_resize_mode,
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        preset_radio.pack(side='left')
        
        # Percentage control frame
        self.percentage_frame = tk.Frame(size_frame, bg='#f0f0f0')
        self.percentage_frame.pack(fill='x', pady=5)
        
        size_control_frame = tk.Frame(self.percentage_frame, bg='#f0f0f0')
        size_control_frame.pack(fill='x')
        
        tk.Label(
            size_control_frame,
            text="Size Reduction:",
            font=('Arial', 9),
            bg='#f0f0f0'
        ).pack(anchor='w')
        
        size_slider_frame = tk.Frame(size_control_frame, bg='#f0f0f0')
        size_slider_frame.pack(fill='x', pady=2)
        
        self.size_scale = tk.Scale(
            size_slider_frame,
            from_=0,
            to=70,
            orient='horizontal',
            variable=self.size_reduction,
            bg='#f0f0f0',
            fg='#333333',
            highlightthickness=0
        )
        self.size_scale.pack(side='left', fill='x', expand=True)
        
        self.size_label = tk.Label(
            size_slider_frame,
            text="0%",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#2563eb',
            width=5
        )
        self.size_label.pack(side='right', padx=(10, 0))
        
        self.size_reduction.trace('w', self.update_size_label)
        
        # Preset dimensions frame
        self.preset_frame = tk.Frame(size_frame, bg='#f0f0f0')
        
        preset_control_frame = tk.Frame(self.preset_frame, bg='#f0f0f0')
        preset_control_frame.pack(fill='x')
        
        tk.Label(
            preset_control_frame,
            text="Target Size:",
            font=('Arial', 9),
            bg='#f0f0f0'
        ).pack(anchor='w')
        
        preset_dropdown_frame = tk.Frame(preset_control_frame, bg='#f0f0f0')
        preset_dropdown_frame.pack(fill='x', pady=2)
        
        preset_sizes = ["1200x800", "800x500", "600x400", "400x300"]
        self.preset_dropdown = ttk.Combobox(
            preset_dropdown_frame,
            textvariable=self.preset_size,
            values=preset_sizes,
            state="readonly",
            font=('Arial', 10),
            width=15
        )
        self.preset_dropdown.pack(side='left')
        
        info_label = tk.Label(
            preset_dropdown_frame,
            text="(maintains aspect ratio)",
            font=('Arial', 8),
            bg='#f0f0f0',
            fg='#666666'
        )
        info_label.pack(side='left', padx=(10, 0))
        
        # Initially show percentage mode
        self.toggle_resize_mode()
        
        # Output folder selection
        output_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        output_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(
            output_frame,
            text="Output Folder:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w')
        
        output_control_frame = tk.Frame(output_frame, bg='#f0f0f0')
        output_control_frame.pack(fill='x', pady=5)
        
        self.output_entry = tk.Entry(
            output_control_frame,
            textvariable=self.output_folder,
            font=('Arial', 10),
            bg='white'
        )
        self.output_entry.pack(side='left', fill='x', expand=True)
        
        output_btn = tk.Button(
            output_control_frame,
            text="Browse",
            command=self.select_output_folder,
            bg='#6366f1',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=20
        )
        output_btn.pack(side='right', padx=(10, 0))
        
        # File selection frame
        file_frame = tk.LabelFrame(
            self.root,
            text="Image Files",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        file_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Buttons for file operations
        btn_frame = tk.Frame(file_frame, bg='#f0f0f0')
        btn_frame.pack(pady=10, padx=10, fill='x')
        
        select_btn = tk.Button(
            btn_frame,
            text="Select Images",
            command=self.select_files,
            bg='#2563eb',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=5
        )
        select_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = tk.Button(
            btn_frame,
            text="Clear All",
            command=self.clear_files,
            bg='#dc2626',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=5
        )
        clear_btn.pack(side='left', padx=(0, 10))
        
        convert_btn = tk.Button(
            btn_frame,
            text="Convert All",
            command=self.start_conversion,
            bg='#16a34a',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=5
        )
        convert_btn.pack(side='right')
        
        # File list
        list_frame = tk.Frame(file_frame, bg='#f0f0f0')
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Treeview for file list
        columns = ('Filename', 'Size', 'Status')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.file_tree.heading('Filename', text='Filename')
        self.file_tree.heading('Size', text='Original Size')
        self.file_tree.heading('Status', text='Status')
        
        self.file_tree.column('Filename', width=300)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Status', width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode='determinate',
            style='TProgressbar'
        )
        self.progress.pack(pady=10, padx=20, fill='x')
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready to convert images",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.status_label.pack(pady=(0, 10))
        
    def update_quality_label(self, *args):
        self.quality_label.config(text=f"{self.quality.get()}%")
        
    def update_size_label(self, *args):
        self.size_label.config(text=f"{self.size_reduction.get()}%")
        
    def toggle_resize_mode(self):
        """Toggle between percentage and preset resize modes"""
        if self.resize_mode.get() == "percentage":
            self.percentage_frame.pack(fill='x', pady=5)
            self.preset_frame.pack_forget()
        else:
            self.preset_frame.pack(fill='x', pady=5)
            self.percentage_frame.pack_forget()
        
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            
    def select_files(self):
        filetypes = [
            ("All Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("BMP files", "*.bmp"),
            ("GIF files", "*.gif"),
            ("TIFF files", "*.tiff"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=filetypes
        )
        
        if files:
            for file_path in files:
                if file_path not in [f['path'] for f in self.selected_files]:
                    file_info = {
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'size': os.path.getsize(file_path),
                        'status': 'Ready'
                    }
                    self.selected_files.append(file_info)
                    
            self.update_file_list()
            
    def clear_files(self):
        self.selected_files.clear()
        self.update_file_list()
        self.progress['value'] = 0
        self.status_label.config(text="Ready to convert images")
        
    def update_file_list(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Add files to list
        for file_info in self.selected_files:
            size_str = self.format_file_size(file_info['size'])
            self.file_tree.insert('', 'end', values=(
                file_info['name'],
                size_str,
                file_info['status']
            ))
            
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select images to convert.")
            return
            
        if not self.output_folder.get():
            messagebox.showwarning("No Output Folder", "Please select an output folder.")
            return
            
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_images)
        thread.daemon = True
        thread.start()
        
    def convert_images(self):
        total_files = len(self.selected_files)
        self.progress['maximum'] = total_files
        converted_count = 0
        failed_count = 0
        
        for i, file_info in enumerate(self.selected_files):
            try:
                # Update status
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Converting {file_info['name']}..."
                ))
                
                # Update file status in tree
                file_info['status'] = 'Converting...'
                self.root.after(0, self.update_file_list)
                
                # Convert image
                success = self.convert_image(file_info)
                
                if success:
                    file_info['status'] = 'Converted ✓'
                    converted_count += 1
                else:
                    file_info['status'] = 'Failed ✗'
                    failed_count += 1
                    
            except Exception as e:
                file_info['status'] = f'Error: {str(e)}'
                failed_count += 1
                
            # Update progress
            self.root.after(0, lambda: setattr(self.progress, 'value', i + 1))
            self.root.after(0, self.update_file_list)
            
        # Final status update
        self.root.after(0, lambda: self.status_label.config(
            text=f"Conversion complete! {converted_count} successful, {failed_count} failed"
        ))
        
        if converted_count > 0:
            self.root.after(0, lambda: messagebox.showinfo(
                "Conversion Complete",
                f"Successfully converted {converted_count} images!\nOutput folder: {self.output_folder.get()}"
            ))
            
    def convert_image(self, file_info):
        try:
            # Open image
            with Image.open(file_info['path']) as img:
                # Convert to RGB if necessary (for formats like PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Apply resizing based on selected mode
                if self.resize_mode.get() == "percentage" and self.size_reduction.get() > 0:
                    # Percentage-based reduction
                    reduction_factor = 1 - (self.size_reduction.get() / 100)
                    new_width = int(img.width * reduction_factor)
                    new_height = int(img.height * reduction_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                elif self.resize_mode.get() == "preset":
                    # Preset dimensions with aspect ratio preservation
                    target_size = self.preset_size.get()
                    target_width, target_height = map(int, target_size.split('x'))
                    
                    # Calculate the scaling factor to fit within target dimensions
                    width_ratio = target_width / img.width
                    height_ratio = target_height / img.height
                    scale_factor = min(width_ratio, height_ratio)
                    
                    # Only resize if the image is larger than target or if scale factor is significantly different
                    if scale_factor < 1.0 or scale_factor > 1.1:
                        new_width = int(img.width * scale_factor)
                        new_height = int(img.height * scale_factor)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create output filename
                input_name = Path(file_info['path']).stem
                output_path = os.path.join(self.output_folder.get(), f"{input_name}.webp")
                
                # Save as WebP
                img.save(
                    output_path,
                    'WEBP',
                    quality=self.quality.get(),
                    optimize=True
                )
                
                return True
                
        except Exception as e:
            print(f"Error converting {file_info['name']}: {str(e)}")
            return False

def main():
    root = tk.Tk()
    app = WebPConverter(root)
    
    # Set minimum window size
    root.minsize(600, 500)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()