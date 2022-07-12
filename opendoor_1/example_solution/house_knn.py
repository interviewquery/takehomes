import numpy as np
from dateutil.parser import parse
import heapq
from statistics import median
from functools import total_ordering
import time

@total_ordering
class Home(object):
	def __init__(self, lat, lng, close, price):
		self.lat = float(lat)
		self.long = float(lng)
		self.close_date = parse(close) # convert to dateutil object for date comparison
		self.close_price = float(price)

	def __str__(self):
		return "lat: {} long: {} close_date: {} close_price: {}".format(self.lat, self.long, self.close_date, self.close_price)

	def __eq__(self, other):
		# homes are equal if they have same lat, lng, close price, close date
		return self.lat == other.lat and self.long == other.long and self.close_date == other.close_date and self.close_price == other.close_price

	def __lt__(self, other):
		return self.close_price < other.close_price

def distance(home1, home2):
	# returns the l2 distance
	return np.sqrt((home1.lat - home2.lat)**2 + (home1.long - home2.long)**2)

def softmax(v):
        """Calculates the softmax function that outputs a vector of values that sum to one.
        Softmax is np.exp(v) / sum(np.exp(v)), but this could present numerical overflow issues if v is very large. 
        We can work around this by adding a constant into the exponent. 
        This is because Ce^t = e^(t + logC)
        """
        v = np.array(v)
        logC = -np.max(v)
        return np.exp(v + logC)/np.sum(np.exp(v + logC), axis = 0)


def weight_homes(target_home, other_homes):
	# assigns weights to homes based on the target homes. 
	# takes the distances from target homes as the weights, but then runs softmax over the resulting vector to normalize to one. 
	# with more data about the homes, we would want to use a similarity_score(home1, home2) function here, instead of only using the l2 distance.
	# For example, if two homes are approximately the same distance to the target home, but also has the same square footage,
	# then it should have a larger weight.
	return softmax([distance(target_home, home) for home in other_homes])

def is_valid_home(current_home, candidate_home):
	# the candidate home must not equal the current home. It also needs to to have a strictly earlier close date. 
	return candidate_home != current_home and candidate_home.close_date < current_home.close_date

def get_max_distance_candidate(current_home, candidate_homes):
	return max(candidate_homes, key = lambda home: distance(current_home, home))

def single_predict(current_home, data, k = 4):
	candidate_homes = []
	for d in data:
		if is_valid_home(current_home, d):
			if len(candidate_homes) < k:
				candidate_homes.append(d)
			else:
				cmax = get_max_distance_candidate(current_home, candidate_homes)
				if distance(current_home, d) < distance(current_home, cmax):
					candidate_homes.remove(cmax)
					candidate_homes.append(d)
	# sanity check: if a home is valid and not in the list of candidate homes, then its distance must be >= the maximum candidate home's distance to the current home.
	for d in data:
		assert not is_valid_home(current_home, d) or d in candidate_homes \
			or distance(d, current_home) >= distance(get_max_distance_candidate(current_home, candidate_homes), current_home), \
			"Sanity check failed, found home with a smaller distance diff that is not in the list."
	# sanity check: the candidate home should not include the current home, and all home close dates should be less than the current home's sold date
	if len(candidate_homes) == 0:
		# case where we picked the home with no prior sales before it - don't have any information to go off of
		return 0
	# note: finding k neighbors may be impossible in case there are < k houses in the dataset that closed before it. 
	# in this case, the price predicted is 0 if it is the single house with no houses sold before it. 
	# otherwise, we use the n nearest neighbors to predict, but we have n < k. 
	for c in candidate_homes:
		assert c != current_home and c.close_date < current_home.close_date, "Error: invalid home in candidate homes"
	# weight the homes according to their distance to the current home
	weights = weight_homes(current_home, candidate_homes)
	# get the price of the current home
	price = sum([weights[i] * candidate_homes[i].close_price for i in range(len(candidate_homes))])
	return price

def mrae(predicted_prices, actual_prices):
	errs = sorted([abs(predicted_prices[i] - actual_prices[i])/actual_prices[i]
		for i in range(len(predicted_prices))])
	return median(errs)

	
if __name__ == '__main__':
	print("reading data")
	with open('data.csv') as f:
		lines = f.readlines()
	print("done reading, now parsing data")
	homes = []
	for line in lines[1:]:
		lat, lng, close, price = line.strip().split(",")
		h = Home(lat, lng, close, price)
		homes.append(h)
	print("creating a subset of 5000 random homes to run predictions on")
	# take a subset of size 5000 random homes
	random_homes = [homes[np.random.randint(0, len(homes))] for _ in range(5000)]
	actual = [h.close_price for h in random_homes]
	preds = []
	for i in range(len(random_homes)):
		if i % 50 == 0:
			print("on prediction {}".format(i))
			t = time.clock()
		preds.append(single_predict(random_homes[i], homes))
		if i % 50 == 0:
			print("prediction took {} seconds".format(time.clock() - t))
	print("done with 5000 predictions!")
	print("Median relative absolute error is {}".format(mrae(preds, actual)))




