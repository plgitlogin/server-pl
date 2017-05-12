# coding: utf-8

import os, re, shutil, git
from os.path import basename, isdir

from django.shortcuts import render, redirect

from gitload.repository import Repository
from gitload.settings import DEFAULT_REPO

from serverpl.settings import MEDIA_ROOT



def index(request):
    """ View for [...]/gitload/ -- template: index.html """
    error = None
    if (request.method == 'POST'):
        repo_url = request.POST.get('repo_url', "")
        if (repo_url != ""):
            repository = Repository(repo_url)
            if (repository.get_repo()):
                request.session["repository"] = repository.__dict__
                return redirect(browse)
            shutil.rmtree(repository.local_root)
            error = "Dépot '" + repository.url + "' introuvable. Merci de vérifier l'adresse ou votre connexion internet."
    
    return render(request, "gitload/index.html", {
        "default_repo": DEFAULT_REPO,
        "error": error,
    })


def browse(request):
    """ View for [...]/gitload/browse -- template: browse.html """
    if (not "repository" in request.session):
        return redirect(index)
    
    dic = request.session["repository"]
    
    repository = Repository("", dic)
        
    if (request.method == 'POST'):
        git_path = request.POST.get('git_path', "")
        if (git_path != ""):
            repository.cd(git_path)
        
        pltp_path = request.POST.get('exported', "")
        if (pltp_path != ""):
            repository.load_pltp(pltp_path)
            return redirect(browse)
    
    repository.refresh_repo()
    repository.parse_content()
    
    #Truncate the path to only keep the path relative to repo.root
    path = repository.local_current_path[repository.local_current_path.find(repository.name):]
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
    
    repo = git.Repo(repository.local_root)
    version = repo.heads.master.commit.name_rev
    
    return render(request, 'gitload/browse.html', {
        'path': path,
        'rel_path': rel_path,
        'repository': repository,
        'breadcrumb': breadcrumb,
        'breadcrumb_value': breadcrumb_value,
        'version': version,
    })


def view_file(request):
    """ View for [...]/gitload/view_file -- template: view_file.html"""
    if (request.method == 'POST'):
        file_path = request.POST.get('file_path', "")
        
        if (file_path != ""):
            readed_file = open(MEDIA_ROOT+file_path, "r")
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
