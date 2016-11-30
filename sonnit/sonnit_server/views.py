from django.shortcuts import render

def index(request):
	return render(request, 'sonnit_server/index.html')
# Create your views here.
