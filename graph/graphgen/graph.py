import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import sys
import math
import json
import platform

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
    # デザイン設定のデフォルト
    default_font = get_system_font()
    
    default_settings = {
        # --- 記憶される入力値 ---
        "x_label": "", "x_unit": "",
        "y_label": "", "y_unit": "",
        "use_trendline": "n",
        
        # --- デザイン設定 ---
        "font_family": default_font,
        "font_size": 12,
        "figure_size": [10, 6],
        "marker_size": 30,
        "dpi": 300,
        "grid": False
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                default_settings.update(user_settings)
                return default_settings
        except:
            return default_settings
    return default_settings

def save_settings(settings):
    """設定を保存する"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"設定の保存に失敗しました: {e}")

def get_input_with_memory(prompt, key, settings, required=True):
    """記憶機能付き入力"""
    default_val = settings.get(key, "")
    prompt_text = f"{prompt}"
    if default_val:
        prompt_text += f" [前回: {default_val}]"
    prompt_text += ": "
    
    while True:
        user_val = input(prompt_text).strip()
        if user_val == "":
            if default_val: return default_val
            if not required: return ""
            print("エラー: 入力は必須です。")
            continue
        return user_val

def float_to_latex_sci(val):
    """数値をLaTeX形式の科学的表記に変換"""
    if val == 0: return "0"
    sci_str = "{:.2e}".format(val)
    mantissa, exponent = sci_str.split('e')
    exp_int = int(exponent)
    if exp_int == 0: return mantissa
    return r"{} \times 10^{{{}}}".format(mantissa, exp_int)

def load_data(file_path):
    """ファイルを読み込み、DataFrameを返す"""
    ext = os.path.splitext(file_path)[1].lower()
    basename = os.path.basename(file_path)
    
    try:
        if ext == '.csv':
            return pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            target_sheet = None
            
            print(f"\nファイル '{basename}' 内のシート一覧:")
            for i, name in enumerate(sheet_names):
                print(f"  [{i + 1}] {name}")
            
            while True:
                prompt_msg = "\n読み込むシートの番号を入力 (Enterで1番目を選択): "
                user_input = input(prompt_msg).strip()
                if user_input == "":
                    if len(sheet_names) > 0:
                        target_sheet = sheet_names[0]
                        print(f"シート '{target_sheet}' を選択しました（デフォルト）。")
                        break
                try:
                    sheet_idx = int(user_input) - 1
                    if 0 <= sheet_idx < len(sheet_names):
                        target_sheet = sheet_names[sheet_idx]
                        print(f"シート '{target_sheet}' を選択しました。")
                        break
                    else: print(f"エラー: 1～{len(sheet_names)}で入力してください")
                except ValueError: print("エラー: 半角数字を入力してください")
            
            return pd.read_excel(file_path, sheet_name=target_sheet)
        else:
            print("エラー: 非対応形式です")
            return None
    except Exception as e:
        print(f"読み込みエラー: {e}")
        return None

def create_graph(file_path, x_label_text, y_label_text, settings, show_trendline=False):
    """グラフ作成のメイン処理"""
    
    # 1. 設定反映
    plt.rcParams['font.family'] = settings.get("font_family", get_system_font())
    plt.rcParams['font.size'] = settings.get("font_size", 12)
    plt.rcParams['mathtext.fontset'] = 'cm' 
    plt.rcParams['mathtext.default'] = 'it' 
    
    # 2. データ読み込み
    df = load_data(file_path)
    if df is None: return
    if df.shape[1] < 2:
        print("エラー: データは最低でも2列（X軸とY軸）必要です。")
        return

    # 3. 出力パス設定
    script_dir = os.path.dirname(os.path.abspath(file_path))
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(script_dir, base_name + ".png")

    print(f"グラフを描画中... (出力: {os.path.basename(output_path)})")
    
    fig_sz = settings.get("figure_size", [10, 6])
    fig, ax = plt.subplots(figsize=(fig_sz[0], fig_sz[1]))
    
    x_data = df.iloc[:, 0]
    
    # 最大値計算（エラーハンドリング強化）
    try:
        # 数値データのみを抽出して最大値を探す
        numeric_df = df.iloc[:, 1:].select_dtypes(include=['number'])
        if not numeric_df.empty:
            all_vals = numeric_df.values.flatten()
            # NaNを除去
            all_vals = all_vals[~np.isnan(all_vals)]
            max_val = max([abs(y) for y in all_vals]) if len(all_vals) > 0 else 0
        else:
            max_val = 0
    except Exception as e:
        print(f"警告: 最大値計算中にエラー ({e})。指数表記を無効化します。")
        max_val = 0
        
    exponent = int(math.floor(math.log10(max_val))) if max_val != 0 else 0
    mk_sz = settings.get("marker_size", 30)

    # 4. プロットループ
    for i in range(1, len(df.columns)):
        col_name = df.columns[i]
        y_data = df.iloc[:, i]
        
        # データチェック: 数値変換できないデータが含まれているか確認
        try:
            x_num = pd.to_numeric(x_data, errors='coerce')
            y_num = pd.to_numeric(y_data, errors='coerce')
        except:
            print(f"スキップ: 列 '{col_name}' は数値データとして読み込めませんでした。")
            continue
            
        # NaNを除去したマスクを作成
        mask = np.isfinite(x_num) & np.isfinite(y_num)
        
        if mask.sum() == 0:
            print(f"スキップ: 列 '{col_name}' に有効なデータ点がありません。")
            continue

        label_str = col_name
        x_line, y_line = None, None
        
        # 近似直線
        if show_trendline and mask.sum() > 1:
            try:
                x_fit = x_num[mask]
                y_fit = y_num[mask]
                z = np.polyfit(x_fit, y_fit, 1)
                p = np.poly1d(z)
                
                # R^2
                correlation_matrix = np.corrcoef(x_fit, y_fit)
                r_squared = correlation_matrix[0, 1]**2

                slope_latex = float_to_latex_sci(z[0])
                intercept_latex = float_to_latex_sci(abs(z[1]))
                sign = "+" if z[1] >= 0 else "-"
                
                label_str += f" ($y={slope_latex}x {sign} {intercept_latex}, R^2={r_squared:.4f}$)"
                
                x_min, x_max = x_fit.min(), x_fit.max()
                x_line = np.linspace(x_min, x_max, 100)
                y_line = p(x_line)
            except Exception as e:
                print(f"警告: {col_name} の近似計算失敗 ({e})")

        sc = ax.scatter(x_num, y_num, label=label_str, marker='o', s=mk_sz)
        
        if x_line is not None:
            color = sc.get_facecolors()[0]
            ax.plot(x_line, y_line, color=color, linestyle='--', linewidth=1, alpha=0.8)

    # 5. 装飾
    ax.set_xlabel(x_label_text)
    ax.set_ylabel(y_label_text)
    ax.grid(settings.get("grid", False))
    ax.tick_params(axis='both', direction='in', which='both', top=True, right=True)

    def scientific_formatter(x, pos):
        if x == 0: return "0"
        coeff = x / (10 ** exponent)
        return r"${:.1f} \times 10^{{{}}}$".format(coeff, exponent)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_formatter))

    if len(df.columns) > 1 or show_trendline:
        # 凡例がある場合のみ表示
        legend = ax.legend(frameon=True, fontsize=settings.get("font_size", 12) * 0.9, edgecolor='black', fancybox=False)
        handles = getattr(legend, 'legend_handles', None) or getattr(legend, 'legendHandles', None)
        if handles:
            for handle in handles:
                handle.set_sizes([mk_sz * 1.5])
        legend.get_frame().set_linewidth(1.0)

    plt.tight_layout()
    
    try:
        plt.savefig(output_path, dpi=settings.get("dpi", 300))
        print("-" * 30)
        print(f"処理完了: 画像を保存しました -> {output_path}")
        print("-" * 30)
    except Exception as e:
        print(f"保存エラー: {e}")
    finally:
        plt.close()

def combine_label_and_unit(label, unit):
    if unit:
        if "^" in unit: return f"{label} [$\\mathrm{{{unit}}}$]"
        else: return f"{label} [{unit}]"
    return label

if __name__ == "__main__":
    print("\n=== グラフ作成ツール（Pro版） ===")
    
    settings = load_settings()
    
    target_file = ""
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        print(f"読み込みファイル: {os.path.basename(target_file)}")
    else:
        current_dir = os.getcwd()
        while True:
            target_file = input("読み込むファイル名(csv/xlsx): ").strip()
            if not target_file: continue
            if os.path.exists(target_file): break
            elif os.path.exists(os.path.join(current_dir, target_file)):
                target_file = os.path.join(current_dir, target_file)
                break
            else: print("エラー: ファイルが見つかりません")

    print("\n--- 軸ラベルと単位の設定 (Enterで前回の値を使用) ---")
    
    x_label_base = get_input_with_memory("X軸のラベル名", "x_label", settings)
    x_unit = get_input_with_memory("X軸の単位", "x_unit", settings, required=False)
    my_xlabel = combine_label_and_unit(x_label_base, x_unit)
    
    y_label_base = get_input_with_memory("Y軸のラベル名", "y_label", settings)
    y_unit = get_input_with_memory("Y軸の単位", "y_unit", settings, required=False)
    my_ylabel = combine_label_and_unit(y_label_base, y_unit)
    
    print("-" * 10)
    
    trend_input = get_input_with_memory("近似直線を追加しますか？ (y/n)", "use_trendline", settings)
    use_trendline = (trend_input.lower() in ['y', 'yes'])

    # 入力内容のみ保存（デザイン設定は維持）
    settings.update({
        "x_label": x_label_base,
        "x_unit": x_unit,
        "y_label": y_label_base,
        "y_unit": y_unit,
        "use_trendline": trend_input
    })
    save_settings(settings)

    create_graph(target_file, my_xlabel, my_ylabel, settings, show_trendline=use_trendline)