import numpy as np

def get_k_closest(li, item_idx, k):
	if k >= len(li):
		return li
	closest = []
	for i in range(item_idx - k, item_idx + k + 1):
		if i >= 0 and i < len(li) and i != item_idx:
			closest.append((li[i], abs(li[i] - li[item_idx])))
	return sorted(closest, key = lambda a: a[1])[:k]


if __name__ == '__main__':
	li = sorted([np.random.randint(100) for _ in range(100)])
	print(li[44])
	print(li[35:55])
	print(get_k_closest(li, 44, 4))