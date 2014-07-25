from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from algorithm_test.compute_ranking import Item, Rating, maximum_likelihood, elo
import csv

from sort.models import IndividualRanking, Ranking, Object

def individual(request):
    user = request.META.get('REMOTE_ADDR') 
    if not user:
        user = "Unknown"

    rated_ids = [o.obj.id for o in IndividualRanking.objects.filter(user=user)]
    ranking_count = IndividualRanking.objects.filter(user=user).count()
    object_count = Object.objects.all().count()

    if object_count - ranking_count <= 0:
        template = loader.get_template('sort/done.html')
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))

    obj = Object.objects.exclude(id__in=rated_ids).order_by('?')[0]

    template = loader.get_template('sort/individual.html')
    context = RequestContext(request, {
        'object': obj,
        'remaining': object_count - ranking_count,
    })
    return HttpResponse(template.render(context))

def individual_raw(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="individual_raw.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'user', 'object', 'value'])

    obs = IndividualRanking.objects.all()
    for o in obs:
        writer.writerow([o.id, o.user, o.obj.name, o.value])
    
    return response

# Create your views here.
def index(request):
    user = request.META.get('REMOTE_ADDR')
    if not user:
        user = "Unknown"

    obs = list(Object.objects.order_by('?')[0:2])
    total = len(Ranking.objects.filter(user=user))

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
    compute_ml()
    #compute_elo()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ranking.csv"'

    writer = csv.writer(response)
    writer.writerow(['name', 'html', 'estimated_rank', 'standard_error'])

    obs = Object.objects.order_by('-rank')
    for o in obs:
        writer.writerow([o.name, o.image, o.rank, o.confidence/1.96])
    
    return response

def compute_ml():
    mapping = {i: Item(0) for i in Object.objects.all()}
    reverse_mapping = {mapping[i]: i for i in mapping}

    items = [mapping[i] for i in mapping]
    ratings = [Rating(mapping[r.first], mapping[r.second], r.value) for r in
               Ranking.objects.all()]
    maximum_likelihood(items, ratings)
    
    for i in items:
        reverse_mapping[i].rank = i.rank
        reverse_mapping[i].confidence = i.confidence
        reverse_mapping[i].save()

def compute_elo():
    mapping = {i: Item(0) for i in Object.objects.all()}
    reverse_mapping = {mapping[i]: i for i in mapping}

    items = [mapping[i] for i in mapping]
    ratings = [Rating(mapping[r.first], mapping[r.second], r.value) for r in
               Ranking.objects.all()]
    elo(items, ratings)
    
    for i in items:
        reverse_mapping[i].rank = i.rank
        reverse_mapping[i].confidence = i.confidence
        reverse_mapping[i].save()


def rank(request):
    
    #compute_elo()
    compute_ml()

    obs = Object.objects.order_by('-rank')

    template = loader.get_template('sort/rank.html')
    context = RequestContext(request, {
        'num_rankings': len(Ranking.objects.all()),
        'objects': obs,
    })
    return HttpResponse(template.render(context))

def vote(request, first, second, value):

    o1 = Object.objects.get(id__exact=first)
    o2 = Object.objects.get(id__exact=second)

    # use this to save the ranking for possible later analysis
    user = request.META.get('REMOTE_ADDR')
    if not user:
        user = "Unknown"
    if float(value) == 0.5:
        r1 = Ranking(user=user, first=o1, second=o2, value=0)
        r1.save()
        r2 = Ranking(user=user, first=o1, second=o2, value=1)
        r2.save()
    else:
        r = Ranking(user=user, first=o1, second=o2, value=value)
    r.save()

    return HttpResponseRedirect(reverse('index'))

def vote_individual(request, obj_id, value):

    if int(value) < 1 or int(value) > 10:
        return HttpResponseRedirect(reverse('individual'))

    obj = Object.objects.get(id__exact=obj_id)

    # use this to save the ranking for possible later analysis
    user = request.META.get('REMOTE_ADDR')
    if not user:
        user = "Unknown"
    r = IndividualRanking(user=user, obj=obj, value=value)
    r.save()

    return HttpResponseRedirect(reverse('individual'))
