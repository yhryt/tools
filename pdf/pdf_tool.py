import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from pypdf import PdfWriter, PdfReader
from PIL import Image
import os
import threading

class PDFTool(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Tool (Fast & Lightweight)")
        self.geometry("500x700")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.merge_tab = MergeTab(self.notebook)
        self.split_tab = SplitTab(self.notebook)
        self.img2pdf_tab = Img2PdfTab(self.notebook)
        
        self.notebook.add(self.merge_tab, text="Merge PDFs")
        self.notebook.add(self.split_tab, text="Split PDF")
        self.notebook.add(self.img2pdf_tab, text="Images to PDF")

class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.files = []
        self.setup_ui()

    def setup_ui(self):
        pass

    def add_drop_zone(self, callback):
        self.drop_frame = tk.Frame(self, bg="#f0f0f0", bd=2, relief="groove")
        self.drop_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.drop_label = tk.Label(self.drop_frame, text="Drop files here", bg="#f0f0f0", fg="#888")
        self.drop_label.pack(pady=20)
        
        # Enable Drag & Drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', callback)
        
        self.btn_select = ttk.Button(self, text="Select Files", command=self.select_files)
        self.btn_select.pack(pady=5)

    def select_files(self):
        pass

    def update_file_list(self):
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
            
        for i, file_path in enumerate(self.files):
            frame = ttk.Frame(self.file_list_frame)
            frame.pack(fill=tk.X, pady=2)
            
            lbl = ttk.Label(frame, text=os.path.basename(file_path))
            lbl.pack(side=tk.LEFT, padx=5)
            
            btn_del = ttk.Button(frame, text="X", width=3, command=lambda idx=i: self.remove_file(idx))
            btn_del.pack(side=tk.RIGHT)
            
            if i < len(self.files) - 1:
                btn_down = ttk.Button(frame, text="↓", width=3, command=lambda idx=i: self.move_file(idx, 1))
                btn_down.pack(side=tk.RIGHT)
                
            if i > 0:
                btn_up = ttk.Button(frame, text="↑", width=3, command=lambda idx=i: self.move_file(idx, -1))
                btn_up.pack(side=tk.RIGHT)

    def remove_file(self, index):
        self.files.pop(index)
        self.update_file_list()

    def move_file(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.files):
            self.files[index], self.files[new_index] = self.files[new_index], self.files[index]
            self.update_file_list()

    def set_loading(self, loading):
        if loading:
            self.action_btn.config(state=tk.DISABLED, text="Processing...")
        else:
            self.action_btn.config(state=tk.NORMAL, text=self.action_text)

class MergeTab(BaseTab):
    def setup_ui(self):
        self.add_drop_zone(self.on_drop)
        
        self.file_list_frame = ttk.LabelFrame(self, text="Selected Files")
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Output filename
        self.out_frame = ttk.Frame(self)
        self.out_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(self.out_frame, text="Output Filename (Opt):").pack(side=tk.LEFT)
        self.ent_filename = ttk.Entry(self.out_frame)
        self.ent_filename.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.action_text = "Merge Files"
        self.action_btn = ttk.Button(self, text=self.action_text, command=self.run_merge)
        self.action_btn.pack(pady=10)

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            if f.lower().endswith('.pdf'):
                self.files.append(f)
        self.update_file_list()

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.files.extend(files)
            self.update_file_list()

    def run_merge(self):
        if len(self.files) < 2:
            messagebox.showwarning("Warning", "Select at least 2 PDF files.")
            return

        out_name = self.ent_filename.get().strip() or "merged.pdf"
        if not out_name.lower().endswith('.pdf'):
            out_name += ".pdf"
            
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=out_name)
        if not save_path:
            return

        self.set_loading(True)
        threading.Thread(target=self.merge_logic, args=(save_path,), daemon=True).start()

    def merge_logic(self, save_path):
        try:
            merger = PdfWriter()
            for pdf in self.files:
                merger.append(pdf)
            merger.write(save_path)
            merger.close()
            messagebox.showinfo("Success", f"Saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.set_loading(False)

class SplitTab(BaseTab):
    def setup_ui(self):
        self.add_drop_zone(self.on_drop)
        
        self.file_label = ttk.Label(self, text="No file selected")
        self.file_label.pack(pady=5)
        
        # Pages Listbox
        self.list_frame = ttk.LabelFrame(self, text="Select Pages to Extract")
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.page_list = tk.Listbox(self.list_frame, selectmode=tk.MULTIPLE, yscrollcommand=self.scrollbar.set)
        self.page_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.page_list.yview)
        
        self.page_list.bind('<<ListboxSelect>>', self.update_range_from_selection)
        
        self.file_list_frame = tk.Frame(self) # Dummy to match BaseTab structure

        ttk.Label(self, text="Selected Ranges:").pack(pady=5)
        self.ent_range = ttk.Entry(self)
        self.ent_range.pack(fill=tk.X, padx=10)
        
        # Output filename
        self.out_frame = ttk.Frame(self)
        self.out_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(self.out_frame, text="Output Filename (Opt):").pack(side=tk.LEFT)
        self.ent_filename = ttk.Entry(self.out_frame)
        self.ent_filename.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.action_text = "Split PDF"
        self.action_btn = ttk.Button(self, text=self.action_text, command=self.run_split)
        self.action_btn.pack(pady=10)

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files and files[0].lower().endswith('.pdf'):
            self.files = [files[0]]
            self.file_label.config(text=os.path.basename(files[0]))
            self.load_pdf_pages()

    def select_files(self):
        f = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.files = [f]
            self.file_label.config(text=os.path.basename(f))
            self.load_pdf_pages()

    def load_pdf_pages(self):
        self.page_list.delete(0, tk.END)
        try:
            reader = PdfReader(self.files[0])
            num_pages = len(reader.pages)
            for i in range(1, num_pages + 1):
                self.page_list.insert(tk.END, f"Page {i}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read PDF: {e}")

    def update_range_from_selection(self, event):
        selection = self.page_list.curselection()
        if not selection:
            self.ent_range.delete(0, tk.END)
            return
            
        # Convert to 1-based indices
        pages = [i + 1 for i in selection]
        pages.sort()
        
        # Simple range compression logic (e.g. 1,2,3 -> 1-3)
        ranges = []
        if pages:
            start = pages[0]
            prev = pages[0]
            for page in pages[1:]:
                if page == prev + 1:
                    prev = page
                else:
                    if start == prev:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start}-{prev}")
                    start = page
                    prev = page
            # Add last one
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
        
        range_str = ", ".join(ranges)
        self.ent_range.delete(0, tk.END)
        self.ent_range.insert(0, range_str)

    def run_split(self):
        if not self.files:
            messagebox.showwarning("Warning", "Select a PDF file.")
            return
        
        ranges = self.ent_range.get().strip()
        if not ranges:
            messagebox.showwarning("Warning", "Select pages from list or enter range.")
            return

        out_name = self.ent_filename.get().strip() or f"split-{os.path.basename(self.files[0])}"
        if not out_name.lower().endswith('.pdf'):
            out_name += ".pdf"

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=out_name)
        if not save_path:
            return

        self.set_loading(True)
        threading.Thread(target=self.split_logic, args=(save_path, ranges), daemon=True).start()

    def split_logic(self, save_path, range_str):
        try:
            reader = PdfReader(self.files[0])
            writer = PdfWriter()
            total_pages = len(reader.pages)
            
            pages_to_keep = set()
            parts = range_str.split(',')
            for part in parts:
                part = part.strip()
                if not part: continue
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    for i in range(start, end + 1):
                        if 1 <= i <= total_pages:
                            pages_to_keep.add(i - 1)
                else:
                    page = int(part)
                    if 1 <= page <= total_pages:
                        pages_to_keep.add(page - 1)
            
            indices = sorted(list(pages_to_keep))
            if not indices:
                 raise ValueError("No valid pages selected")

            for i in indices:
                writer.add_page(reader.pages[i])
            
            writer.write(save_path)
            writer.close()
            messagebox.showinfo("Success", f"Saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.set_loading(False)

class Img2PdfTab(BaseTab):
    def setup_ui(self):
        self.add_drop_zone(self.on_drop)
        
        self.file_list_frame = ttk.LabelFrame(self, text="Selected Images")
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Output filename
        self.out_frame = ttk.Frame(self)
        self.out_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(self.out_frame, text="Output Filename (Opt):").pack(side=tk.LEFT)
        self.ent_filename = ttk.Entry(self.out_frame)
        self.ent_filename.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.action_text = "Convert to PDF"
        self.action_btn = ttk.Button(self, text=self.action_text, command=self.run_convert)
        self.action_btn.pack(pady=10)

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            ext = f.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png']:
                self.files.append(f)
        self.update_file_list()

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg;*.jpeg;*.png")])
        if files:
            self.files.extend(files)
            self.update_file_list()

    def run_convert(self):
        if not self.files:
            messagebox.showwarning("Warning", "Select images.")
            return

        out_name = self.ent_filename.get().strip() or "images.pdf"
        if not out_name.lower().endswith('.pdf'):
            out_name += ".pdf"
            
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=out_name)
        if not save_path:
            return

        self.set_loading(True)
        threading.Thread(target=self.convert_logic, args=(save_path,), daemon=True).start()

    def convert_logic(self, save_path):
        try:
            images = []
            for f in self.files:
                img = Image.open(f)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                images.append(img)
            
            if images:
                images[0].save(save_path, save_all=True, append_images=images[1:])
                messagebox.showinfo("Success", f"Saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.set_loading(False)

if __name__ == "__main__":
    app = PDFTool()
    app.mainloop()
