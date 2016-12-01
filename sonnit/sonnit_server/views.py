from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from sonnit_server.models import *


# TODO: DELTE THIS STUFF LATER
import datetime

def index(request):
    return render(request, 'sonnit_server/index.html')

def new_sonnet(request):
    if request.method == "POST":
        # TODO: Actually generate a sonnet
        sonnet = Sonnet.objects.create(text="ASDF" + str(datetime.datetime.now()))
    else:
        sonnet = None
    return render(request, 'sonnit_server/new_sonnet.html', {'sonnet': sonnet})

def number(request, sonnet_number):
    if Sonnet.objects.filter(id=sonnet_number).count() > 0:
        sonnet = Sonnet.objects.get(id=sonnet_number)
    else:
        sonnet = None
    return render(request, 'sonnit_server/number.html', {'sonnet': sonnet})

def list_sonnets(request, order=None):
    sonnets = Sonnet.objects.all()
    if order is None or order == "oldest":
        # This is the default of how they come
        pass
    elif order == "newest":
        sonnets = reversed(sonnets)
    elif order == "best":
        sonnets = sorted(sonnets, key=lambda x: x.score, reverse=True)
    elif order == "worst":
        sonnets = sorted(sonnets, key=lambda x: x.score)
    return render(request, 'sonnit_server/list_sonnets.html', {'sonnets': sonnets})

def rate(request, sonnet_id, vote):
    if Sonnet.objects.filter(id=sonnet_id).count() == 0:
        # Return an error 
        return HttpResponseBadRequest("400: No sonnet found")
    else:
        sonnet = Sonnet.objects.get(id=sonnet_id)
    # Get the IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    vote = int(vote)
    if Score.objects.filter(ip=ip, sonnet=sonnet).count() > 0:
        score = Score.objects.get(ip=ip, sonnet=sonnet)
        if vote==0:
            if score.value == 0:
                diff = 0
            else:
                diff = -2
            score.value = 0
        else:
            if score.value == 0:
                diff = 2
            else:
                diff = 0
            score.value = 1
        score.save()
    else:
        if vote == 0:
            diff = -1
            score = Score.objects.create(sonnet=sonnet, ip=ip, value=0)
        else:
            diff = 1
            score = Score.objects.create(sonnet=sonnet, ip=ip, value=1)
    return HttpResponse(diff)
