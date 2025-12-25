import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import os
import sys
import math
import json
import platform
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# --- 重要: 必要なライブラリ ---
# pip install openpyxl numpy

# 設定ファイルのパス
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "settings.json")

def get_system_font():
    """OSに合わせてデフォルトフォントを決定する"""
    system_name = platform.system()
    if system_name == "Windows":
        return "MS Gothic"
    elif system_name == "Darwin": # Mac
        return "Hiragino Sans"
    else: # Linux etc
        return "Noto Sans CJK JP"

def load_settings():
    """設定を読み込む"""
    default_font = get_system_font()
    default_settings = {
        "x_label": "", "x_unit": "",
        "y_label": "", "y_unit": "",
        "font_family": default_font,
        "font_size": 10,
        "marker_size": 20,
        "grid": True, # デフォルトでグリッドON
        "dpi": 100,
        "dpi": 100,
        "show_r2": True,
        "x_log": False,
        "y_log": False
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                default_settings.update(user_settings)
        except:
            pass
    return default_settings

def save_settings(settings):
    """設定を保存する"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"設定保存エラー: {e}")

def float_to_latex_sci(val):
    """数値をLaTeX形式の科学的表記に変換"""
    if val == 0: return "0"
    sci_str = "{:.2e}".format(val)
    try:
        mantissa, exponent = sci_str.split('e')
        exp_int = int(exponent)
        if exp_int == 0: return mantissa
        return r"{} \times 10^{{{}}}".format(mantissa, exp_int)
    except:
        return str(val)

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Maker Pro")
        self.root.geometry("1280x850")
        
        self.settings = load_settings()
        self.df_raw = None
        self.filepath = ""
        self.trendline_sets = [] 
        
        # 配色設定：標準的なライトテーマ（白・グレー基調）
        self.colors = {
            'bg': '#f0f0f0',          # 標準的なウィンドウ背景色（薄いグレー）
            'fg': '#000000',          # 黒
            'accent': '#0078d7',      # 標準的な青
            'panel': '#ffffff',       # 白（リストボックスやグラフ背景）
            'input': '#ffffff',       # 入力欄
            'button': '#e1e1e1',      # ボタン背景
            'button_action': '#0066cc', # アクションボタン
            'text': '#000000',        # テキスト
            'border': '#a0a0a0',      # 境界線
            'active': '#e5f3ff',      # ホバー
            'highlight': '#fff2cc'    # 強調色（薄い黄色）
        }
        
        self.apply_theme()
        
        # Matplotlibスタイル（標準）
        self.setup_matplotlib_style()
        
        self.setup_ui()

        # 起動引数チェック
        if len(sys.argv) > 1:
            potential_file = sys.argv[1]
            if os.path.exists(potential_file):
                self.filepath = potential_file
                self.lbl_filename.config(text=os.path.basename(self.filepath))
                self.root.after(100, self.load_initial_data)

    def setup_matplotlib_style(self):
        """Matplotlibのスタイル設定（標準ライトモード）"""
        plt.style.use('default')
        
        # UIに合わせた背景色
        plt.rcParams['figure.facecolor'] = 'white'
        # グラフエリアは白が見やすい
        plt.rcParams['axes.facecolor'] = 'white'
        
        # フォント設定
        font_family = self.settings.get("font_family", get_system_font())
        plt.rcParams['font.family'] = font_family
        plt.rcParams['font.size'] = self.settings.get("font_size", 10)
        
        # グリッド設定（初期値）
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 1.0 # はっきり見えるように不透明に
        plt.rcParams['grid.linestyle'] = '-'
        plt.rcParams['grid.color'] = '#bfbfbf' # 少し濃い目のグレー
        
        # 数式フォント
        plt.rcParams['mathtext.fontset'] = 'cm'
        plt.rcParams['mathtext.default'] = 'it'

    def apply_theme(self):
        """Tkinterテーマ設定"""
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure('.',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['input'],
            troughcolor=self.colors['bg'],
            selectbackground=self.colors['accent'],
            selectforeground='#ffffff',
            font=('Segoe UI', 9)
        )
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        
        # LabelFrame
        style.configure('TLabelframe', 
            background=self.colors['bg'], 
            foreground=self.colors['text'],
            bordercolor=self.colors['border'],
            borderwidth=1
        )
        style.configure('TLabelframe.Label', 
            background=self.colors['bg'], 
            foreground=self.colors['accent'],
            font=('Segoe UI', 9, 'bold')
        )
        
        # 通常ボタン
        style.configure('TButton', 
            background=self.colors['button'], 
            foreground=self.colors['text'], 
            borderwidth=1,
            relief='raised',
            padding=5
        )
        style.map('TButton', 
            background=[('active', self.colors['active']), ('pressed', self.colors['accent'])],
            foreground=[('pressed', '#ffffff')]
        )
        
        # アクションボタン
        style.configure('Action.TButton', 
            background=self.colors['button_action'], 
            foreground='#ffffff', 
            font=('Segoe UI', 9, 'bold')
        )
        style.map('Action.TButton', 
            background=[('active', '#3385ff'), ('pressed', '#0052a3')]
        )
        
        style.configure('TEntry', 
            fieldbackground=self.colors['input'], 
            foreground=self.colors['text'],
            borderwidth=1,
            relief='sunken'
        )
        
        style.configure('TCheckbutton',
            background=self.colors['bg'],
            foreground=self.colors['text']
        )
        
        style.configure('TCombobox', 
            fieldbackground=self.colors['input'], 
            foreground=self.colors['text'],
            arrowcolor=self.colors['text'],
            borderwidth=1
        )
        
        style.configure("Vertical.TScrollbar", 
            background=self.colors['button'], 
            troughcolor=self.colors['bg'], 
            arrowcolor=self.colors['text']
        )

    def setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_container, width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # === 左パネル ===
        
        # 1. データソース
        src_frame = ttk.LabelFrame(left_panel, text="📁 データソース", padding=10)
        src_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_load = ttk.Button(src_frame, text="ファイルを開く...", command=self.select_file)
        self.btn_load.pack(fill=tk.X, pady=5)
        
        self.lbl_filename = ttk.Label(src_frame, text="ファイル未選択", font=("", 9, "italic"), wraplength=280)
        self.lbl_filename.pack(fill=tk.X)
        
        ttk.Label(src_frame, text="シート選択:").pack(anchor=tk.W, pady=(8,2))
        self.combo_sheet = ttk.Combobox(src_frame, state="readonly")
        self.combo_sheet.pack(fill=tk.X)
        self.combo_sheet.bind("<<ComboboxSelected>>", self.on_sheet_selected)

        # 2. 列設定
        col_conf_frame = ttk.LabelFrame(left_panel, text="📊 列設定", padding=10)
        col_conf_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(col_conf_frame, text="X軸 (横軸):").pack(anchor=tk.W)
        self.combo_x_col = ttk.Combobox(col_conf_frame, state="readonly")
        self.combo_x_col.pack(fill=tk.X, pady=(0, 10))
        self.combo_x_col.bind("<<ComboboxSelected>>", lambda e: self.update_y_list())

        ttk.Label(col_conf_frame, text="Y軸 (縦軸):").pack(anchor=tk.W)
        list_frame = ttk.Frame(col_conf_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.list_cols = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                                    bg=self.colors['input'], fg=self.colors['fg'],
                                    selectbackground=self.colors['accent'], 
                                    selectforeground='#ffffff',
                                    borderwidth=1, relief="sunken",
                                    exportselection=False) 
        self.list_cols.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        col_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.list_cols.yview)
        col_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_cols.config(yscrollcommand=col_scroll.set)
        self.list_cols.bind('<<ListboxSelect>>', lambda e: self.draw_graph())

        # 3. 軸ラベル
        lbl_frame = ttk.LabelFrame(left_panel, text="📝 軸ラベル", padding=10)
        lbl_frame.pack(fill=tk.X, pady=(0, 10))
        
        grid_l = ttk.Frame(lbl_frame)
        grid_l.pack(fill=tk.X)
        
        ttk.Label(grid_l, text="X:").grid(row=0, column=0, sticky="w")
        self.entry_xlabel = ttk.Entry(grid_l)
        self.entry_xlabel.grid(row=0, column=1, sticky="ew", padx=5)
        self.entry_xlabel.insert(0, self.settings.get("x_label", ""))
        self.entry_xlabel.bind('<Return>', lambda e: self.draw_graph())
        self.entry_xlabel.bind('<FocusOut>', lambda e: self.draw_graph())
        
        ttk.Label(grid_l, text="単位:").grid(row=0, column=2, sticky="w")
        self.entry_xunit = ttk.Entry(grid_l, width=6)
        self.entry_xunit.grid(row=0, column=3, sticky="e")
        self.entry_xunit.insert(0, self.settings.get("x_unit", ""))
        self.entry_xunit.bind('<Return>', lambda e: self.draw_graph())
        self.entry_xunit.bind('<FocusOut>', lambda e: self.draw_graph())

        self.var_x_log = tk.BooleanVar(value=self.settings.get("x_log", False))
        self.chk_x_log = ttk.Checkbutton(grid_l, text="Log", variable=self.var_x_log, command=self.draw_graph)
        self.chk_x_log.grid(row=0, column=4, sticky="w", padx=5)

        ttk.Label(grid_l, text="Y:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_ylabel = ttk.Entry(grid_l)
        self.entry_ylabel.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.entry_ylabel.insert(0, self.settings.get("y_label", ""))
        self.entry_ylabel.bind('<Return>', lambda e: self.draw_graph())
        self.entry_ylabel.bind('<FocusOut>', lambda e: self.draw_graph())
        
        ttk.Label(grid_l, text="単位:").grid(row=1, column=2, sticky="w", pady=5)
        self.entry_yunit = ttk.Entry(grid_l, width=6)
        self.entry_yunit.grid(row=1, column=3, sticky="e", pady=5)
        self.entry_yunit.insert(0, self.settings.get("y_unit", ""))
        self.entry_yunit.bind('<Return>', lambda e: self.draw_graph())
        self.entry_yunit.bind('<FocusOut>', lambda e: self.draw_graph())

        self.var_y_log = tk.BooleanVar(value=self.settings.get("y_log", False))
        self.chk_y_log = ttk.Checkbutton(grid_l, text="Log", variable=self.var_y_log, command=self.draw_graph)
        self.chk_y_log.grid(row=1, column=4, sticky="w", padx=5)
        
        grid_l.columnconfigure(1, weight=1)

        # 4. 近似直線
        trend_frame = ttk.LabelFrame(left_panel, text="📈 近似直線 (範囲指定)", padding=10)
        trend_frame.pack(fill=tk.X, pady=(0, 10))
        
        # オプション類
        opt_frame = ttk.Frame(trend_frame)
        opt_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.var_show_r2 = tk.BooleanVar(value=self.settings.get("show_r2", True))
        self.chk_r2 = ttk.Checkbutton(opt_frame, text="$R^2$値を表示", variable=self.var_show_r2, command=self.draw_graph)
        self.chk_r2.pack(side=tk.LEFT)

        self.list_trends = tk.Listbox(trend_frame, height=3,
                                      bg=self.colors['input'], fg=self.colors['fg'],
                                      selectbackground=self.colors['accent'], 
                                      borderwidth=1, relief="sunken",
                                      exportselection=False)
        self.list_trends.pack(fill=tk.X, pady=(0, 5))
        self.list_trends.bind('<<ListboxSelect>>', self.on_trend_selected)
        
        btn_tr_f = ttk.Frame(trend_frame)
        btn_tr_f.pack(fill=tk.X)
        ttk.Button(btn_tr_f, text="+ 追加", command=self.add_trendline).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,2))
        ttk.Button(btn_tr_f, text="- 削除", command=self.remove_trendline).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2,0))

        # 5. 保存ボタン
        self.btn_save = ttk.Button(left_panel, text="💾 画像を保存 (Export)", command=self.save_image, style='Action.TButton')
        self.btn_save.pack(fill=tk.X, pady=10)


        # === 右パネル ===
        
        # グラフ
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        # 初期描画はsetup_matplotlib_styleで設定した通り
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar_frame = ttk.Frame(right_panel)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        toolbar.config(background=self.colors['bg'])
        for button in toolbar.winfo_children():
            try:
                button.config(background=self.colors['bg'])
            except: pass
        
        # スライダー
        slider_frame = ttk.LabelFrame(right_panel, text="近似範囲セレクター (選択中の範囲)", padding=10)
        slider_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.var_min = tk.DoubleVar(value=0)
        self.var_max = tk.DoubleVar(value=100)
        
        f_s1 = ttk.Frame(slider_frame)
        f_s1.pack(fill=tk.X)
        ttk.Label(f_s1, text="最小 (Min):", width=10).pack(side=tk.LEFT)
        self.scale_min = tk.Scale(f_s1, variable=self.var_min, orient=tk.HORIZONTAL,
                                  bg=self.colors['bg'], fg=self.colors['fg'], 
                                  troughcolor=self.colors['button'], 
                                  activebackground=self.colors['accent'],
                                  highlightthickness=0, borderwidth=0,
                                  command=self.on_slider_change)
        self.scale_min.pack(side=tk.LEFT, fill=tk.X, expand=True)

        f_s2 = ttk.Frame(slider_frame)
        f_s2.pack(fill=tk.X)
        ttk.Label(f_s2, text="最大 (Max):", width=10).pack(side=tk.LEFT)
        self.scale_max = tk.Scale(f_s2, variable=self.var_max, orient=tk.HORIZONTAL,
                                  bg=self.colors['bg'], fg=self.colors['fg'], 
                                  troughcolor=self.colors['button'], 
                                  activebackground=self.colors['accent'],
                                  highlightthickness=0, borderwidth=0,
                                  command=self.on_slider_change)
        self.scale_max.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def select_file(self):
        ftypes = [("Data Files", "*.csv *.xlsx *.xls"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(filetypes=ftypes)
        if path:
            self.filepath = path
            self.lbl_filename.config(text=os.path.basename(path))
            self.load_initial_data()

    def load_initial_data(self):
        ext = os.path.splitext(self.filepath)[1].lower()
        try:
            if ext == '.csv':
                encodings = ['utf-8', 'shift_jis', 'cp932']
                success = False
                for enc in encodings:
                    try:
                        self.df_raw = pd.read_csv(self.filepath, encoding=enc)
                        success = True
                        break
                    except UnicodeDecodeError:
                        continue
                if not success:
                    raise ValueError("対応できない文字コードです")
                
                self.sheet_map = {'Default': self.df_raw}
                self.combo_sheet['values'] = ['Default']
                self.combo_sheet.current(0)
                self.init_columns()
                
            elif ext in ['.xlsx', '.xls']:
                self.excel_file = pd.ExcelFile(self.filepath)
                sheets = self.excel_file.sheet_names
                self.combo_sheet['values'] = sheets
                if sheets:
                    self.combo_sheet.current(0)
                    self.on_sheet_selected(None)
        except Exception as e:
            messagebox.showerror("Error", f"ファイル読み込み失敗:\n{e}")

    def on_sheet_selected(self, event):
        sheet_name = self.combo_sheet.get()
        if not sheet_name: return
        try:
            if hasattr(self, 'excel_file'):
                self.df_raw = pd.read_excel(self.filepath, sheet_name=sheet_name)
            self.init_columns()
        except Exception as e:
            messagebox.showerror("Error", f"シート読み込み失敗:\n{e}")

    def init_columns(self):
        """データ読み込み後の列初期化処理"""
        if self.df_raw is None: return
        
        self.df_raw = self.df_raw.dropna(axis=1, how='all')
        self.df_raw = self.df_raw.loc[:, ~self.df_raw.columns.str.contains('^Unnamed')]
        
        columns = self.df_raw.columns.tolist()
        
        self.combo_x_col['values'] = columns
        if columns:
            self.combo_x_col.current(0)
        
        self.update_y_list()

    def update_y_list(self):
        if self.df_raw is None: return
        
        x_col_idx = self.combo_x_col.current()
        if x_col_idx < 0: return
        x_col_name = self.combo_x_col.get()
        
        self.list_cols.delete(0, tk.END)
        columns = self.df_raw.columns.tolist()
        for col in columns:
            self.list_cols.insert(tk.END, col)
        
        try:
            x_data = pd.to_numeric(self.df_raw[x_col_name], errors='coerce')
            min_val = np.nanmin(x_data)
            max_val = np.nanmax(x_data)
        except:
            min_val, max_val = 0, 100
        
        if np.isnan(min_val): min_val = 0
        if np.isnan(max_val): max_val = 100
        
        step = (max_val - min_val) / 1000 if max_val != min_val else 0.1
        self.scale_min.config(from_=min_val, to=max_val, resolution=step)
        self.scale_max.config(from_=min_val, to=max_val, resolution=step)
        self.var_min.set(min_val)
        self.var_max.set(max_val)
        
        self.draw_graph()

    def add_trendline(self):
        if self.df_raw is None: return
        idx = len(self.trendline_sets) + 1
        c_min = self.var_min.get()
        c_max = self.var_max.get()
        new_set = {'name': f"Range {idx}", 'min': c_min, 'max': c_max}
        self.trendline_sets.append(new_set)
        self.list_trends.insert(tk.END, new_set['name'])
        self.list_trends.selection_clear(0, tk.END)
        self.list_trends.selection_set(tk.END)
        self.draw_graph()

    def remove_trendline(self):
        sel = self.list_trends.curselection()
        if not sel: return
        idx = sel[0]
        self.list_trends.delete(idx)
        self.trendline_sets.pop(idx)
        self.draw_graph()

    def on_trend_selected(self, event):
        sel = self.list_trends.curselection()
        if not sel: return
        idx = sel[0]
        data = self.trendline_sets[idx]
        
        cmd_min = self.scale_min['command']
        cmd_max = self.scale_max['command']
        self.scale_min.config(command="")
        self.scale_max.config(command="")
        self.var_min.set(data['min'])
        self.var_max.set(data['max'])
        self.scale_min.config(command=cmd_min)
        self.scale_max.config(command=cmd_max)
        
        self.draw_graph()

    def on_slider_change(self, val):
        sel = self.list_trends.curselection()
        if not sel: return
        idx = sel[0]
        self.trendline_sets[idx]['min'] = self.var_min.get()
        self.trendline_sets[idx]['max'] = self.var_max.get()
        self.draw_graph()

    def combine_label(self, label, unit):
        if unit:
            if "^" in unit: return f"{label} [$\\mathrm{{{unit}}}$]"
            else: return f"{label} [{unit}]"
        return label

    def render_plot(self, ax):
        """描画ロジック（ライトモード前提）"""
        if self.df_raw is None: return

        # 設定反映
        settings = self.settings
        settings.update({
            "x_label": self.entry_xlabel.get(),
            "x_unit": self.entry_xunit.get(),
            "y_label": self.entry_ylabel.get(),
            "y_unit": self.entry_yunit.get(),
            "show_r2": self.var_show_r2.get(),
            "x_log": self.var_x_log.get(),
            "y_log": self.var_y_log.get()
        })

        x_col_idx = self.combo_x_col.current()
        if x_col_idx < 0: return
        x_col_name = self.combo_x_col.get()
        
        y_indices = self.list_cols.curselection()
        if not y_indices: return

        x_data_raw = self.df_raw[x_col_name]
        x_num_all = pd.to_numeric(x_data_raw, errors='coerce')
        
        max_val = 0
        
        # 色被りを防ぐため、プロット用と近似直線用でパレットを分離
        # プロット用: 寒色・中間色系 (青, 緑, 紫, 茶, シアン, 灰)
        plot_colors = ['#1f77b4', '#2ca02c', '#9467bd', '#8c564b', '#17becf', '#7f7f7f']
        # 近似直線用: 暖色・強調色系 (赤, オレンジ, ピンク, オリーブ, 黒)
        trend_colors = ['#d62728', '#ff7f0e', '#e377c2', '#bcbd22', '#000000']

        # 凡例収集用のリスト
        plot_handles = []
        plot_labels = []
        fit_handles = []
        fit_labels = []

        # --- データプロット ---
        for i, idx in enumerate(y_indices):
            col_name = self.df_raw.columns[idx]
            y_data_raw = self.df_raw[col_name]
            y_num = pd.to_numeric(y_data_raw, errors='coerce')
            
            mask = np.isfinite(x_num_all) & np.isfinite(y_num)
            if mask.sum() == 0: continue
            
            current_max = np.max(np.abs(y_num[mask]))
            if current_max > max_val: max_val = current_max

            series_color = plot_colors[i % len(plot_colors)]
            
            sc = ax.scatter(x_num_all[mask], y_num[mask], label=col_name, s=settings["marker_size"], color=series_color, alpha=0.8, zorder=3)
            plot_handles.append(sc)
            plot_labels.append(col_name)

            # --- 近似直線 ---
            for t_idx, t_set in enumerate(self.trendline_sets):
                r_min = t_set['min']
                r_max = t_set['max']
                
                # 計算には「指定された範囲」のデータのみを使用
                range_mask = mask & (x_num_all >= r_min) & (x_num_all <= r_max)
                
                if range_mask.sum() > 1:
                    try:
                        x_fit = x_num_all[range_mask].values.astype(float)
                        y_fit = y_num[range_mask].values.astype(float)
                        
                        # ログスケールの場合は <= 0 のデータを除外
                        valid_mask = np.full(x_fit.shape, True)
                        if settings["x_log"]:
                            valid_mask &= (x_fit > 0)
                        if settings["y_log"]:
                            valid_mask &= (y_fit > 0)
                            
                        x_fit = x_fit[valid_mask]
                        y_fit = y_fit[valid_mask]

                        if len(x_fit) < 2: continue

                        # フィッティングモードの決定と計算
                        # 1. Log-Log (両対数): log(y) = A * log(x) + B
                        if settings["x_log"] and settings["y_log"]:
                            log_x = np.log10(x_fit)
                            log_y = np.log10(y_fit)
                            z = np.polyfit(log_x, log_y, 1)
                            A = z[0] # Slope
                            B = z[1] # Intercept
                            
                            corr = np.corrcoef(log_x, log_y)
                            r2 = corr[0, 1]**2
                            
                            s_A = float_to_latex_sci(A)
                            s_B = float_to_latex_sci(abs(B))
                            sign = "+" if B >= 0 else "-"
                            trend_label = f"$\log(y)={s_A} \log(x) {sign} {s_B}$"
                            
                            func = lambda x: 10**(A * np.log10(x) + B)
                            
                        # 2. Semi-Log X (片対数X): y = A * log(x) + B
                        elif settings["x_log"] and not settings["y_log"]:
                            log_x = np.log10(x_fit)
                            z = np.polyfit(log_x, y_fit, 1)
                            A = z[0]
                            B = z[1]
                            
                            corr = np.corrcoef(log_x, y_fit)
                            r2 = corr[0, 1]**2
                            
                            s_A = float_to_latex_sci(A)
                            s_B = float_to_latex_sci(abs(B))
                            sign = "+" if B >= 0 else "-"
                            trend_label = f"$y={s_A} \log(x) {sign} {s_B}$"
                            
                            func = lambda x: A * np.log10(x) + B

                        # 3. Semi-Log Y (片対数Y): log(y) = A * x + B
                        elif not settings["x_log"] and settings["y_log"]:
                            log_y = np.log10(y_fit)
                            z = np.polyfit(x_fit, log_y, 1)
                            A = z[0]
                            B = z[1]
                            
                            corr = np.corrcoef(x_fit, log_y)
                            r2 = corr[0, 1]**2
                            
                            s_A = float_to_latex_sci(A)
                            s_B = float_to_latex_sci(abs(B))
                            sign = "+" if B >= 0 else "-"
                            trend_label = f"$\log(y)={s_A} x {sign} {s_B}$"
                            
                            func = lambda x: 10**(A * x + B)

                        # 4. Linear (通常): y = ax + b
                        else:
                            z = np.polyfit(x_fit, y_fit, 1)
                            p = np.poly1d(z)
                            
                            corr = np.corrcoef(x_fit, y_fit)
                            r2 = corr[0, 1]**2
                            
                            slope = float_to_latex_sci(z[0])
                            intercept = float_to_latex_sci(abs(z[1]))
                            sign = "+" if z[1] >= 0 else "-"
                            
                            trend_label = f"$y={slope}x {sign} {intercept}$"
                            func = p

                        if settings.get("show_r2", True):
                            trend_label += f", $R^2={r2:.3f}$"
                        
                        # 描画用x座標の生成
                        x_min_fit, x_max_fit = x_fit.min(), x_fit.max()
                        
                        # 範囲外への少しの延長
                        if settings["x_log"]:
                            # 対数軸の場合、少しマージンを取る計算
                            log_min = np.log10(x_min_fit)
                            log_max = np.log10(x_max_fit)
                            diff = log_max - log_min
                            if diff == 0: diff = 0.1
                            m = diff * 0.1
                            x_l = np.logspace(log_min - m, log_max + m, 100)
                        else:
                            x_range = x_max_fit - x_min_fit
                            if x_range == 0: x_range = 1
                            m = x_range * 0.1
                            x_l = np.linspace(x_min_fit - m, x_max_fit + m, 100)
                        
                        t_color = trend_colors[t_idx % len(trend_colors)]
                        
                        line, = ax.plot(x_l, func(x_l), color=t_color, linestyle='--', linewidth=2.0, alpha=0.9, label=trend_label, zorder=2)
                        
                        # 重複しないようにラベルを追加
                        if trend_label not in fit_labels:
                            fit_handles.append(line)
                            fit_labels.append(trend_label)
                        
                    except Exception as e:
                        # print(f"Trendline error: {e}") 
                        pass

        # x=0, y=0 のラインを強調 (ログスケールの場合は無視)
        if not settings["x_log"] and not settings["y_log"]:
            ax.axhline(0, color='gray', linewidth=1.0, zorder=1)
            ax.axvline(0, color='gray', linewidth=1.0, zorder=1)
        
        # 軸のスケール設定
        if settings["x_log"]:
            ax.set_xscale('log')
        if settings["y_log"]:
            ax.set_yscale('log')
        
        # 通常のグリッド線は設定に従う（視認性を上げるため明示的にスタイル指定）
        if settings["grid"]:
            ax.grid(True, which='major', linestyle='-', linewidth=0.5, color='#bfbfbf', alpha=1.0, zorder=0)
            ax.set_axisbelow(True)
        else:
            ax.grid(False)

        # 軸ラベル
        xlabel = self.combine_label(settings["x_label"], settings["x_unit"])
        ylabel = self.combine_label(settings["y_label"], settings["y_unit"])
        ax.set_xlabel(xlabel, fontsize=settings["font_size"]*1.5)
        ax.set_ylabel(ylabel, fontsize=settings["font_size"]*1.5)
        
        # 指数表記 (ログスケールでない場合のみ適用)
        if not settings["y_log"]:
            exponent = int(math.floor(math.log10(max_val))) if max_val != 0 else 0
            def sci_fmt(x, pos):
                if x==0: return "0"
                return r"${:.1f} \times 10^{{{}}}$".format(x / 10**exponent, exponent)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(sci_fmt))

        # --- 凡例の配置 (2箇所に分離) ---
        
        # 1. プロット凡例 (右上) - データが2つ以上ある場合のみ
        if len(plot_handles) > 1:
            l1 = ax.legend(plot_handles, plot_labels, loc='upper right', fontsize=settings["font_size"]*1.2, frameon=True)
            ax.add_artist(l1) # 2つ目の凡例を追加するために必要
            
        # 2. 近似直線凡例 (右下) - 近似直線がある場合のみ
        if fit_handles:
            ax.legend(fit_handles, fit_labels, loc='lower right', fontsize=settings["font_size"]*1.2, frameon=True)

    def draw_graph(self):
        self.ax.clear()
        self.render_plot(self.ax)
        save_settings(self.settings)
        self.fig.tight_layout()
        self.canvas.draw()

    def save_image(self):
        if self.filepath:
            default_name = os.path.splitext(os.path.basename(self.filepath))[0] + ".png"
        else:
            default_name = "graph.png"
            
        path = filedialog.asksaveasfilename(
            initialfile=default_name,
            filetypes=[("PNG Image", "*.png"), ("PDF", "*.pdf")]
        )
        if path:
            # 保存時も現在と同じ設定（標準配色）で保存
            self.fig.savefig(path, dpi=300)
            messagebox.showinfo("Saved", f"保存しました:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()