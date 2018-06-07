"""
Definition of views.
"""
import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext
from datetime import datetime

def home(request):
    """Renders the home page."""
    print('app.views.home')
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def meta(request):
    """print out the meta."""
    now_at = os.getcwd()
    want_go = settings.BASE_DIR
    out = 'now at {}, want go {}<br>'.format(now_at, want_go)
    new_ = os.chdir(want_go)
    out + 'after i am in {}'.format(os.getcwd())
    #values = request.META.items()
    #for i, j in values:
    #    item = '{} : {}<br>'.format(i,j)
    #    out += item
    #out += 'I am meta now folder:'+os.getcwd()
    return HttpResponse(out)
