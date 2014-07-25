import random
from math import sqrt, log, exp, pi
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

class Item:

    def __init__(self, value):
        self.true_value = value
        self.reset()

    def reset(self):
        self.rank = random.random()/10000.0
        self.confidence = 100

class Rating:

    def __init__(self, item1, item2, rating):
        self.first = item1
        self.second = item2
        self.value = rating

def item_information(i1, i2):
    return probability(i1, i2, 0) * probability(i1, i2, 1)

def test_information(i1, ratings):
    information = 0.0

    for r in ratings:
        if r.first == i1:
            information += item_information(i1, r.second)
        elif r.second == i1:
            information += item_information(i1, r.first)

    return information

def standard_error_in_measurement(i1, ratings):
    if test_information(i1, ratings) == 0:
        return 100.0

    return sqrt(1.0 / test_information(i1, ratings))

def probability(i1, i2, value):
    """
    The probability of a particular outcome for i1 vs. i2. 
    
    Value = 0 if i1 < i2. 
    Value = 1 if i1 > i2. 
    """
    if value == 0:
        return exp(i2.rank) / (exp(i1.rank) + exp(i2.rank))
    elif value == 1:
        return exp(i1.rank) / (exp(i1.rank) + exp(i2.rank))
    else:
        # This would be a tie situation, print an error for now
        print("ERROR: TIES NOT SUPPORTED!")

def log_likelihood(ratings):
    log_likelihood = 0

    for r in ratings:
        log_likelihood += log(probability(r.first, r.second, r.value))

    return log_likelihood

def plot_pdf(item, ratings):
    x = [(-3.0 + v * 0.01) for v in range(0, 600)]
    y = [pdf(v, item, ratings) for v in x]

    plt.scatter(x,y, color="black")
    plt.plot([item.rank], [pdf(item.rank, item, ratings)], 'ro')
    plt.plot([item.true_value], [pdf(item.true_value, item, ratings)], 'bo')
    plt.show()

def normal_pdf(x, u, sigma):
    return (1.0 / (sigma * sqrt(2 * pi)) * 
            exp((-1 * (x - u) * (x - u)) / (2 * sigma * sigma)))

def pdf(x, item, ratings):
    value = 0.0

    for r in ratings:
        if r.first == item:
            if r.value == 0:
                value += (log(exp(r.second.rank) / (exp(x) +
                                                   exp(r.second.rank))))
            elif r.value == 1:
                value += (log(exp(x) / (exp(x) + exp(r.second.rank))))
            else:
                print("ERROR TIES NOT SUPPORTED!")

        elif r.second == item:
            if r.value == 0:
                value += (log(exp(x) / (exp(x) + exp(r.first.rank))))
            elif r.value == 1:
                value += (log(exp(r.first.rank) / (exp(x) +
                                                   exp(r.first.rank))))
            else:
                print("ERROR TIES NOT SUPPORTED!")

    return value

def pdf_first_derivative(rank_est, item, ratings):
    value = 0.0
    for r in ratings:
        if r.first == item:
            if r.value == 0:
                value += -1 * exp(rank_est) / (exp(rank_est) +
                                               exp(r.second.rank))
            elif r.value == 1:
                value += exp(r.second.rank) / (exp(rank_est) +
                                               exp(r.second.rank))
            else:
                print("ERROR TIES NOT SUPPORTED!")

        elif r.second == item:
            if r.value == 0:
                value += exp(r.first.rank) / (exp(rank_est) +
                                               exp(r.first.rank))
            elif r.value == 1:
                value += -1 * exp(rank_est) / (exp(rank_est) +
                                               exp(r.first.rank))
            else:
                print("ERROR TIES NOT SUPPORTED!")

    return value

def pdf_second_derivative(rank_est, item, ratings):
    value = 0.0
    
    for r in ratings:
        if r.first == item:
            value += ((-1 * exp(rank_est + r.second.rank)) / 
                      ((exp(rank_est) + exp(r.second.rank)) *
                       (exp(rank_est) + exp(r.second.rank))))
        if r.second == item:
            value += ((-1 * exp(rank_est + r.first.rank)) / 
                      ((exp(rank_est) + exp(r.first.rank)) *
                       (exp(rank_est) + exp(r.first.rank))))

    return value

def estimate_rank(item, ratings):
    """
    Estimate the rank using the Newton-Raphson method.
    """
    rank_est = item.rank
    prior = float('inf')

    while(abs(rank_est - prior) > 0.0001):
        prior = rank_est
        fd = pdf_first_derivative(rank_est, item, ratings)
        sd = pdf_second_derivative(rank_est, item, ratings)
        if sd == 0:
            print("SECOND MOMENT == 0???!")
            rank_est = rank_est
        else:
            rank_est = rank_est - (fd / sd)
        
        # bound the rank to the range [-3, 3]
        if rank_est < -3.0:
            rank_est = -3.0
        elif rank_est > 3.0:
            rank_est = 3.0

    return rank_est

def maximum_likelihood(items, ratings):
    next_estimates = {i: 0.0 for i in items}

    prior = log_likelihood(ratings)
    error = 1.0
    print("Initial log-likelihood: %0.3f" % prior)

    # initialize the ranks to be close to 0
    for i in items:
        i.reset()

    # perform 20 iterations
    while(error > 0.0001):
        # estimate better ranks
        for i in items:
            next_estimates[i] = estimate_rank(i, ratings)

        # update ranks
        for i in items:
            i.rank = next_estimates[i]

        new = log_likelihood(ratings)
        error = abs(new - prior)
        prior = new
        print("Log-likelihood at Iteration: %0.3f" % new)

    for i in items:
        i.confidence = 1.96 * standard_error_in_measurement(i, ratings)

def elo(items, ratings):

    for o in items:
        o.reset()

    last_error = float('inf') 
    diff = float('inf')

    iteration = 1
    while diff > 0.000005:
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
    if random.random() <= exp(i1.true_value) / (exp(i1.true_value) +
                                                exp(i2.true_value)):
        return 1
    else:
        return 0

def rank_deterministic(i1, i2):
    if i1.true_value >= i2.true_value:
        return 1 
    else:
        return 0

def randomly_sample(items, n):
    ratings = []
    for i in range(n):
        sample = [i for i in items]
        random.shuffle(sample)
        i1 = sample[0]
        i2 = sample[1]
        ratings.append(Rating(i1, i2, rank_probabilistic(i1,i2)))
        #ratings.append(Rating(i1, i2, rank_deterministic(i1,i2)))
    return ratings

def mean(values):
    return sum(values) / len(values)

def std(values):
    m = mean(values)
    variance = (float(sum([(v - m) * (v - m) for v in values])) /
                (len(values) - 1.0))

    return sqrt(variance)

if __name__ == "__main__":
    
    random.seed(1)
    values = [random.normalvariate(0,1) for i in range(48)]
    std_values = [(v - mean(values))/std(values) for v in values]
    items = [Item(v) for v in values]

    random.seed()

    ratings = randomly_sample(items, 750)
    maximum_likelihood(items, ratings)

    #elo(items, ratings)
    #print(log_likelihood(ratings))

    #for i in items:
    #    plot_pdf(i, ratings)
    
    x = [i.true_value for i in items]    
    y = [i.rank for i in items]    

    print(pearsonr(x,y))
    print(spearmanr(x,y))
    plt.scatter(x,y)

    for i in items:
        plt.plot([i.true_value, i.true_value], [i.rank + i.confidence, i.rank -
                                               i.confidence])

    plt.show()
    
    

