import math
import diff_calc
class mods:
	def __init__(self):
		self.nomod = 1,
		self.nf = 0
		self.ez = 0
		self.hd = 0
		self.hr = 0
		self.dt = 0
		self.ht = 0
		self.nc = 0
		self.fl = 0
		self.so = 0
		speed_changing = self.dt | self.ht | self.nc
		map_changing = self.hr | self.ez | speed_changing

def base_strain(strain):
	return math.pow(5.0 * max(1.0, strain / 0.0675) - 4.0, 3.0) / 100000.0

def acc_calc(c300, c100, c50, misses):
	total_hits = c300 + c100 + c50 + misses
	acc = 0.0
	if total_hits > 0:
		acc = (c50 * 50.0 + c100 * 100.0 + c300 * 300.0) / (total_hits * 300.0)
	return acc

class pp_calc_result:
	def __init__(self):
		self.acc_percent = 0
		self.pp = 0
		self.aim_pp = 0
		self.speed_pp = 0
		self.acc_pp = 0

def pp_calc(aim, speed, b, misses, c100, c50, used_mods = mods() ,combo = 0xFFFF, score_version = 1, c300 = 0xFFFF):
	res = pp_calc_result()
	od = b.od
	ar = b.ar
	circles = b.num_circles

	if c100 > b.num_objects or c50 > b.num_objects or misses > b.num_objects:
		print("Invalid accuracy number")
		return res

	if c300 == 0xFFFF:
		c300 = b.num_objects - c100 - c50 - misses

	if combo == 0xFFFF:
		combo = b.max_combo
	elif combo == 0:
		print("Invalid combo count")
		return res

	total_hits = c300 + c100 + c50 + misses
	if total_hits != b.num_objects:
		print("warning hits != objects")

	if score_version != 1 and score_version != 2:
		print("Score version not found")
		return res

	acc = acc_calc(c300,c100,c50,misses)
	res.acc_percent = acc * 100.0

	if used_mods.td:
		aim = math.pow(aim, 0.8)

	aim_value = base_strain(aim)

	total_hits_over_2k = total_hits / 2000.0
	length_bonus = 0.95 + 0.4 * min(1.0, total_hits_over_2k) + (math.log10(total_hits_over_2k) * 0.5 if total_hits > 2000 else 0.0)

	miss_penalty = math.pow(0.97,misses)

	combo_break = math.pow(combo, 0.8) / math.pow(b.max_combo,0.8)

	aim_value *= length_bonus
	aim_value *= miss_penalty
	aim_value *= combo_break
	ar_bonus = 1.0

	if ar > 10.33:
		ar_bonus += 0.3 * (ar - 10.33)
	elif ar < 8:
		ar_bonus += 0.01*(8.0 - ar)

	

	aim_value *= ar_bonus
	hd_bonus = 1.0
	if used_mods.hd:
		hd_bonus = 1.0 + 0.04*(12 - ar)
	aim_value *= hd_bonus

	hardSliders = b.NumSliders() * 0.15

	if b.NumSliders() > 0:
		_maxCombo = b.maxCombo
		estimateEndsDropped = math.min(math.max(math.min((c100 + c50 + misses), _maxCombo - 

	acc_bonus = 0.5 + acc / 2.0

	od_bonus = 0.98 + math.pow(od,2) / 2500.0

	aim_value *= acc_bonus
	aim_value *= od_bonus

	res.aim_pp = aim_value

	speed_value = base_strain(speed)

	speed_value *= length_bonus
	speed_value *= miss_penalty
	speed_value *= combo_break
	if(ar > 10.33):
		speed_value *= ar_bonus
	speed_value *= hd_bonus
	speed_value *= 0.02 + acc
	speed_value *= 0.96 + (math.pow(od, 2) / 1600)
	
	res.speed_pp = speed_value

	real_acc = 0.0

	if score_version == 2:
		circles = total_hits
		real_acc = acc
	else:
		if circles:
			real_acc = ((c300 - (total_hits - circles)) * 300.0 + c100 * 100.0 + c50 * 50.0) / (circles * 300)
		real_acc = max(0.0,real_acc)

	acc_value = math.pow(1.52163, od) * math.pow(real_acc, 24.0) * 2.83
	
	acc_value *= min(1.15, math.pow(circles / 1000.0, 0.3))

	if used_mods.hd:
		acc_value *= 1.08

	if used_mods.fl:
		acc_value *= 1.02

	res.acc_pp = acc_value
        
	final_multiplier = 1.14

	if used_mods.nf:
		final_multiplier *= math.max(0.9, 1.0 - 0.02 * numMiss)

	if used_mods.so:
		final_multiplier *= 1.0 - math.pow(b.NumSpinners() / total_hits, 0.85)
		
	res.pp = math.pow(math.pow(aim_value,1.1) + math.pow(speed_value,1.1) + math.pow(acc_value, 1.1), 1.0 / 1.1) * final_multiplier
	return res;

def pp_calc_acc(aim, speed, b, acc_percent, used_mods = mods(), combo = 0xFFFF, misses = 0,score_version = 1):
	misses = min(b.num_objects,misses)

	max300 = (b.num_objects - misses)
	
	acc_percent = max(0.0, min(acc_calc(max300, 0, 0, misses) * 100.0, acc_percent))

	c50 = 0

	c100 = round(-3.0 * ((acc_percent * 0.01 - 1.0) * b.num_objects + misses) * 0.5)

	if c100 > b.num_objects - misses:
		c100 = 0
		c50 = round(-6.0 * ((acc_percent * 0.01 - 1.0) * b.num_objects + misses) * 0.2);

		c50 = min(max300, c50)
	else:
		c100 = min(max300, c100)

	c300 = b.num_objects - c100 - c50 - misses

	return pp_calc(aim,speed,b,misses,c100,c50,used_mods, combo, score_version,c300)
