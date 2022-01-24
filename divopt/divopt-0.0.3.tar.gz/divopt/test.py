
# 3分凸最適化 [divopt]
# 【動作確認 / 使用例】

import sys
import random
from ezpip import load_develop
# 3分凸最適化 [divopt]
divopt = load_develop("divopt", "../", develop_flag = True)

dim_n = 50

# 最適化対象関数の例を生成 [divopt]
func = divopt.gen_example_func(
	ans = [0.3 for _ in range(dim_n)],	# 最適値(答え)のベクトル
	direction = "maximize"	# 最大化 / 最小化
)

lim_range = [(0,1) for _ in range(dim_n)]

# 最適化 [divopt]
res = divopt.optimize(
	func = func,	# 最適化対象関数
	dim_n = dim_n,	# 入力の次元数
	lim_range = lim_range,	# 各軸の範囲
	fin_judge = ["rep", 500],	# 終了条件 (指定: [mode, value])
	direction = "maximize"	# 最大化 / 最小化
)

# debug
print(res)

# 最適性判断 [divopt]
flag = divopt.is_optimal(
	func = func,	# 最適化対象関数
	x = res,	# 検査したい解
	delta = 0.02,	# 許容誤差
	lim_range = lim_range,	# 各軸の範囲
	direction = "maximize"	# 最大化 / 最小化
)

# debug
print(flag)

# optunaのIFに合わせた目的関数
def target_func(trial):
	x = []
	for i in range(dim_n):
		x.append(trial.suggest_float("param_%d"%i, 0, 1))
	return func(x)

# optuna様インターフェース
oi = divopt.optuna_interface
study = oi.create_study(
	direction = "maximize"
)
study.optimize(target_func, n_trials = 500)
flag = study.is_optimal(delta = 0.05)	# 最適性判断 [divopt]
print(flag)
print(study.best_params)
