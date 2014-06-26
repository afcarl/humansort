import random
from math import sqrt, log, exp
import matplotlib.pyplot as plt

class Item:

    def __init__(self, value):
        self.value = value
        self.reset()

    def reset(self):
        self.rank = random.random()/10000.0
        self.confidence = 100

class Rating:

    def __init__(self, item1, item2, rating):
        self.first = item1
        self.second = item2
        self.value = rating

def compute_ranking(items, ratings):
    for o in items:
        o.reset()

    last_error = float('inf') 
    diff = float('inf')

    iteration = 1
    while diff > 0.5:
        print("Iteration: %i (diff = %0.2f)" % (iteration, diff))

        error = 0
        ranks = {}
        confidence = {}

        for o in items:
            opponent_sum = 0.0
            opponent_count = 0.0
            wins = 0.0

            for r in ratings:
                if r.first == o:
                    opponent_sum = r.second.rank
                    opponent_count += 1
                    if r.value == 0.5:
                        wins += 0.5
                    elif r.value == 1:
                        wins += 1.0

                elif r.second == o:
                    opponent_sum = r.first.rank
                    opponent_count += 1
                    if r.value == 0.5:
                        wins += 0.5
                    elif r.value == 0:
                        wins += 1

            if opponent_count > 0:
                opponent_average = opponent_sum / opponent_count
                accuracy = wins / opponent_count

                #handle extremes
                if accuracy == 0:
                    accuracy = 0.01/1.01
                elif accuracy == 1:
                    accuracy = 100.0/101.0

                #print("prob: %0.4f" % accuracy)

                new_rank = opponent_average + log(accuracy/(1-accuracy))
                #print("rank: %0.4f" % new_rank)

                A = 100.0
                if opponent_count > 1:
                    sum_error = 0.0
                    for oa in items:
                        for r in ratings:
                            if r.first == oa:
                                if r.value == 0:
                                    sum_error += (0.5 - accuracy) * (0.5 - accuracy)
                                elif r.value == 1:
                                    sum_error += (1 - accuracy) * (1 - accuracy)
                                else:
                                    sum_error += (0 - accuracy) * (0 - accuracy)
                            elif r.second == oa:
                                if r.value == 0:
                                    sum_error += (0.5 - accuracy) * (0.5 - accuracy)
                                elif r.value == -1:
                                    wins += 1
                                    sum_error += (1 - accuracy) * (1 - accuracy)
                                else:
                                    sum_error += (0 - accuracy) * (0 - accuracy)
                    s = sqrt((1 / (opponent_count - 1)) * sum_error)
                    A = 1.96 * (s / sqrt(opponent_count))

                error += abs(o.rank - new_rank)
                ranks[o] = new_rank
                confidence[o] = A
            else:
                ranks[o] = 0.0
                confidence[o] = 100.0

        for o in items:
            o.rank = ranks[o]
            o.confidence = confidence[o]

        diff = abs(last_error - error)
        last_error = error
        iteration += 1

def rank_probabilistic(i1, i2):
    #print(1.0 / (1.0 + exp(-1.0 * (i1.value - i2.value))))
    if (abs(i1.value - i2.value) <= 0.05):
        return 0.5
    elif random.random() <= 1.0 / (1.0 + exp(-1.0 * (i1.value - i2.value))):
        return 1
    else:
        return 0

def rank_deterministic(i1, i2):
    if i1.value < i2.value:
        return 0 
    elif i1.value == i2.value:
        return 0.5
    else:
        return 1

def rmse(items):
    pass

def mean(values):
    return sum(values) / len(values)

def std(values):
    m = mean(values)
    variance = (float(sum([(v - m) * (v - m) for v in values])) /
                (len(values) - 1.0))

    return sqrt(variance)

if __name__ == "__main__":
    items = [Item(random.normalvariate(0,1)) for i in range(10)]
    #all ratings
    #ratings = [Rating(i1, i2, rank_probabilistic(i1,i2)) for i1 in items for i2 in items if i1 != i2]
    ratings = []
    for i in range(40):
        i1 = random.choice(items)
        i2 = random.choice(items)
        ratings.append(Rating(i1, i2, rank_probabilistic(i1,i2)))

    #print("RATINGS")
    #for r in ratings:
    #    print("%s vs. %s => %i" %(r.first.value, r.second.value, r.value))

    print("ITEMS")
    #items.sort(key=lambda x: x.value)
    for i in items:
        print("%s: %0.2f (%0.2f)" % (i.value, i.rank, i.confidence))

    print()
    print("Estimating rank...")
    compute_ranking(items, ratings)

    print()
    print("ITEMS")
    #items.sort(key=lambda x: x.value)
    for i in items:
        print("%s: %0.2f (%0.2f)" % (i.value, i.rank, i.confidence))

    x = [i.value for i in items]    
    xmean = mean(x)
    xstd = std(x)
    x = [(v - xmean)/xstd for v in x]
    y = [i.rank for i in items]
    ymean = mean(y)
    ystd = std(y)
    y = [(v - ymean)/ystd for v in y]

    for i in range(len(x)):
        print("%0.3f\t%0.3f" % (x[i], y[i]))

    plt.scatter(x,y)

    plt.show()

