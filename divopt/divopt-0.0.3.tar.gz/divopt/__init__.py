
# 3分凸最適化 [divopt]

import sys
import copy
import random
import numpy as np
from sout import sout
from tqdm import tqdm

# 次元数のチェック
def check_dim(arg_vec, dim_n):
	# numpy の arrayも受け付けたいのでlist型チェックはしない
	# if type(arg_vec) != type([]): raise Exception("[divopt error] vec type must be list.")
	if len(arg_vec) != dim_n: raise Exception("[divopt error] The dimension of the vector is incorrect.")
	return True

# 最大化・最小化問題の指定をプラスマイナス1の数値に変換する (最大化: +1, 最小化: -1)
def direction_to_sign(direction):
	if direction == "minimize":
		direc_sign = -1
	elif direction == "maximize":
		direc_sign = +1
	else:
		raise Exception("[divopt error] direction parameter is invalid.")
	return direc_sign

# 最適化対象関数の例を生成 [divopt]
def gen_example_func(
	ans,	# 最適値(答え)のベクトル
	direction = "minimize"	# 最大化 / 最小化
):
	# 次元数
	dim_n = len(ans)
	# 最大化・最小化問題の指定をプラスマイナス1の数値に変換する (最大化: +1, 最小化: -1)
	direc_sign = direction_to_sign(direction)
	# 関数の定義
	def func(x):
		# 次元数のチェック
		check_dim(x, dim_n)
		# 各軸について二次関数を加える
		value = 0
		for i in range(dim_n):
			value += (x[i] - ans[i]) ** 2
		# 最大化問題のときは符号を反転する
		value = value * direc_sign * (-1)
		return value
	return func

# 探索範囲の初期仮説を生成
def gen_init_range_hypos(
	limit	# 探索範囲 (制約条件)
):
	# 初期仮説で端にどの程度隙間を空けておくか
	margin_ratio = 1/4
	# 初期仮説範囲を計算する
	lower_lim, upper_lim = limit
	width = upper_lim - lower_lim
	margin = width * margin_ratio
	lower_hypos = lower_lim + margin
	upper_hypos = upper_lim - margin
	range_hypos = (lower_hypos, upper_hypos)
	return range_hypos

# 「範囲の仮説」からpivot値を算出 (他軸探索時の仮の値)
def calc_pivot(range_hypos):
	lower_lim, upper_lim = range_hypos
	# pivotはちょうどまんなかに取る
	pivot = (lower_lim + upper_lim) / 2
	return pivot

# 探索メモの初期化
def init_memo(lim_range, dim_n):
	memo = {}
	# 次元数
	memo["dim_n"] = dim_n
	# 各軸のメモを記録
	memo["ax_memo"] = []
	for ax_i in range(dim_n):
		one_ax_memo = {}
		# 探索範囲 (制約条件)
		one_ax_memo["limit"] = lim_range[ax_i]
		# 範囲の現時点の仮説 (ここでは初期仮説を格納)
		one_ax_memo["range_hypos"] = gen_init_range_hypos(one_ax_memo["limit"])	# 探索範囲の初期仮説を生成
		# pivot値の初期値を格納 (他軸探索時の仮の値)
		one_ax_memo["pivot"] = calc_pivot(one_ax_memo["range_hypos"])	# 「範囲の仮説」からpivot値を算出 (他軸探索時の仮の値)
		# 着目軸に関するメモを格納
		memo["ax_memo"].append(one_ax_memo)
	return memo

# 無限に続く自然数列
def inf_int():
	cnt = 0
	while True:
		yield cnt
		cnt += 1

# rep回数に基づく終了判定
def rep_fin_judge(th_value, cnt):
	if cnt >= th_value:
		return True
	else:
		return False

# 終了条件の判定
def judge_fin(fin_judge, cnt):
	mode = fin_judge[0]
	if mode == "rep":
		# rep回数に基づく終了判定
		return rep_fin_judge(fin_judge[1], cnt)
	else:
		raise Exception("[divopt error] invalid fin_judge mode.")

# 軸をランダムに選ぶ
def ax_choice(rand_obj, dim_n):
	r = rand_obj.random()
	ax_idx = int(r * dim_n)
	return ax_idx

# memoからpivot位置を取得
def get_pivot_vec(memo):
	pivot_vec = [e["pivot"]
		for e in memo["ax_memo"]]
	return pivot_vec

# 探索点を出力する関数を生成 (pivotの着目軸のみrange_hypos内の内分点に書き換えたもの)
def gen_search_x_func(
	pivot_vec, ax_idx,
	range_hypos
):
	def search_x_func(ratio):
		# 汚染防止した下地ベクトルの生成
		ret_vec = copy.copy(pivot_vec)
		# 内分点を求める
		lim_0, lim_1 = range_hypos
		new_value = lim_0 + (lim_1 - lim_0) * ratio
		# 書き換え
		ret_vec[ax_idx] = new_value
		return ret_vec
	return search_x_func

