import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  # pip install pyperclip

class LatexTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thesis Table Maker v3 (Visual Borders)")
        self.root.geometry("750x420")
        
        # --- テーマ設定 ---
        self.colors = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'accent': '#0078d7',
            'panel': '#ffffff',
            'input': '#ffffff',
            'header': '#e6f3ff',
            'button': '#e1e1e1',
            'button_action': '#0066cc',
            'text': '#000000',
            'border': '#a0a0a0',
            'active': '#e5f3ff',
            'highlight': '#fff2cc',
            'label': '#666666',
            'disabled': '#a0a0a0',
            'status': '#333333',
            'border_visual': '#4da6ff' # 視覚的な罫線の色（青に変更）
        }

        self.root.configure(bg=self.colors['bg'])
        self.setup_styles()

        # データ管理
        self.rows = 2
        self.cols = 2
        
        # 罫線管理
        self.col_right_borders = [True] * self.cols
        self.row_bottom_borders = [True] * self.rows
        
        # グリッドの状態管理辞書
        self.grid_data = {} 
        self.current_focus = None 

        # --- UIレイアウト ---
        
        main_container = ttk.Frame(root)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 1. ツールバー
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill='x', pady=(0, 5))

        # (A) 基本操作 (レイアウト変更: ラベル + ボタン)
        btn_frame = ttk.LabelFrame(toolbar, text="編集", padding=2)
        btn_frame.pack(side='left', padx=2, fill='y')
        
        # 行操作
        f_row = ttk.Frame(btn_frame)
        f_row.pack(side='left', padx=2)
        ttk.Label(f_row, text="行:").pack(side='left', padx=(0, 2))
        ttk.Button(f_row, text="+", width=4, command=self.add_row).pack(side='left', padx=0)
        ttk.Button(f_row, text="-", width=4, command=self.delete_row).pack(side='left', padx=0)
        
        # 列操作
        f_col = ttk.Frame(btn_frame)
        f_col.pack(side='left', padx=5) # 行操作との間隔
        ttk.Label(f_col, text="列:").pack(side='left', padx=(0, 2))
        ttk.Button(f_col, text="+", width=4, command=self.add_col).pack(side='left', padx=0)
        ttk.Button(f_col, text="-", width=4, command=self.delete_col).pack(side='left', padx=0)

        ttk.Button(btn_frame, text="クリア", width=5, command=self.reset_grid).pack(side='left', padx=5)

        # (B) 結合
        merge_frame = ttk.LabelFrame(toolbar, text="結合", padding=2)
        merge_frame.pack(side='left', padx=2, fill='y')
        ttk.Button(merge_frame, text="→", width=3, command=self.merge_right).pack(side='left', padx=1)
        ttk.Button(merge_frame, text="↓", width=3, command=self.merge_down).pack(side='left', padx=1)
        ttk.Button(merge_frame, text="×", width=3, command=self.unmerge_cell).pack(side='left', padx=1)

        # (C) 罫線操作
        border_frame = ttk.LabelFrame(toolbar, text="罫線", padding=2)
        border_frame.pack(side='left', padx=2, fill='y')
        self.btn_toggle_v = ttk.Button(border_frame, text="┃", width=3, command=self.toggle_col_border)
        self.btn_toggle_v.pack(side='left', padx=1)
        self.btn_toggle_h = ttk.Button(border_frame, text="━", width=3, command=self.toggle_row_border)
        self.btn_toggle_h.pack(side='left', padx=1)

        # 2. 設定エリア
        settings_frame = ttk.Frame(main_container)
        settings_frame.pack(fill='x', pady=(0, 5), padx=2)

        left_settings = ttk.Frame(settings_frame)
        left_settings.pack(side='left', fill='x')

        ttk.Label(left_settings, text="Caption:").pack(side='left')
        self.entry_caption = ttk.Entry(left_settings, width=12)
        self.entry_caption.pack(side='left', padx=(2, 5))
        
        ttk.Label(left_settings, text="Label: tab:").pack(side='left')
        self.entry_label = ttk.Entry(left_settings, width=6)
        self.entry_label.pack(side='left', padx=(0, 5))

        self.use_booktabs = tk.BooleanVar(value=True)
        self.first_col_line = tk.BooleanVar(value=False) # 1列目右線
        self.show_outer_border = tk.BooleanVar(value=True)

        # テキストを「Booktabs」から「論文」に変更
        self.cb_booktabs = ttk.Checkbutton(left_settings, text="論文", variable=self.use_booktabs, command=self.update_ui_state)
        self.cb_booktabs.pack(side='left', padx=2)
        
        # 1列目右線チェックボックス (復活)
        self.cb_first_col = ttk.Checkbutton(left_settings, text="1列目右線", variable=self.first_col_line, command=self.refresh_all_borders)
        self.cb_first_col.pack(side='left', padx=2)

        self.cb_outer = ttk.Checkbutton(left_settings, text="外枠", variable=self.show_outer_border, command=self.refresh_all_borders)
        self.cb_outer.pack(side='left', padx=2)
        
        # 保存ボタン
        self.btn_generate = ttk.Button(settings_frame, text="Copy LaTeX", command=self.generate_latex, style='Action.TButton')
        self.btn_generate.pack(side='right', padx=5)

        # 3. グリッドエリア
        self.canvas = tk.Canvas(main_container, bg=self.colors['panel'], highlightthickness=1, highlightbackground=self.colors['border'])
        self.scrollbar_y = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(main_container, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Panel.TFrame")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.canvas.pack(side="top", fill="both", expand=True, padx=0, pady=5)
        self.scrollbar_y.pack(side="right", fill="y", in_=self.canvas) 
        self.scrollbar_x.pack(side="bottom", fill="x", in_=main_container)

        # 4. 下部ステータス
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(side='bottom', fill='x', pady=0, padx=2)

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, foreground=self.colors['status'], font=("", 8))
        status_label.pack(side='left', anchor='w')

        self.create_grid()
        self.root.after(100, self.update_ui_state)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default') 
        style.configure('.', background=self.colors['bg'], foreground=self.colors['text'], font=('Segoe UI', 9))
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('Panel.TFrame', background=self.colors['panel'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TLabelframe', background=self.colors['bg'], bordercolor=self.colors['border'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['accent'], font=('Segoe UI', 9, 'bold'))
        style.configure('TButton', background=self.colors['button'], borderwidth=1, relief='raised')
        style.map('TButton', background=[('active', self.colors['active']), ('pressed', self.colors['accent'])])
        style.configure('Action.TButton', background=self.colors['button_action'], foreground='#ffffff', font=('Segoe UI', 9, 'bold'))
        style.map('Action.TButton', background=[('active', '#3385ff'), ('pressed', '#0052a3')])
        style.configure('TCheckbutton', background=self.colors['bg'])

    def update_ui_state(self):
        is_booktabs = self.use_booktabs.get()
        state = 'disabled' if is_booktabs else '!disabled'
        self.btn_toggle_v.state([state])
        self.btn_toggle_h.state([state])
        self.cb_outer.state([state])
        
        # 論文モードのときは「1列目右線」を有効化
        if is_booktabs:
            self.cb_first_col.state(['!disabled'])
        else:
            self.cb_first_col.state(['disabled'])

        # Booktabsモード切替時に罫線表示を更新
        self.refresh_all_borders()

    def update_status(self):
        if not self.current_focus:
            self.status_var.set("Select a cell")
            return
        
        r, c = self.current_focus
        if c < len(self.col_right_borders) and r < len(self.row_bottom_borders):
            v_stat = "ON" if self.col_right_borders[c] else "OFF"
            h_stat = "ON" if self.row_bottom_borders[r] else "OFF"
            self.status_var.set(f"Row:{r+1} Col:{c+1} | V-Line:{v_stat} H-Line:{h_stat}")
        else:
            self.status_var.set("")

    def toggle_col_border(self):
        if not self.current_focus: return
        r, c = self.current_focus
        cell = self.grid_data.get((r, c))
        if not cell: return
        target_col = c + cell['colspan'] - 1
        
        if target_col < len(self.col_right_borders):
            self.col_right_borders[target_col] = not self.col_right_borders[target_col]
            self.refresh_all_borders()
            self.update_status()

    def toggle_row_border(self):
        if not self.current_focus: return
        r, c = self.current_focus
        cell = self.grid_data.get((r, c))
        if not cell: return
        target_row = r + cell['rowspan'] - 1

        if target_row < len(self.row_bottom_borders):
            self.row_bottom_borders[target_row] = not self.row_bottom_borders[target_row]
            self.refresh_all_borders()
            self.update_status()

    def refresh_all_borders(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.grid_data:
                    self.update_cell_visual(r, c)

    def update_cell_visual(self, r, c):
        cell = self.grid_data.get((r, c))
        if not cell or cell['hidden']: return
        
        entry = cell['widget']
        
        # Booktabsモードの処理
        if self.use_booktabs.get():
            # 1列目右線が有効で、かつ現在0列目（または0列目で終わる結合セル）の場合
            end_col = c + cell['colspan'] - 1
            if self.first_col_line.get() and end_col == 0:
                entry.pack_configure(padx=(0, 3), pady=0)
            else:
                entry.pack_configure(padx=0, pady=0)
            return

        # --- 標準モードでの青線表示ロジック ---
        
        outer = self.show_outer_border.get()
        
        # 右線: 結合セルの場合は最終列の設定を見る
        end_col = c + cell['colspan'] - 1
        has_right = self.col_right_borders[end_col] if end_col < len(self.col_right_borders) else False
        
        # 下線: 結合セルの場合は最終行の設定を見る
        end_row = r + cell['rowspan'] - 1
        has_bottom = self.row_bottom_borders[end_row] if end_row < len(self.row_bottom_borders) else False

        # パディング計算 (青線表示用)
        # 外枠(Outer)がONなら、左端の左と、上端の上も青くする
        # また、右端の右と下端の下も外枠として扱う
        
        pad_left = 3 if (outer and c == 0) else 0
        pad_top = 3 if (outer and r == 0) else 0
        
        # 右パディング: 個別の右線がON または (外枠ON かつ 最後の列)
        is_last_col = (end_col == self.cols - 1)
        pad_right = 3 if (has_right or (outer and is_last_col)) else 0
        
        # 下パディング: 個別の下線がON または (外枠ON かつ 最後の行)
        is_last_row = (end_row == self.rows - 1)
        pad_bottom = 3 if (has_bottom or (outer and is_last_row)) else 0
        
        entry.pack_configure(padx=(pad_left, pad_right), pady=(pad_top, pad_bottom))

    def create_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.grid_data = {}
        
        self.col_right_borders = [True] * self.cols
        self.row_bottom_borders = [True] * self.rows

        for r in range(self.rows):
            for c in range(self.cols):
                self._create_entry(r, c)
        
        self.refresh_all_borders()

    def _create_entry(self, r, c):
        container = tk.Frame(self.scrollable_frame, bg=self.colors['border_visual'], bd=0)
        container.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

        bg_color = self.colors['header'] if r == 0 else self.colors['input']
        entry = tk.Entry(container, width=15, 
                         bg=bg_color, fg=self.colors['text'], 
                         relief="sunken", borderwidth=1,
                         font=("Consolas", 10))
        entry.pack(fill='both', expand=True)
        
        entry.bind("<FocusIn>", lambda e, r=r, c=c: self._on_focus(r, c, entry))
        
        self.grid_data[(r, c)] = {
            'widget': entry, 'container': container, 
            'colspan': 1, 'rowspan': 1, 'hidden': False, 'owner': (r, c)
        }
        return entry

    def _on_focus(self, r, c, widget):
        self.current_focus = (r, c)
        self.update_status()

    # --- 行・列の追加削除 ---

    def add_row(self):
        self.rows += 1
        self.row_bottom_borders.append(True) # デフォルトで線あり
        for c in range(self.cols):
            self._create_entry(self.rows-1, c)
        self._update_scroll()
        self.refresh_all_borders()

    def add_col(self):
        self.cols += 1
        self.col_right_borders.append(True) # デフォルトで線あり
        for r in range(self.rows):
            self._create_entry(r, self.cols-1)
        self._update_scroll()
        self.refresh_all_borders()

    def delete_row(self):
        if self.rows <= 1: return
        
        # 削除対象行（選択がなければ末尾）
        target_r = self.current_focus[0] if self.current_focus else self.rows - 1
        
        # データ退避（テキスト、結合状態、罫線状態を保持して再構築する簡易実装）
        # ※結合が含まれると複雑になるため、今回は「全データをテキストとして退避し、結合は解除される」仕様とする
        
        new_data = []
        for r in range(self.rows):
            if r == target_r: continue # 削除対象行はスキップ
            
            row_vals = []
            for c in range(self.cols):
                cell = self.grid_data.get((r, c))
                val = ""
                if cell and not cell['hidden']:
                    val = cell['widget'].get()
                row_vals.append(val)
            new_data.append(row_vals)
        
        # 罫線情報の更新
        self.row_bottom_borders.pop(target_r)
        
        # 再構築
        self.rows -= 1
        self.create_grid() 
        
        # テキスト復元
        for r in range(self.rows):
            for c in range(self.cols):
                if c < len(new_data[r]):
                    val = new_data[r][c]
                    if val:
                        self.grid_data[(r, c)]['widget'].insert(0, val)

        self.refresh_all_borders()
        self.current_focus = None
        self.update_status()

    def delete_col(self):
        if self.cols <= 1: return
        
        target_c = self.current_focus[1] if self.current_focus else self.cols - 1
        
        new_data = []
        for r in range(self.rows):
            row_vals = []
            for c in range(self.cols):
                if c == target_c: continue
                
                cell = self.grid_data.get((r, c))
                val = ""
                if cell and not cell['hidden']:
                    val = cell['widget'].get()
                row_vals.append(val)
            new_data.append(row_vals)
            
        self.col_right_borders.pop(target_c)
        
        self.cols -= 1
        self.create_grid()
        
        for r in range(self.rows):
            for c in range(self.cols):
                if c < len(new_data[r]):
                    val = new_data[r][c]
                    if val:
                        self.grid_data[(r, c)]['widget'].insert(0, val)

        self.refresh_all_borders()
        self.current_focus = None
        self.update_status()

    def reset_grid(self):
        self.rows = 2
        self.cols = 2
        self.current_focus = None
        self.create_grid()
        self.update_status()

    def _update_scroll(self):
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def merge_right(self):
        if not self.current_focus: return
        r, c = self.current_focus
        cell = self.grid_data.get((r, c))
        if not cell or cell['hidden']: return
        target_c = c + cell['colspan']
        target_cell = self.grid_data.get((r, target_c))

        if target_cell and not target_cell['hidden'] and target_cell['rowspan'] == cell['rowspan']:
            target_cell['container'].grid_remove()
            cell['container'].grid(columnspan=cell['colspan'] + 1)
            cell['widget'].configure(width=15 * (cell['colspan'] + 1))
            
            cell['colspan'] += 1
            target_cell['hidden'] = True
            target_cell['owner'] = (r, c)
            
            self.refresh_all_borders()
        else:
            messagebox.showinfo("Merge", "結合不可")

    def merge_down(self):
        if not self.current_focus: return
        r, c = self.current_focus
        cell = self.grid_data.get((r, c))
        if not cell or cell['hidden']: return
        target_r = r + cell['rowspan']
        target_cell = self.grid_data.get((target_r, c))

        if target_cell and not target_cell['hidden'] and target_cell['colspan'] == cell['colspan']:
            target_cell['container'].grid_remove()
            cell['container'].grid(rowspan=cell['rowspan'] + 1)
            
            cell['rowspan'] += 1
            target_cell['hidden'] = True
            target_cell['owner'] = (r, c)
            
            self.refresh_all_borders()
        else:
            messagebox.showinfo("Merge", "結合不可")

    def unmerge_cell(self):
        if not self.current_focus: return
        r, c = self.current_focus
        cell = self.grid_data.get((r, c))
        if not cell or cell['hidden']: return
        if cell['colspan'] == 1 and cell['rowspan'] == 1: return

        for tr in range(r, r + cell['rowspan']):
            for tc in range(c, c + cell['colspan']):
                if tr == r and tc == c: continue 
                target = self.grid_data.get((tr, tc))
                if target:
                    target['hidden'] = False
                    target['owner'] = (tr, tc)
                    target['container'].grid()

        cell['colspan'] = 1
        cell['rowspan'] = 1
        cell['container'].grid(rowspan=1, columnspan=1)
        cell['widget'].configure(width=15)
        
        self.refresh_all_borders()

    def generate_latex(self):
        caption = self.entry_caption.get()
        lbl_in = self.entry_label.get().strip()
        label = f"tab:{lbl_in}" if lbl_in else ""
        
        is_bt = self.use_booktabs.get()
        outer = self.show_outer_border.get()
        first_col_line = self.first_col_line.get()

        lines = [f"\\begin{{table}}[H]", "  \\centering"]
        if caption: lines.append(f"  \\caption{{{caption}}}")
        if label: lines.append(f"  \\label{{{label}}}")

        col_fmt_parts = []
        if is_bt:
            col_fmt_parts = ["c"] * self.cols
            if first_col_line and self.cols > 1:
                col_fmt_parts[0] = "c|"
        else:
            if outer: col_fmt_parts.append("|")
            for i in range(self.cols):
                col_fmt_parts.append("c")
                if self.col_right_borders[i]:
                    col_fmt_parts.append("|")
            
        col_fmt_str = "".join(col_fmt_parts)
        lines.append(f"  \\begin{{tabular}}{{{col_fmt_str}}}")

        if is_bt:
            if first_col_line:
                lines.append("    \\hline")
            else:
                lines.append("    \\toprule")
        elif outer:
            lines.append("    \\hline")

        for r in range(self.rows):
            row_cells = []
            c = 0
            while c < self.cols:
                cell = self.grid_data.get((r, c))
                if cell['hidden']:
                    owner_r, owner_c = cell['owner']
                    owner = self.grid_data.get((owner_r, owner_c))
                    if owner['colspan'] > 1 and (c > owner_c): 
                        pass 
                    else: 
                        row_cells.append("") 
                    c += 1
                    continue

                text = cell['widget'].get().strip()
                
                if text:
                    has_alpha = any(char.isalpha() for char in text)
                    if has_alpha and not text.startswith("\\"): text = f"\\mathrm{{{text}}}"
                    if not (text.startswith("$") and text.endswith("$")): text = f"${text}$"

                if cell['colspan'] > 1:
                    align_char = "c"
                    l_bar = ""
                    r_bar = ""

                    if is_bt:
                        if first_col_line and c == 0:
                            align_char = "c|"
                    else:
                        if c == 0:
                            if outer: l_bar = "|"
                        else:
                            if self.col_right_borders[c-1]: l_bar = "|"
                        
                        end_col = c + cell['colspan'] - 1
                        if end_col < self.cols and self.col_right_borders[end_col]:
                            r_bar = "|"
                    
                    align = f"{l_bar}{align_char}{r_bar}"
                    text = f"\\multicolumn{{{cell['colspan']}}}{{{align}}}{{{text}}}"
                
                if cell['rowspan'] > 1:
                     text = f"\\multirow{{{cell['rowspan']}}}{{*}}{{{text}}}"

                row_cells.append(text)
                c += cell['colspan']

            lines.append("    " + " & ".join(row_cells) + " \\\\")

            if is_bt:
                if r == 0:
                    if first_col_line:
                        lines.append("    \\hline")
                    else:
                        lines.append("    \\midrule")
            else:
                if self.row_bottom_borders[r]:
                    cline_segments = []
                    start_idx = None
                    
                    for c in range(self.cols):
                        should_draw = True
                        target_cell = self.grid_data.get((r, c))
                        if target_cell['hidden']:
                            owner_r, owner_c = target_cell['owner']
                            owner = self.grid_data.get((owner_r, owner_c))
                            if r < (owner_r + owner['rowspan'] - 1):
                                should_draw = False
                        else:
                            if target_cell['rowspan'] > 1:
                                if r < (r + target_cell['rowspan'] - 1):
                                    should_draw = False
                        
                        if should_draw:
                            if start_idx is None:
                                start_idx = c + 1
                        else:
                            if start_idx is not None:
                                end_idx = c
                                cline_segments.append(f"\\cline{{{start_idx}-{end_idx}}}")
                                start_idx = None
                    
                    if start_idx is not None:
                         cline_segments.append(f"\\cline{{{start_idx}-{self.cols}}}")
                    
                    if not cline_segments:
                        pass
                    elif len(cline_segments) == 1 and cline_segments[0] == f"\\cline{{1-{self.cols}}}":
                        lines.append("    \\hline")
                    else:
                        lines.append("    " + " ".join(cline_segments))

        if is_bt:
            if first_col_line:
                lines.append("    \\hline")
            else:
                lines.append("    \\bottomrule")

        lines.append("  \\end{tabular}")
        lines.append("\\end{table}")

        pyperclip.copy("\n".join(lines))
        messagebox.showinfo("完了", "クリップボードにコピーしました")

if __name__ == "__main__":
    root = tk.Tk()
    app = LatexTableApp(root)
    root.mainloop()