from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from math import pow

from sort.models import Ranking, Object

# Create your views here.
def index(request):
    obs = list(Object.objects.order_by('?')[0:2])

    template = loader.get_template('sort/index.html')
    context = RequestContext(request, {
        'o1': obs[0],
        'o2': obs[1],
    })
    return HttpResponse(template.render(context))

def rank(request):
    obs = Object.objects.order_by('rank')

    template = loader.get_template('sort/rank.html')
    context = RequestContext(request, {
        'objects': obs,
    })
    return HttpResponse(template.render(context))

def vote(request, first, second, value):
    kConstant = 20

    o1 = Object.objects.get(id__exact=first)
    o2 = Object.objects.get(id__exact=second)

    o1pt = 0
    o2pt = 0

    if value == 0:
        o1pt = 0.5
        o2pt = 0.5
    elif value == -1:
        o1pt = 0
        o2pt = 1
    else:
        o1pt = 1
        o2pt = 0

    o1WinProb = (1.0 / pow(10,((o2.rank - o1.rank)/400)+1))
    o2WinProb = (1.0 / pow(10,((o1.rank - o2.rank)/400)+1))

    o1.rank = o1.rank + (kConstant * (o1pt - o1WinProb))
    o2.rank = o2.rank + (kConstant * (o2pt - o2WinProb))

    o1.save()
    o2.save()

    # use this to save the ranking for possible later analysis
    user = request.session.session_key
    r = Ranking(user=user, first=o1, second=o2, value=value)
    r.save()


    return HttpResponseRedirect(reverse('index'))
