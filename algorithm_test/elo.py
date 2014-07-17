import random
from math import sqrt, log, exp
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

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
    while diff > 0.005:
        #print("Iteration: %i (diff = %0.2f)" % (iteration, diff))

        error = 0
        ranks = {}
        confidence = {}

        for o in items:
            opponent_sum = 0.0
            opponent_count = 0.0
            wins = 0.0

            test_rank = 0

            for r in ratings:
                if r.first == o:
                    opponent_sum = r.second.rank
                    opponent_count += 1
                    if r.value == 0.5:
                        test_rank += r.second.rank + log(r.value / (1-r.value))
                        wins += 0.5
                    elif r.value == 1:
                        wins += 1.0
                        test_rank += r.second.rank + log(0.95 / (1-0.95))
                    else:
                        test_rank += r.second.rank + log(0.05 / (1-0.05))

                elif r.second == o:
                    opponent_sum = r.first.rank
                    opponent_count += 1
                    if r.value == 0.5:
                        test_rank += r.first.rank + log(r.value / (1-r.value))
                        wins += 0.5
                    elif r.value == 0:
                        test_rank += r.first.rank + log(0.95 / (1-0.95))
                        wins += 1
                    else:
                        test_rank += r.first.rank + log(0.05 / (1-0.05))

            if opponent_count > 0:
                opponent_average = opponent_sum / opponent_count
                accuracy = wins / opponent_count

                #handle extremes
                if accuracy == 0:
                    accuracy = 0.05
                    #accuracy = 0.01/1.01
                elif accuracy == 1:
                    #accuracy = 100.0/101.0
                    accuracy = 0.95

                #print("prob: %0.4f" % accuracy)

                # Compute the estimate of the average
                #new_rank = opponent_average + log(accuracy/(1-accuracy))
                #print("new rank:", new_rank)
                #print("test rank:", test_rank/opponent_count)
                #print("rank: %0.4f" % new_rank)

                # compute computer the average over the estimates
                new_rank = test_rank / opponent_count

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
    noise = 0.0

    #print(1.0 / (1.0 + exp(-1.0 * (i1.value - i2.value))))
    if (abs(i1.value - i2.value) <= 0.05):
        if random.random() <= noise:
            return random.choice([0,1])
        return 0.5
    elif random.random() <= 1.0 / (1.0 + exp(-1.0 * (i1.value - i2.value))):
        if random.random() <= noise:
            return random.choice([0.5,0])
        return 1
    else:
        if random.random() <= noise:
            random.choice([0.5,1])
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

def randomly_sample(items, n):
    ratings = []
    for i in range(n):
        sample = [i for i in items]
        random.shuffle(sample)
        i1 = sample[0]
        i2 = sample[1]
        for i in range(3):
            ratings.append(Rating(i1, i2, rank_probabilistic(i1,i2)))
    return ratings

def connected_sample(items, n):
    ratings = []
    counts = {e:0 for e in items}
    pairs = []
    links = {e:[] for e in items}

    for i in range(n):
        sample = [img[2] for img in sorted([(counts[e], random.random(), e) for e
                                            in counts])][0:2]
#        count = 0
#        offset = 0
#        while (sample[0], sample[1]) in pairs:
#            sample = [img[2] for img in sorted([(counts[e], random.random(), e) for e
#                                                in counts])][0:offset+2]
#            count += 1
#
#            if count > 100:
#                offset += 1
#                count = 0


        for i in range(1):
            counts[sample[0]] += 1
            counts[sample[1]] += 1
            pairs.append((sample[0], sample[1]))
            pairs.append((sample[1], sample[0]))
            links[sample[0]].append(sample[1])
            links[sample[1]].append(sample[0])

            ratings.append(Rating(sample[0], sample[1],
                                  rank_probabilistic(sample[0], sample[1])))
        #ratings.append(Rating(sample[0], sample[1],
        #                      rank_deterministic(sample[0], sample[1])))
    return ratings

def online_sample(items, n):
    ratings = []
    counts = {e:0 for e in items}
    pairs = []
    links = {e:[] for e in items}

    for i in range(n):
        compute_ranking(items, ratings)

        sample = [img[2] for img in sorted([(-1 * e.confidence, random.random(), e) for e
                                            in counts])][0:2]
#        count = 0
#        offset = 0
#        while (sample[0], sample[1]) in pairs:
#            sample = [img[2] for img in sorted([(counts[e], random.random(), e) for e
#                                                in counts])][0:offset+2]
#            count += 1
#
#            if count > 100:
#                offset += 1
#                count = 0


        for i in range(3):
            counts[sample[0]] += 1
            counts[sample[1]] += 1
            pairs.append((sample[0], sample[1]))
            pairs.append((sample[1], sample[0]))
            links[sample[0]].append(sample[1])
            links[sample[1]].append(sample[0])

            ratings.append(Rating(sample[0], sample[1],
                                  rank_probabilistic(sample[0], sample[1])))
        #ratings.append(Rating(sample[0], sample[1],
        #                      rank_deterministic(sample[0], sample[1])))
    return ratings

if __name__ == "__main__":
    
    for outer in range(70):
        correlations = []
        for inner in range(30):
            items = [Item(random.normalvariate(0,1)) for i in range(48)]
            #all ratings
            #ratings = [Rating(i1, i2, rank_probabilistic(i1,i2)) for i1 in items for i2 in items if i1 != i2]
            ratings = randomly_sample(items, 10*outer + 1)
            #ratings = randomly_sample(items, 200)
            #ratings = connected_sample(items, 10*outer+1 )
            #ratings = online_sample(items, 250)

            #print("RATINGS")
            #for r in ratings:
            #    print("%s vs. %s => %i" %(r.first.value, r.second.value, r.value))

            #print("ITEMS")
            ##items.sort(key=lambda x: x.value)
            #for i in items:
            #    print("%s: %0.2f (%0.2f)" % (i.value, i.rank, i.confidence))

            #print()
            #print("Estimating rank...")
            compute_ranking(items, ratings)

            #print()
            #print("ITEMS")
            ##items.sort(key=lambda x: x.value)
            #for i in items:
            #    print("%s: %0.2f (%0.2f)" % (i.value, i.rank, i.confidence))

            x = [i.value for i in items]    
            xmean = mean(x)
            xstd = std(x)
            #x = [(v - xmean)/xstd for v in x]
            y = [i.rank for i in items]
            ymean = mean(y)
            ystd = std(y)
            #y = [(v - ymean)/ystd for v in y]

            #for i in range(len(x)):
            #    print("%0.3f\t%0.3f" % (x[i], y[i]))


            #plt.scatter(x,y)

            m,b = np.polyfit(x, y, 1)
            #print(x)
            #print(m*np.array(x) + b)
            plt.clf()
            plt.plot(x, y, '.')
            plt.plot(x, m * np.array(x) + b, '-')

            corr, p = pearsonr(x,y)
            correlations.append(corr)
            #print(corr)
            #print('Correlation Coefficient: %0.3f (p < %0.3f)' %
            #      (corr, p))

        #plt.show()
        print(sum(correlations)/(1.0 * len(correlations)))

