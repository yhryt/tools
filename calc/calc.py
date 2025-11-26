import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import pyperclip
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- 1. 計算で使うシンボルの定義 ---
x, y, z, t = sp.symbols('x y z t')
k, m, n = sp.symbols('k m n', integer=True)
a, b, c = sp.symbols('a b c', real=True)
theta, phi, omega = sp.symbols('theta phi omega')
hbar = sp.Symbol('hbar')
epsilon = sp.Symbol('epsilon')

class ScienceCalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tsukuba Science Calculator (GUI Ver.)")
        self.root.geometry("920x600") # キーパッドを横に配置するため横長に変更

        # スタイル設定
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("TEntry", font=("Consolas", 12))
        
        # --- メインレイアウト (左右分割) ---
        main_container = ttk.Frame(root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # 左側: 機能タブ (メインエリア)
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side='left', fill='both', expand=True)

        # 右側: 共通入力キーパッド
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side='right', fill='y', padx=(10, 0))

        # --- 左側: ノートブック設定 ---
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(expand=True, fill='both')

        # タブ1: 解析学
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text='解析学 (微積)')
        self.setup_analysis_tab()

        # タブ2: 線形代数
        self.tab_matrix = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_matrix, text='線形代数 (行列)')
        self.setup_matrix_tab()

        # --- 右側: キーパッド設定 ---
        self.setup_shared_keypad(right_frame)

    # =========================================
    #  タブ1: 解析学 UI
    # =========================================
    def setup_analysis_tab(self):
        frame = self.tab_analysis

        # --- 数式入力欄 ---
        input_frame = ttk.LabelFrame(frame, text="数式 (f(x))", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        self.expr_entry = ttk.Entry(input_frame, font=("Consolas", 14))
        self.expr_entry.pack(fill='x', pady=5)
        self.expr_entry.focus() # 初期フォーカス

        # --- 計算実行ボタン ---
        action_frame = ttk.LabelFrame(frame, text="計算実行", padding=10)
        action_frame.pack(fill='x', padx=10, pady=5)

        actions = [
            ("微分 (d/dx)", self.calc_diff),
            ("不定積分 (∫dx)", self.calc_integrate),
            ("定積分 (0→∞)", self.calc_definite_integrate),
            ("極限 (x→0)", self.calc_limit),
            ("簡約化", self.calc_simplify),
            ("展開", self.calc_expand),
            ("グラフ描画", self.calc_plot)
        ]
        
        # 3列で配置
        for i, (text, func) in enumerate(actions):
            btn = ttk.Button(action_frame, text=text, command=func)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        for i in range(3): action_frame.columnconfigure(i, weight=1)

        # --- 結果表示 ---
        self.create_result_area(frame, "ana")

    # =========================================
    #  タブ2: 線形代数 UI (グリッド入力)
    # =========================================
    def setup_matrix_tab(self):
        frame = self.tab_matrix

        # --- サイズ設定 ---
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(size_frame, text="行(Row):").pack(side='left')
        self.rows_var = tk.IntVar(value=2)
        ttk.Spinbox(size_frame, from_=1, to=5, textvariable=self.rows_var, width=3).pack(side='left', padx=5)
        
        ttk.Label(size_frame, text="列(Col):").pack(side='left', padx=(10,0))
        self.cols_var = tk.IntVar(value=2)
        ttk.Spinbox(size_frame, from_=1, to=5, textvariable=self.cols_var, width=3).pack(side='left', padx=5)
        
        ttk.Button(size_frame, text="グリッド作成", command=self.create_matrix_grid).pack(side='left', padx=20)

        # --- マトリクス入力グリッド ---
        self.grid_frame = ttk.LabelFrame(frame, text="行列入力 (キーパッド使用可)", padding=10)
        self.grid_frame.pack(padx=10, pady=5)
        
        self.matrix_entries = [] 
        self.create_matrix_grid() 

        # --- 計算実行ボタン ---
        action_frame = ttk.LabelFrame(frame, text="計算実行", padding=10)
        action_frame.pack(fill='x', padx=10, pady=5)

        actions = [
            ("固有値 (Eigen)", self.calc_eigen),
            ("行列式 (Det)", self.calc_det),
            ("逆行列 (Inv)", self.calc_inv),
            ("対角化 (Diag)", self.calc_diagonalize),
            ("転置 (Transpose)", self.calc_transpose),
            ("自乗 (M²)", self.calc_square)
        ]

        for i, (text, func) in enumerate(actions):
            btn = ttk.Button(action_frame, text=text, command=func)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        for i in range(3): action_frame.columnconfigure(i, weight=1)

        # --- 結果表示 ---
        self.create_result_area(frame, "mat")

    def create_matrix_grid(self):
        """指定されたサイズの入力グリッドを作成"""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        self.matrix_entries = []

        for r in range(rows):
            row_entries = []
            for c in range(cols):
                entry = ttk.Entry(self.grid_frame, width=12, font=("Consolas", 12), justify='center')
                entry.grid(row=r, column=c, padx=3, pady=3)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

    # =========================================
    #  共通: 入力キーパッド (右側に配置)
    # =========================================
    def setup_shared_keypad(self, parent):
        keypad_frame = ttk.LabelFrame(parent, text="キーパッド", padding=10)
        keypad_frame.pack(fill='both', expand=True)

        # 縦長レイアウトに対応するため列数を減らす (4列)
        keys = [
            ['Clr', 'BS', '(', ')'],
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', 'pi', '+'],
            ['sin', 'cos', 'tan', '^'],
            ['exp', 'log', 'sqrt', 'x'],
            ['y', 't', 'theta', 'omega'],
            ['hbar', 'epsilon', 'i', ''] # i を追加
        ]

        for r, row_keys in enumerate(keys):
            for c, key in enumerate(row_keys):
                if key == '': continue
                cmd = lambda k=key: self.on_key_click(k)
                
                width = 4
                if key in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'theta', 'omega', 'hbar', 'epsilon']: width = 5
                
                btn = ttk.Button(keypad_frame, text=key, width=width, command=cmd, takefocus=False)
                btn.grid(row=r, column=c, padx=2, pady=3, sticky='nsew')
        
        # グリッドの重み設定
        for i in range(4): keypad_frame.columnconfigure(i, weight=1)

    def on_key_click(self, key):
        """キーパッドが押された時の処理"""
        target = self.root.focus_get()

        if not isinstance(target, ttk.Entry) and not isinstance(target, tk.Entry):
            target = self.expr_entry # デフォルト

        try:
            cursor_pos = target.index(tk.INSERT)
        except:
            return 

        if key == 'Clr':
            target.delete(0, tk.END)
        elif key == 'BS':
            if cursor_pos > 0:
                target.delete(cursor_pos - 1, cursor_pos)
        else:
            text_to_insert = key
            if key == '^': text_to_insert = '**'
            if key in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']: text_to_insert += '('
            
            target.insert(cursor_pos, text_to_insert)

    # =========================================
    #  共通: 結果表示エリア
    # =========================================
    def create_result_area(self, parent, prefix):
        res_frame = ttk.LabelFrame(parent, text="計算結果", padding=10)
        res_frame.pack(fill='x', padx=10, pady=10)

        res_var = tk.StringVar()
        res_entry = ttk.Entry(res_frame, textvariable=res_var, font=("Consolas", 11), state='readonly')
        res_entry.pack(fill='x', pady=5)
        
        latex_frame = ttk.Frame(res_frame)
        latex_frame.pack(fill='x', pady=5)
        ttk.Label(latex_frame, text="LaTeX:").pack(side='left')
        
        latex_var = tk.StringVar()
        latex_entry = ttk.Entry(latex_frame, textvariable=latex_var, font=("Consolas", 10))
        latex_entry.pack(side='left', fill='x', expand=True, padx=5)

        ttk.Button(latex_frame, text="Copy", width=6,
                   command=lambda: self.copy_to_clipboard(latex_var.get())).pack(side='right')

        setattr(self, f"{prefix}_res_var", res_var)
        setattr(self, f"{prefix}_latex_var", latex_var)

    # =========================================
    #  ロジック: 解析学
    # =========================================
    def get_expr(self):
        txt = self.expr_entry.get()
        if not txt:
            return sp.Integer(0)
        txt = txt.replace('^', '**')
        # i を sp.I (虚数単位) として追加
        local_dict = {'x':x, 'y':y, 't':t, 'theta':theta, 'omega':omega, 'hbar':hbar, 'pi':sp.pi, 'i':sp.I}
        return sp.sympify(txt, locals=local_dict)

    def update_ana_result(self, result):
        self.ana_res_var.set(str(result))
        self.ana_latex_var.set(sp.latex(result))

    def calc_diff(self):
        try: self.update_ana_result(sp.diff(self.get_expr(), x))
        except Exception as e: self.ana_res_var.set(f"Error: {e}")

    def calc_integrate(self):
        try: self.update_ana_result(sp.integrate(self.get_expr(), x))
        except Exception as e: self.ana_res_var.set(f"Error: {e}")
    
    def calc_definite_integrate(self):
        try: self.update_ana_result(sp.integrate(self.get_expr(), (x, 0, sp.oo)))
        except Exception as e: self.ana_res_var.set(f"Error: {e}")

    def calc_limit(self):
        try: self.update_ana_result(sp.limit(self.get_expr(), x, 0))
        except Exception as e: self.ana_res_var.set(f"Error: {e}")
        
    def calc_simplify(self):
        try: self.update_ana_result(sp.simplify(self.get_expr()))
        except Exception as e: self.ana_res_var.set(f"Error: {e}")

    def calc_expand(self):
        try: self.update_ana_result(sp.expand(self.get_expr()))
        except Exception as e: self.ana_res_var.set(f"Error: {e}")

    def calc_plot(self):
        """グラフ描画機能"""
        try:
            expr = self.get_expr()
            
            try:
                f = sp.lambdify(x, expr, "numpy")
            except Exception:
                messagebox.showerror("Error", "プロットできるのは変数xを含む式のみです。")
                return

            plot_window = tk.Toplevel(self.root)
            plot_window.title("Graph Plot")
            plot_window.geometry("600x450")

            x_val = np.linspace(-10, 10, 400)
            try:
                y_val = f(x_val)
                if np.isscalar(y_val):
                    y_val = np.full_like(x_val, y_val)
            except Exception as e:
                messagebox.showerror("Error", f"計算エラー: 実数範囲で定義されていない可能性があります。\n{e}")
                plot_window.destroy()
                return

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(x_val, y_val, label=f"y = {sp.latex(expr)}")
            ax.axhline(0, color='black', linewidth=0.5)
            ax.axvline(0, color='black', linewidth=0.5)
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            # ax.legend() # 凡例を削除しました
            ax.set_title(f"Plot: {str(expr)}")

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"描画エラー: {e}")

    # =========================================
    #  ロジック: 線形代数
    # =========================================
    def get_matrix(self):
        rows = len(self.matrix_entries)
        cols = len(self.matrix_entries[0])
        matrix_data = []
        
        # i を sp.I (虚数単位) として追加
        local_dict = {'x':x, 'y':y, 't':t, 'epsilon':epsilon, 'omega':omega, 'hbar':hbar, 'i':sp.I}

        for r in range(rows):
            row_data = []
            for c in range(cols):
                val_txt = self.matrix_entries[r][c].get()
                if not val_txt: val_txt = "0"
                row_data.append(sp.sympify(val_txt, locals=local_dict))
            matrix_data.append(row_data)
            
        return sp.Matrix(matrix_data)

    def update_mat_result(self, result):
        self.mat_res_var.set(str(result))
        self.mat_latex_var.set(sp.latex(result))

    def calc_eigen(self):
        try:
            M = self.get_matrix()
            eigenvals = M.eigenvals()
            res_str = ", ".join([f"λ={sp.simplify(k)} (x{v})" for k, v in eigenvals.items()])
            self.mat_res_var.set(res_str)
            
            lat = []
            for val, count in eigenvals.items():
                lat.append(sp.latex(sp.simplify(val)))
            self.mat_latex_var.set(", ".join(lat))
        except Exception as e: self.mat_res_var.set(f"Error: {e}")

    def calc_det(self):
        try: self.update_mat_result(self.get_matrix().det())
        except Exception as e: self.mat_res_var.set(f"Error: {e}")

    def calc_inv(self):
        try: self.update_mat_result(self.get_matrix().inv())
        except Exception as e: self.mat_res_var.set(f"Error: {e}")

    def calc_diagonalize(self):
        try:
            M = self.get_matrix()
            P, D = M.diagonalize()
            self.mat_res_var.set(f"P={str(P)}, D={str(D)}")
            self.mat_latex_var.set(sp.latex(P) + r", \quad " + sp.latex(D))
        except Exception as e: self.mat_res_var.set(f"Error: {e}")

    def calc_transpose(self):
        try: self.update_mat_result(self.get_matrix().T)
        except Exception as e: self.mat_res_var.set(f"Error: {e}")
        
    def calc_square(self):
        try:
            M = self.get_matrix()
            self.update_mat_result(M * M)
        except Exception as e: self.mat_res_var.set(f"Error: {e}")

    def copy_to_clipboard(self, text):
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "LaTeXコードをコピーしました")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScienceCalcApp(root)
    root.mainloop()