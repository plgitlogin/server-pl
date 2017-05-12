# -*- coding: utf-8 -*-
# Python 3.6
#
#  Author: Coumes Quentin     Mail: qcoumes@etud.u-pem.fr
#  Created: 2017-03-16
#  Last Modified: 2017-03-16

import os, shutil

from django.test import TestCase
from django.shortcuts import get_object_or_404

from gitload.base import Repository, PLTP_Loader
from gitload.models import Loaded_Pltp, Loaded_Pl

from mysite.settings import MEDIA_ROOT




class TestGetRepository(TestCase):
    
    def test_get_repo_pulled(self):
        """ Check if repository has been correctly clone when get_repo() return True. Need an internet connection. """
        repo = Repository("https://github.com/qcoumes/gitload_test.git")
        self.assertTrue(repo.get_repo())
        self.assertTrue(os.path.exists(MEDIA_ROOT+"/gitload_test"))
        if (os.path.exists(MEDIA_ROOT+"/gitload_test")):
            shutil.rmtree(MEDIA_ROOT+"/gitload_test")
    
    def test_get_repo_false(self):
        """ Check if get_repo() correctly return False when the URL is wrong. Need an internet connection. """
        repo = Repository("https://repo.com/fake.git")
        self.assertFalse(repo.get_repo())
        if (os.path.exists(MEDIA_ROOT+"/fake")):
            shutil.rmtree(MEDIA_ROOT+"/fake")



class TestRepository(TestCase):
    
    @classmethod
    def setUpClass(self):
        """ Set a repo for the following test """
        self.repo = Repository("https://github.com/qcoumes/gitload_test.git")
        self.repo.get_repo()
    
    @classmethod
    def tearDownClass(self):
        """ Delete de test repo at the end of the tests """
        if (os.path.exists(MEDIA_ROOT+"/gitload_test")):
            shutil.rmtree(MEDIA_ROOT+"/gitload_test")
    
    def setUp(self):
        """ Set the cursor to the repo root before very test """
        self.repo.cd()
        
        
    def test_cd(self):
        """ Check if cd() correctly change Repository.local_current_path. Need an internet connection. """
        self.repo.cd("PLTP")
        self.assertEqual(self.repo.local_current_path, self.repo.local_root + "/PLTP/")
        self.repo.cd()
        self.assertEqual(self.repo.local_current_path, self.repo.local_root)
            
    def test_parse_content(self):
        """ Check if parse_content() correctly lists every files. Need an internet connection. """
        self.repo.cd("PLTP")
        self.repo.parse_content()
        self.assertEqual(self.repo.local_pltp_list, ["test.pltp"])
        self.assertEqual(self.repo.local_other_list, ["autosubsets.pl"])
        self.assertEqual(self.repo.local_dir_list, ["function"])
        
    def test_load_pltp(self):
        """ Check if load_pltp() correctly create an instance of PLTP_Loader """
        self.assertIsInstance(self.repo.load_pltp("/PLTP/test.pltp"), PLTP_Loader)

class TestPLTPLoader(TestCase):
    
    @classmethod
    def setUpClass(self):
        """ Set a repo for the following test """
        self.repo = Repository("https://github.com/qcoumes/gitload_test.git")
        self.repo.get_repo()
        self.loader = self.repo.load_pltp("/PLTP/test.pltp")
    
    @classmethod
    def tearDownClass(self):
        if (os.path.exists(MEDIA_ROOT+"/pl_test1_"+self.loader.version)):
            shutil.rmtree(MEDIA_ROOT+"/pl_test1_"+self.loader.version)
        if (os.path.exists(MEDIA_ROOT+"/pl_test2_"+self.loader.version)):
            shutil.rmtree(MEDIA_ROOT+"/pl_test2_"+self.loader.version)
    
    def test_load_file(self):
        """ Check if every file are correctly loaded """
        self.assertTrue(os.path.exists(MEDIA_ROOT+"/pl_test1_"+self.loader.version))
        self.assertTrue(os.path.exists(MEDIA_ROOT+"/pl_test2_"+self.loader.version))
    
    def test_load_data_base(self):
        """ Check if every information are present in the data base after loading """
        pltp = get_object_or_404(Loaded_Pltp, name="test")
        pl = pltp.loaded_pl_set.all()
        
        self.assertEqual(pltp.name, "test")
        #test json
        
        self.assertEqual(len(pl), 2)
        
        self.assertEqual(pl[0].name, "test1")
        #test dirname + json
        self.assertEqual(pl[1].name, "test2")
        #test dirname + json
    
    
    
