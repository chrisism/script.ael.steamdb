﻿# -*- coding: utf-8 -*-
#
# SteamGrid DB Scraper for AEL
#
# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division

import sys
import argparse
import logging
import json
    
# --- Kodi stuff ---
import xbmcaddon

# AEL main imports
from ael import constants
from ael.utils import kodilogging, io, kodi
from ael.scrapers import ScraperSettings, ScrapeStrategy

# Local modules
from resources.lib.scraper import SteamGridDB

kodilogging.config() 
logger = logging.getLogger(__name__)

# --- Addon object (used to access settings) ---
addon           = xbmcaddon.Addon()
addon_id        = addon.getAddonInfo('id')
addon_version   = addon.getAddonInfo('version')

# ---------------------------------------------------------------------------------------------
# This is the plugin entry point.
# ---------------------------------------------------------------------------------------------
def run_plugin():
    # --- Some debug stuff for development ---
    logger.info('------------ Called Advanced Emulator Launcher Plugin: SteamGrid DB Scraper ------------')
    logger.info('addon.id         "{}"'.format(addon_id))
    logger.info('addon.version    "{}"'.format(addon_version))
    logger.info('sys.platform     "{}"'.format(sys.platform))
    if io.is_android(): logger.info('OS               "Android"')
    if io.is_windows(): logger.info('OS               "Windows"')
    if io.is_osx():     logger.info('OS               "OSX"')
    if io.is_linux():   logger.info('OS               "Linux"')
    for i in range(len(sys.argv)): logger.info('sys.argv[{}] "{}"'.format(i, sys.argv[i]))
    
    parser = argparse.ArgumentParser(prog='script.ael.steamdb')
    parser.add_argument('--cmd', help="Command to execute", choices=['launch', 'scan', 'scrape', 'configure'])
    parser.add_argument('--type',help="Plugin type", choices=['LAUNCHER', 'SCANNER', 'SCRAPER'], default=constants.AddonType.LAUNCHER.name)
    parser.add_argument('--server_host', type=str, help="Host")
    parser.add_argument('--server_port', type=int, help="Port")
    parser.add_argument('--rom_id', type=str, help="ROM ID")
    parser.add_argument('--romcollection_id', type=str, help="ROM Collection ID")
    parser.add_argument('--ael_addon_id', type=str, help="Addon configuration ID")
    parser.add_argument('--settings', type=json.loads, help="Specific run setting")
    
    try:
        args = parser.parse_args()
    except Exception as ex:
        logger.error('Exception in plugin', exc_info=ex)
        kodi.dialog_OK(text=parser.usage)
        return
        
    if args.type == constants.AddonType.SCRAPER.name and args.cmd == 'scrape': run_scraper(args)
    else:
        kodi.dialog_OK(text=parser.format_help())
        
    logger.debug('Advanced Emulator Launcher Plugin: SteamGrid DB Scraper -> exit')

# ---------------------------------------------------------------------------------------------
# Scraper methods.
# ---------------------------------------------------------------------------------------------
def run_scraper(args):
    logger.debug('========== run_scraper() BEGIN ==================================================')
    pdialog             = kodi.ProgressDialog()
    
    settings            = ScraperSettings.from_settings_dict(args.settings)
    scraper_strategy    = ScrapeStrategy(
                            args.server_host, 
                            args.server_port, 
                            settings, 
                            SteamGridDB(), 
                            pdialog)
                        
    if args.rom_id is not None:
        scraped_rom = scraper_strategy.process_single_rom(args.rom_id)
        pdialog.endProgress()
        pdialog.startProgress('Saving ROM in database ...')
        scraper_strategy.store_scraped_rom(args.ael_addon_id, args.rom_id, scraped_rom)
        pdialog.endProgress()
        
    if args.romcollection_id is not None:
        scraped_roms = scraper_strategy.process_collection(args.romcollection_id)
        pdialog.endProgress()
        pdialog.startProgress('Saving ROMs in database ...')
        scraper_strategy.store_scraped_roms(args.ael_addon_id, args.romcollection_id, scraped_roms)
        pdialog.endProgress()

# ---------------------------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------------------------
try:
    run_plugin()
except Exception as ex:
    logger.fatal('Exception in plugin', exc_info=ex)
    kodi.notify_error("General failure")
    