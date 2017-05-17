# coding: utf-8

import os, re, shutil, git
from os.path import basename, isdir, splitext

from django.shortcuts import render, redirect

from gitload.repository import Repository
from gitload.models import Loaded_Pltp

from serverpl.settings import DIRREPO



def index(request):
    """ View for /gitload/ -- template: index.html """
    repo = list()
    for (path, subdirs, files) in os.walk(DIRREPO):    
        for filename in subdirs:
            repo.append(filename)
        break
    
    error = ""
    
    if (request.method == 'POST'):
        repo_url = request.POST.get('repo_url', "")
        repo_name = request.POST.get('repo_name', "")
        
        if (repo_name != ""):
            repository = Repository(repo_name)
            
        if (repo_url != ""):
            repository = Repository(splitext(basename(repo_url))[0], url=repo_url)
            if (not repository.get_repo()):
                shutil.rmtree(repository.root)
                error = "Dépot '" + repository.url + "' introuvable. Merci de vérifier l'adresse ou votre connexion internet."
        
        if ((repo_name != "" or repo_url != "") and error == ""):
            request.session["repository"] = repository.__dict__
            return redirect(browse)
    
    return render(request, "gitload/index.html", {
        "default_repo": repo,
        "error": error,
    })


def browse(request):
    """ View for [...]/gitload/browse -- template: browse.html """
    if (not "repository" in request.session):
        return redirect(index)
    
    repository = Repository(None, dic=request.session["repository"])
    confirmation = ""
    error = ""
    
    if (request.method == 'POST'):
        git_path = request.POST.get('git_path', "")
        if (git_path != ""):
            repository.cd(git_path)
        
        pltp_path = request.POST.get('exported', "")
        if (pltp_path != ""):
            confirmation = repository.load_pltp(pltp_path)
            if (confirmation != ""):
                confirmation = "http://"+request.get_host()+confirmation
            else:
                error = "Erreur lors du chargement de " + pltp_path
        
        if (request.POST.get('refresh', False)):
            repository.refresh_repo()
    
    repository.parse_content()
    
    ####Creating breadcrumb####
    path = repository.current_path[repository.current_path.find(repository.name):]
    rel_path = path[len(repository.name)+1:]
    if (path[-1] != '/'):
        path += '/'
    breadcrumb = path.split('/')[:-1];
    breadcrumb_value = list()
    for i in range(0, len(breadcrumb)):
        if (i == 0):
            breadcrumb_value.append("/")
        else:
            breadcrumb_value.append("")
        for j in range(1, i+1):
            breadcrumb_value[i] += ('/' + breadcrumb[j])
            if (breadcrumb_value[i][0] == '/' and len(breadcrumb_value[i]) > 1):
                breadcrumb_value[i] = breadcrumb_value[i][1:]
    
    return render(request, 'gitload/browse.html', {
        'path': path,
        'rel_path': rel_path,
        'repository': repository,
        'breadcrumb': breadcrumb,
        'breadcrumb_value': breadcrumb_value,
        'error': error,
        'confirmation': confirmation,
    })


def view_file(request):
    """ View for [...]/gitload/view_file -- template: view_file.html"""
    if (request.method == 'POST'):
        file_path = request.POST.get('file_path', "")
        
        if (file_path != ""):
            readed_file = open(DIRREPO+file_path, "r")
            lines = list()
            for line in readed_file:
                lines.append(line)
            readed_file.close()
            
            request.current_app = 'gitload'
            return render(request,  'gitload/view_file.html', {
                'lines': lines,
                'filename': basename(file_path),
            })
    
    return redirect(browse)

def loaded_pltp(request):
    """ View for [...]/gitload/loaded_pltp -- template: loaded_pltp.html"""
    pltp = Loaded_Pltp.objects.all();
    
    return render(request, 'gitload/loaded_pltp.html', {
        'pltp': pltp,
        'domain': "http://"+request.get_host(),
    })
