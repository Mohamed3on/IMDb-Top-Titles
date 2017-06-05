import time as time
from django.shortcuts import render
from .models import Title

def index(request):
    timebefore=time.time()
    highest_scores=Title.objects.order_by('score').reverse()[:100]
    times=(time.time()-timebefore)
    context = {
        'highest_scores': highest_scores,
    }
    return render(request, 'imdb/index.html', context)
