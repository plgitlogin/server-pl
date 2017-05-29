#!/usr/bin/env python3
# coding: utf-8

import os, re, shutil, git
from os.path import basename, isdir, splitext

from django.shortcuts import render, redirect
from django.db import IntegrityError

from gitload.browser import Browser
from gitload.models import PLTP, Repository

from serverpl.settings import DIRREPO



def index(request):
    """ View for /gitload/ -- template: index.html """
    repo_list = Repository.objects.all()
    
    error = ""
    error_url = False
    error_name = False
    warning_repo = Repository.missing_repository_in_bd()
    
    if (request.method == 'POST'):
        repo_url = request.POST.get('repo_url', "")
        repo_name = request.POST.get('repo_name', "")
            
        if (repo_url != ""): #If new repository
            try:
                repo, created = Repository.objects.get_or_create(name=repo_name, url=repo_url)
                browser = Browser(repo)
                if (not browser.get_repo()):
                    shutil.rmtree(browser.root)
                    error_url = True
                    error = "Dépot '" + browser.url + "' introuvable. Merci de vérifier l'adresse ou votre connexion internet."
                    repo.delete()
            except IntegrityError:
                error_name = True
                error = "Le nom "+repo_name+" est déjà utilisé, merci d'en choisir un autre."
                
        elif (repo_name != ""): #If default
            repo = Repository.objects.get(name=repo_name)
            browser = Browser(repo)
        
        if (repo_name != "" and error == ""): #If None or error
            request.session["browser"] = browser.__dict__
            return redirect(browse)
    
    return render(request, "gitload/index.html", {
        "default": repo_list,
        "error": error,
        "error_name": error_name,
        "error_url": error_url,
        "warning_repo": warning_repo,
    })


def browse(request):
    """ View for [...]/gitload/browse -- template: browse.html """
    if (not "browser" in request.session):
        return redirect(index)
    
    browser = Browser(None, dic=request.session["browser"])
    confirmation = ""
    error = ""
    
    if (request.method == 'POST'):
        git_path = request.POST.get('git_path', "")
        if (git_path != ""):
            browser.cd(git_path)
        
        pltp_path = request.POST.get('exported', "")
        if (pltp_path != ""):
            repo_object = Repository.objects.get(name=browser.name)
            loaded, msg = browser.load_pltp(pltp_path, repo_object)
            if (not loaded):
                error = msg
            else:
                lti = PLTP.objects.get(rel_path=pltp_path).url
                confirmation = "http://"+request.get_host()+lti
        
        if (request.POST.get('refresh', False)):
            browser.refresh_repo()
    
    browser.parse_content()
    
    ####Creating breadcrumb####
    path = browser.current_path[browser.current_path.find(browser.name):]
    rel_path = path[len(browser.name)+1:]
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
        'browser': browser,
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

def edit_file(request):
    """ View for [...]/gitload/edit_file -- template: edit_file.html"""
    if (request.method == 'POST'):
        file_path = request.POST.get('file_path', "")
        
        if (file_path != ""):
            with open(DIRREPO+file_path, "r") as f:
                content  = f.read()
            
            request.current_app = 'gitload' # Interet ?
            return render(request,  'gitload/edit_file.html', {
                'filecontent': content,
                'filename': basename(file_path),
            })
    
    return redirect(browse)

def save_file(request):
    """ View for [...]/gitload/edit_file -- template: edit_file.html"""
    if (request.method == 'POST'):
        file_path = request.POST.get('file_path', "")
        
        print("saving ",file_path)
    
    return redirect(browse)





def loaded_pltp(request):
    """ View for [...]/gitload/loaded_pltp -- template: loaded_pltp.html"""
    pltp = PLTP.objects.all();
    
    return render(request, 'gitload/loaded_pltp.html', {
        'pltp': pltp,
        'domain': "http://"+request.get_host(),
    })