# 新しいrange_hyposを生成
def gen_new_rh(d1, d3, direc):
	if direc == "left":
		rh_L, rh_R = (0 - d1), (0 - d3)
	elif direc == "right":
		rh_L, rh_R = (1 + d3), (1 + d1)
	return rh_L, rh_R

# 値がlimit内にあるかどうかを判定 (両端含む)
def judge_within(value, limit):
	lim_0, lim_1 = limit
	if value < lim_0: return False
	if value > lim_1: return False
	return True

# 領域を広げる
def expand(search_x_func, func, ax_limit, ax_idx, direc):
	# 端部のratio
	frontier_r = {"left": 0, "right": 1}[direc]
	# 直前のy値
	pre_y = func(search_x_func(frontier_r))
	# 所定距離離れた場所を取得する関数
	d_getter = {
		"left": lambda d: 0 - d,
		"right": lambda d: 1 + d
	}[direc]
	# 拡張距離履歴
	dist_hist = [-1/3, 0, 1/3]
	while True:
		# 新しい探索場所
		x = search_x_func(d_getter(dist_hist[-1]))
		# 終了条件その1: 世界の終わりに達した場合
		if judge_within(x[ax_idx], ax_limit) is False: break	# 値がlimit内にあるかどうかを判定 (両端含む)
		# 終了条件その2: 小さくなった場合
		post_y = func(x)
		if post_y < pre_y: return gen_new_rh(dist_hist[-1], dist_hist[-3], direc)	# 新しいrange_hyposを生成
		# pre_yを更新
		pre_y = post_y
		# 距離を更新
		dist_hist.append(dist_hist[-1] * 3/2)
	# 世界の終わりに達した場合の返り値
	if direc == "left":
		rh_L, rh_R = ax_limit[0], (0 - dist_hist[-3])
	elif direc == "right":
		rh_L, rh_R = (1 + dist_hist[-3]), ax_limit[1]
	return rh_L, rh_R

# 探索点4つから新しいrange_hyposを計算
def calc_new_range_hypos(search_x_func, func, ax_limit, ax_idx):
	# 探索点4つのy座標 (出力) の計算
	y_ls = [func(search_x_func(r))
		for r in [0,1/3,2/3,1]]
	# y_lsの最大値がどれかを得る
	max_i = np.argmax(y_ls)
	# 場合分け
	if max_i == 0:
		# 左へ領域を「広げる」
		rh_L, rh_R = expand(search_x_func, func, ax_limit, ax_idx, direc = "left")	# 領域を広げる
	elif max_i == 1:
		# 左の2領域に「縮める」
		rh_L, rh_R = 0, 2/3
	elif max_i == 2:
		# 右の2領域に「縮める」
		rh_L, rh_R = 1/3, 1
	elif max_i == 3:
		# 右へ領域を「広げる」
		rh_L, rh_R = expand(search_x_func, func, ax_limit, ax_idx, direc = "right")	# 領域を広げる
	else:
		raise Exception("実装に誤りがあります")
	# rh_L, rh_Rから新しいrangeの仮説を生成
	new_range_hypos = (
		search_x_func(rh_L)[ax_idx],
		search_x_func(rh_R)[ax_idx]
	)
	return new_range_hypos

# 指定された軸の範囲絞り込み (memo内容を更新)
def update_ax_range(ax_idx, memo, func):
	# 着目軸のmemo
	ax_memo = memo["ax_memo"][ax_idx]
	# range_hyposが幅0の場合はこの軸の探索をスキップする
	rh_L, rh_R = ax_memo["range_hypos"]
	if rh_L == rh_R: return None
	# memoからpivot位置を取得
	pivot_vec = get_pivot_vec(memo)
	# 探索点を出力する関数を生成 (pivotの着目軸のみrange_hypos内の内分点に書き換えたもの)
	search_x_func = gen_search_x_func(
		pivot_vec, ax_idx,
		ax_memo["range_hypos"]
	)
	# 探索点4つから新しいrange_hyposを計算
	new_range_hypos = calc_new_range_hypos(
		search_x_func, func, ax_memo["limit"], ax_idx)
	ax_memo["range_hypos"] = new_range_hypos
	new_pivot = calc_pivot(new_range_hypos)	# 「範囲の仮説」からpivot値を算出 (他軸探索時の仮の値)
	ax_memo["pivot"] = new_pivot

