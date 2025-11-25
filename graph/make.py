import os

# 10のマイナス10乗オーダーのデータ
csv_content = """Time [s],Theory [A],Experiment [A]
0.0, 0.0, 0.0
1.0, 1.0e-10, 1.1e-10
2.0, 2.0e-10, 1.9e-10
3.0, 3.0e-10, 3.05e-10
4.0, 4.0e-10, 3.95e-10
5.0, 5.0e-10, 5.1e-10
"""

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'data_exp.csv')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(csv_content)

print(f"テストデータ '{file_path}' を作成しました。")