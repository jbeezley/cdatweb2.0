from django.http import HttpResponse
import json
import os
import vtk_launcher
from search import files
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

try:
    from local_settings import base_path
except ImportError:
    base_path = 'tmp/data'
    _browser_help = (
        "Choose a variable from the list of files available on the server "
        "and drag it to the canvas."
        )
def render_template(request, template, context):
    template = loader.get_template(template)
    context = RequestContext(request, context)
    return template.render(context)
       
# *****
# CDATWeb Frontend Pages
# ******
def index(request):
    data = {}
    data['base'] = base_path

    data['files'] = [
        f for f in os.listdir(base_path)
        if not os.path.isdir(os.path.join(base_path, f))
    ]
    data['dirs'] = [
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f))
    ]
    return HttpResponse(render_template(request, "cdatweb/dashboard.html", data))

def user_login(request):
    return HttpResponse(render_template(request, "cdatweb/cdat.html", {}))

def user_logout(request):
    return HttpResponse("logout")

def register(request):
    return HttpResponse("register")

# *****
# CDATWeb Frontend AJAX
# ******
@csrf_exempt 
def esgf_search(request):
    try:
        results = {}
        inputstring = request.POST.get('query')
        context = json.loads(inputstring)

        host = context["host"]
        print host
        query = {}
        if context["text"]:
            query["query"] = context["text"]
        if context["project"]:
            query["project"] = context["project"]
        if context["limit"]:
            query["limit"] = context["limit"]
        if context["offset"]:
            query["offset"] = context["offset"]
        # query['fields'] = 'size,timestamp,project,id,experiment,title,url'

        try:
            results['data'] = files(host, query)
        except Exception, e:
            results['data'] = "failed to reach node"
            print "failed to reach node"
            print e
    except Exception:
        results['data'] = "failed to parse json"
        print "failed to parse json"

    return HttpResponse(json.dumps(results))
    
@csrf_exempt
def get_children(request):
    query = {}
    folder_content = []

    inputstring = request.POST.get('query')
    context = json.loads(inputstring)

    path = context["path"]

    for newpath in os.listdir(path):
        folder_content.append(os.path.join(path, newpath))

    query['files'] = [f for f in folder_content if not os.path.isdir(f)]
    query['dirs'] = [f for f in folder_content if os.path.isdir(f)]
    return HttpResponse(json.dumps(query))    

def get_folder(request):
    return HttpResponse("get folder")

def get_file(request):
    return HttpResponse("get file")

# ******
# VTK
# ******
def _refresh(request):
    """Refresh the visualization session information."""
    # check the session for a vtkweb instance
    vis = request.session.get('vtkweb')
    if vis is None or vtk_launcher.status(vis.get('id', '')) is None:
        # open a visualization instance
        vis = vtk_launcher.new_instance()
        request.session['vtkweb'] = vis
    return dict(vis)

def vtk_viewer(request):
    """Open the main visualizer view."""
    data = {}
    data['base'] = base_path
    data['files'] = [
            f for f in os.listdir(base_path)
            if not os.path.isdir(os.path.join(base_path, f))
            ]
    data['dirs'] = [
            f for f in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, f))
            ]
    return render(
            request,
            'vtk_view/cdat_viewer.html',
            data
            )

def vtk_test(request, test="cone"):
    return render(request, 'vtk_view/view_test.html', {"test": test})

@csrf_exempt  # should probably fix this at some point
def vtkweb_launcher(request):
    """Proxy requests to the configured launcher service."""
    import requests
    VISUALIZATION_LAUNCHER = 'http://aims1.llnl.gov/vtk'
    if getattr(settings, 'VISUALIZATION_LAUNCHER'):
        VISUALIZATION_LAUNCHER = settings.VISUALIZATION_LAUNCHER
    if not VISUALIZATION_LAUNCHER:
        # unconfigured launcher
        return HttpResponse(status=404)
    # TODO: add status and delete methods
    if request.method == 'POST':
        req = requests.post(VISUALIZATION_LAUNCHER, request.body)
        if req.ok:
            return HttpResponse(req.content)
        else:
            return HttpResponse(status=500)
    return HttpResponse(status=404)