# 最適化 [divopt]
def optimize(
	func,	# 最適化対象関数
	dim_n,	# 入力の次元数
	lim_range,	# 各軸の範囲
	fin_judge = ["rep", 1000],	# 終了条件 (指定: [mode, value])
	direction = "minimize",	# 最大化 / 最小化
	seed = 23	# 探索時に用いる乱数のシード値
):
	if direction != "maximize": raise Exception("[error] maximize以外は未実装です")
	# 乱数を使う別のモジュールに影響を与えぬよう、シードを固定する範囲を囲い込む
	rand_obj = random.Random(seed)
	# 探索メモの初期化
	memo = init_memo(lim_range, dim_n)
	# 終了条件を満たすまで繰り返す
	for cnt in tqdm(inf_int()):	# 無限に続く自然数列
		# 終了条件の判定
		if judge_fin(fin_judge, cnt): break
		# 軸をランダムに選ぶ
		ax_idx = ax_choice(rand_obj, dim_n)
		# 指定された軸の範囲絞り込み (memo内容を更新)
		update_ax_range(ax_idx, memo, func)
	# pivotを最適値として出力する
	opt_x = get_pivot_vec(memo)	# memoからpivot位置を取得
	return opt_x

# 最適性判断 [divopt]
def is_optimal(
	func,	# 最適化対象関数
	x,	# 検査したい解
	delta,	# 許容誤差
	lim_range,	# 各軸の範囲
	direction = "minimize"	# 最大化 / 最小化
):
	if direction != "maximize": raise Exception("[error] maximize以外は未実装です")
	# 基準y値
	base_y = func(x)
	dim_n = len(x)
	for ax_i in range(dim_n):
		for sign in [-1, 1]:
			check_x = copy.copy(x)
			new_value = check_x[ax_i] + sign * delta
			# チェック点が範囲外の場合はチェックしない (その方向はすでに最適であるとみなす)
			if judge_within(new_value, lim_range[ax_i]) is False: continue	# 値がlimit内にあるかどうかを判定 (両端含む)
			check_x[ax_i] = new_value
			y = func(check_x)
			# 誤っている場合
			if y > base_y: return False
	# すべてのテストに合格した場合
	return True

# 初回空打ちで情報を取得
def get_init_info(target_func):
	# 情報取得用のダミーtrialオブジェクト
	class DummyTrial:
		# 初期化処理
		def __init__(self):
			self.info = {
				"param_names": [],
				"lim_range": [],
				"dim_n": 0
			}
		# パラメータの提案
		def suggest_float(self, param_name, lower_limit, upper_limit):
			dummy_value = (lower_limit + upper_limit) / 2
			# すでに登録されている場合はスルー
			if param_name in self.info["param_names"]: return dummy_value
			self.info["param_names"].append(param_name)
			self.info["lim_range"].append((lower_limit, upper_limit))
			self.info["dim_n"] += 1
			return dummy_value
	d_trial = DummyTrial()
	_ = target_func(d_trial)
	return d_trial.info

# optunaのtrialオブジェクトの模倣
class OptunaTrial:
	# 初期化処理
	def __init__(self, x, info):
		self.params = {
			info["param_names"][i]: x[i]
			for i in range(info["dim_n"])
		}
	# 実数値の取得
	def suggest_float(self, param_name, lower_limit, upper_limit):
		return self.params[param_name]

# optuna様のtarget_funcを呼ぶラッパーを生成
def gen_wrapper_func(target_func, info):
	def wrapper_func(x):
		# optunaのtrialオブジェクトの模倣
		trial = OptunaTrial(x, info)
		res = target_func(trial)
		return res
	return wrapper_func

# optunaのstudyオブジェクトの模倣
class OptunaStudy:
	# 初期化処理
	def __init__(self, direction = "minimize"):
		self.direction = direction
		self.optimize_done_flag = False
	# 最適化
	def optimize(self, target_func, n_trials):
		if self.optimize_done_flag is True:
			raise Exception("[divopt error] 追加最適化には未対応です")
		# 初回空打ちで情報を取得
		self.info = get_init_info(target_func)
		# optuna様のtarget_funcを呼ぶラッパーを生成
		self.wrapper_func = gen_wrapper_func(target_func, self.info)
		# 最適化 [divopt]
		self.best_x = optimize(
			func = self.wrapper_func,	# 最適化対象関数
			dim_n = self.info["dim_n"],	# 入力の次元数
			lim_range = self.info["lim_range"],	# 各軸の範囲
			fin_judge = ["rep", n_trials],	# 終了条件 (指定: [mode, value])
			direction = self.direction	# 最大化 / 最小化
		)
		# best_paramsを束縛する
		self.best_params = {
			self.info["param_names"][i]: self.best_x[i]
			for i in range(self.info["dim_n"])
		}
		self.optimize_done_flag = False
	# 最適性判断 [divopt]
	def is_optimal(self, delta):
		# 最適性判断 [divopt]
		return is_optimal(
			func = self.wrapper_func,	# 最適化対象関数
			x = self.best_x,	# 検査したい解
			delta = delta,	# 許容誤差
			lim_range = self.info["lim_range"],	# 各軸の範囲
			direction = self.direction	# 最大化 / 最小化
		)

# optuna様インターフェース
class OptunaInterface:
	# 初期化処理
	def __init__(self):
		pass
	# studyの作成
	def create_study(self, direction):
		# optunaのstudyオブジェクトの模倣
		study = OptunaStudy(direction)
		return study

# 実体化しておく
optuna_interface = OptunaInterface()
