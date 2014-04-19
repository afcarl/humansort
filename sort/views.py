from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from math import pow, log
import random

from sort.models import Ranking, Object

# Create your views here.
def index(request):
    #obs = list(Object.objects.order_by('rank'))
    #r = random.randint(0,len(obs)-2)
    #obs = obs[r:r+2]

    obs = list(Object.objects.order_by('?')[0:2])

    template = loader.get_template('sort/index.html')
    context = RequestContext(request, {
        'o1': obs[0],
        'o2': obs[1],
    })
    return HttpResponse(template.render(context))

def rank(request):
    print("# rankings: %i" % len(Ranking.objects.all()))
    
    for o in Object.objects.all():
        o.rank = random.random()
        o.save()

    last_error = float('inf') 
    diff = 100

    #for i in range(0,5):
    while diff > 0.5:
        print(diff)

        error = 0
        ranks = {}

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
                if accuracy == 0 or not accuracy:
                    accuracy = 0.1
                elif accuracy == 1:
                    accuracy = 0.9

                #print("prob: %0.4f" % accuracy)

                new_rank = opponent_average + log(accuracy/(1-accuracy))
                #print("rank: %0.4f" % new_rank)

                error += abs(o.rank - new_rank)
                ranks[o.id] = new_rank
            else:
                error += abs(o.rank - 0.0)
                ranks[o.id] = 0.0

        for o in Object.objects.all():
            o.rank = ranks[o.id]
            o.save()

        diff = abs(last_error - error)
        last_error = error

    obs = Object.objects.order_by('rank')

    template = loader.get_template('sort/rank.html')
    context = RequestContext(request, {
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
