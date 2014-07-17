from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from math import log, sqrt
import random
import csv

from sort.models import Ranking, Object

# Create your views here.
def index(request):
    #obs = list(Object.objects.order_by('rank'))
    #r = random.randint(0,len(obs)-2)
    #obs = obs[r:r+2]

    obs = list(Object.objects.order_by('?')[0:2])
    total = len(Ranking.objects.all())

    #objects = list(Object.objects.all())
    #counts = {o:0 for o in objects}
    #for o in objects:
    #    counts[o] += len(Ranking.objects.filter(first=o))
    #    counts[o] += len(Ranking.objects.filter(second=o))
    #
    #obs = [img[2] for img in sorted([(counts[e], random.random(), e) for e
    #                                    in counts])][0:2]

    template = loader.get_template('sort/index.html')
    context = RequestContext(request, {
        'o1': obs[0],
        'o2': obs[1],
        'total' : total,
    })
    return HttpResponse(template.render(context))

def graph(request):
    template = loader.get_template('sort/graph.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def pairwise_raw(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pairwise_raw.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'user', 'first', 'second', 'value'])

    obs = Ranking.objects.all()
    for o in obs:
        writer.writerow([o.id, o.user, o.first.name, o.second.name, o.value])
    
    return response

def export(request):
    compute_ranking()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ranking.csv"'

    writer = csv.writer(response)
    writer.writerow(['name', 'image', 'rank', 'confidence'])

    obs = Object.objects.order_by('-rank')
    for o in obs:
        writer.writerow([o.name, o.image, o.rank, o.confidence])
    
    return response

def compute_ranking():
    for o in Object.objects.all():
        o.rank = random.random() / 10000.0
        o.confidence = 100.0
        o.save()

    last_error = float('inf') 
    diff = float('inf')

    #for i in range(0,5):
    while diff > 0.5:
        print(diff)

        error = 0
        ranks = {}
        confidence = {}

        for o in Object.objects.all():
            opponent_sum = 0.0
            opponent_count = 0.0
            wins = 0.0

            for r in Ranking.objects.filter(first=o):
                opponent_sum = r.second.rank
                opponent_count += 1
                if r.value == 0:
                    wins += 0.5
                elif r.value == 1:
                    wins += 1.0
            for r in Ranking.objects.filter(second=o):
                opponent_sum = r.first.rank
                opponent_count += 1
                if r.value == 0:
                    wins += 0.5
                elif r.value == -1:
                    wins += 1

            if opponent_count > 0:
                opponent_average = opponent_sum / opponent_count
                accuracy = wins / opponent_count

                #handle extremes
                if accuracy == 0:
                    accuracy = 0.0001/1.0001
                elif accuracy == 1:
                    accuracy = 10000.0/10001.0

                #print("prob: %0.4f" % accuracy)

                new_rank = opponent_average + log(accuracy/(1-accuracy))
                #print("rank: %0.4f" % new_rank)

                A = 100.0
                if opponent_count > 1:
                    sum_error = 0.0
                    for oa in Object.objects.all():
                        for r in Ranking.objects.filter(first=oa):
                            if r.value == 0:
                                sum_error += (0.5 - accuracy) * (0.5 - accuracy)
                            elif r.value == 1:
                                sum_error += (1 - accuracy) * (1 - accuracy)
                            else:
                                sum_error += (0 - accuracy) * (0 - accuracy)
                        for r in Ranking.objects.filter(second=oa):
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
                ranks[o.id] = new_rank
                confidence[o.id] = A
            else:
                ranks[o.id] = 0.0
                confidence[o.id] = 100.0

        for o in Object.objects.all():
            o.rank = ranks[o.id]
            o.confidence = confidence[o.id]
            o.save()

        diff = abs(last_error - error)
        last_error = error


def rank(request):
    
    compute_ranking()

    obs = Object.objects.order_by('-rank')

    template = loader.get_template('sort/rank.html')
    context = RequestContext(request, {
        'num_rankings': len(Ranking.objects.all()),
        'objects': obs,
    })
    return HttpResponse(template.render(context))

def vote(request, first, second, value):

    #kConstant = 20

    o1 = Object.objects.get(id__exact=first)
    o2 = Object.objects.get(id__exact=second)

    #o1pt = 0
    #o2pt = 0

    #if value == 0:
    #    o1pt = 0.5
    #    o2pt = 0.5
    #elif value == -1:
    #    o1pt = 0
    #    o2pt = 1
    #else:
    #    o1pt = 1
    #    o2pt = 0

    #o1WinProb = (1.0 / pow(10,((o2.rank - o1.rank)/400)+1))
    #o2WinProb = (1.0 / pow(10,((o1.rank - o2.rank)/400)+1))

    #print(o1WinProb)
    #print(o2WinProb)

    #o1.rank = o1.rank + (kConstant * (o1pt - o1WinProb))
    #o2.rank = o2.rank + (kConstant * (o2pt - o2WinProb))

    #o1.save()
    #o2.save()

    # use this to save the ranking for possible later analysis
    user = request.session.session_key
    if not user:
        user = "Unknown"
    r = Ranking(user=user, first=o1, second=o2, value=value)
    r.save()


    return HttpResponseRedirect(reverse('index'))
