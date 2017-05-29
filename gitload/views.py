#!/usr/bin/env python3
# coding: utf-8

import os, re, shutil, git
from os.path import basename, isdir, splitext

from django.shortcuts import render, redirect
from django.db import IntegrityError

from gitload.browser import Browser
from gitload.models import PLTP, Repository
from gitload.utils import create_breadcrumb

from serverpl.settings import DIRREPO



def index(request):
    """ View for /gitload/ -- template: index.html """
    Repository.add_missing_repository_in_bd()
    repo_list = Repository.objects.all()
    
    error = ""
    error_url = False
    error_name = False
    
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
    })


def browse(request):
    """ View for [...]/gitload/browse -- template: browse.html """
    if (not "browser" in request.session):
        return redirect(index)
    
    browser = Browser(None, dic=request.session["browser"])
    confirmation = ""
    error = ""
    ask_force = False
    force = False
    pltp_path = ""
    
    if (request.method == 'POST'):
        git_path = request.POST.get('git_path', "") #Changing directory
        if (git_path != ""):
            browser.cd(git_path)
        
        pltp_path = request.POST.get('exported', "")
        if (pltp_path != ""): #Loading a PLTP
            repo_object = Repository.objects.get(name=browser.name)
            if (request.POST.get('force', "False") == "True"):
                force = True
            sha1, msg = browser.load_pltp(pltp_path, repo_object, force)
            if (not sha1):
                if (msg):
                    error = msg
                else:
                    ask_force = True
            else:
                lti = PLTP.objects.get(sha1=sha1).url
                confirmation = "http://"+request.get_host()+lti
        
        if (request.POST.get('refresh', False)):
            browser.refresh_repo()
    
    browser.parse_content()
    request.session["browser"] = browser.__dict__
    
    path = browser.current_path[browser.current_path.find(browser.name):]
    rel_path = path[len(browser.name)+1:]
    breadcrumb, breadcrumb_value = create_breadcrumb(path)
    
    return render(request, 'gitload/browse.html', {
        'path': path,
        'rel_path': rel_path,
        'browser': browser,
        'breadcrumb': breadcrumb,
        'breadcrumb_value': breadcrumb_value,
        'error': error,
        'confirmation': confirmation,
        'ask_force': ask_force,
        'exported': pltp_path,
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
