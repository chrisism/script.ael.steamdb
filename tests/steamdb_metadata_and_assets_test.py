#!/usr/bin/python -B
# -*- coding: utf-8 -*-
#
# Test AKL SteamGridDB scraper.
#

# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division
from __future__ import annotations

import os
import unittest
import unittest.mock
from unittest.mock import patch, MagicMock
import logging

logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG)
logger = logging.getLogger(__name__)

from resources.lib.scraper import SteamGridDB
from akl.utils import kodi, io
from akl.api import ROMObj
from akl import constants

from tests.fakes import FakeFile
    
class Test_steamdb_metadata_and_assets(unittest.TestCase):
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_OUTPUT_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
        cls.TEST_OUTPUT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'output/'))
                
        if not os.path.exists(cls.TEST_OUTPUT_DIR):
            os.makedirs(cls.TEST_OUTPUT_DIR)
    
    @unittest.skip('You must have an API key to use this resource')
    @patch('akl.settings.getSettingAsFilePath', autospec=True)
    @patch('resources.lib.scraper.settings.getSetting', autospec=True,return_value= os.getenv('STEAMDB_APIKEY'))
    def test_steamdb_metadata(self, settings_mock, settings_path_mock):     
        settings_path_mock.return_value = io.FileName(self.TEST_OUTPUT_DIR,isdir=True)

        # --- main ---------------------------------------------------------------------------------------
        print('*** Fetching candidate game list ********************************************************')
        # --- Create scraper object ---
        scraper_obj = SteamGridDB()
        scraper_obj.set_verbose_mode(False)
        scraper_obj.set_debug_file_dump(True, self.TEST_OUTPUT_DIR)
        status_dic = kodi.new_status_dic('Scraper test was OK')

        # --- Choose data for testing ---
        search_term, rombase, platform = ('Sniper Elite III', 'Sniper.exe', 'Microsoft Windows')

        subject = ROMObj({
            'id': '1234',
            'scanned_data': {
                'identifier': search_term,
                'file': f'/roms/{rombase}'
            },
            'platform': platform,
            'assets': {key: '' for key in constants.ROM_ASSET_ID_LIST},
            'asset_paths': {
                constants.ASSET_TITLE_ID: '/titles/',
            }
        })

        # --- Get candidates, print them and set first candidate ---
        rom_FN = io.FileName(rombase)
        if scraper_obj.check_candidates_cache(rom_FN.getBase(), platform):
            print('>>>> Game "{}" "{}" in disk cache.'.format(rom_FN.getBase(), platform))
        else:
            print('>>>> Game "{}" "{}" not in disk cache.'.format(rom_FN.getBase(), platform))
            
        candidate_list = scraper_obj.get_candidates(search_term, subject, platform, status_dic)
        # pprint.pprint(candidate_list)
        self.assertTrue(status_dic['status'], 'Status error "{}"'.format(status_dic['msg']))
        self.assertIsNotNone(candidate_list, 'Error/exception in get_candidates()')
        self.assertNotEquals(len(candidate_list), 0, 'No candidates found.')
        
        for candidate in candidate_list:
            print(candidate)
        scraper_obj.set_candidate(rom_FN.getBase(), platform, candidate_list[0])
            
        # --- Print metadata of first candidate ----------------------------------------------------------
        print('*** Fetching game metadata **************************************************************')
        metadata = scraper_obj.get_metadata(status_dic)
        # pprint.pprint(metadata)
        print(metadata)
        scraper_obj.flush_disk_cache()

    @unittest.skip('You must have an API key to use this resource')
    @patch('akl.settings.getSettingAsFilePath', autospec=True)
    @patch('resources.lib.scraper.settings.getSetting', autospec=True, return_value=os.getenv('STEAMDB_APIKEY'))
    def test_steamdb_assets(self, settings_mock, settings_path_mock):                 
        # --- main ---------------------------------------------------------------------------------------
        print('*** Fetching candidate game list ********************************************************')
        settings_path_mock.return_value = io.FileName(self.TEST_OUTPUT_DIR,isdir=True)

        # --- Create scraper object ---
        scraper_obj = SteamGridDB()
        scraper_obj.set_verbose_mode(False)
        scraper_obj.set_debug_file_dump(True, self.TEST_OUTPUT_DIR)
        status_dic = kodi.new_status_dic('Scraper test was OK')

        # --- Choose data for testing ---
        search_term, rombase, platform = ('Sniper Elite III', 'Sniper.exe', 'Microsoft Windows')

        subject = ROMObj({
            'id': '1234',
            'scanned_data': {
                'identifier': search_term,
                'file': f'/roms/{rombase}'
            },
            'platform': platform,
            'assets': {key: '' for key in constants.ROM_ASSET_ID_LIST},
            'asset_paths': {
                constants.ASSET_TITLE_ID: f'{self.TEST_OUTPUT_DIR}/titles/',
            }
        })

        # --- Get candidates, print them and set first candidate ---
        rom_FN = io.FileName(rombase)
        if scraper_obj.check_candidates_cache(rom_FN.getBase(), platform):
            print('>>>> Game "{}" "{}" in disk cache.'.format(rom_FN.getBase(), platform))
        else:
            print('>>>> Game "{}" "{}" not in disk cache.'.format(rom_FN.getBase(), platform))
        candidate_list = scraper_obj.get_candidates(search_term, subject, platform, status_dic)
        # pprint.pprint(candidate_list)
        self.assertTrue(status_dic['status'], 'Status error "{}"'.format(status_dic['msg']))
        self.assertIsNotNone(candidate_list, 'Error/exception in get_candidates()')
        self.assertNotEquals(len(candidate_list), 0, 'No candidates found.')
        
        for candidate in candidate_list:
            print(candidate)
            
        scraper_obj.set_candidate(rom_FN.getBase(), platform, candidate_list[0])

        # --- Print list of assets found -----------------------------------------------------------------
        print('*** Fetching game assets ****************************************************************')
        # --- Get specific assets ---
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_TITLE_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_SNAP_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_BOXFRONT_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_BOXBACK_ID, status_dic))
        self.print_game_assets(scraper_obj.get_assets(constants.ASSET_CARTRIDGE_ID, status_dic))
        scraper_obj.flush_disk_cache()

    def print_game_assets(self, assets):
        for asset in assets:
            print(asset)