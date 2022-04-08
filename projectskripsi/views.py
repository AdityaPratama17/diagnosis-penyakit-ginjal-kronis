from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

def index(request):

    context ={
        'movie_top' : 1,
    }
    return render(request, 'index.html', context)