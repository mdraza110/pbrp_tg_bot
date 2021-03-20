import subprocess
import html
import json
import random
import time
import pyowm
import os
from pyowm import timeutils, exceptions
from datetime import datetime
from typing import Optional, List
from pythonping import ping as ping3
from typing import Optional, List
from hurry.filesize import size

from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from tg_bot.modules.helper_funcs.chat_status import is_user_admin, bot_admin, user_admin_no_reply, user_admin
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER, LOGGER
from tg_bot.__main__ import STATS, USER_INFO
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.helper_funcs.filters import CustomFilters

from requests import get, post

# DO NOT DELETE THIS, PLEASE.
# Made by @manjotsidhu on GitHub and Telegram.
#
# This module helps PBRP Admins to trigger and release their builds using CI/CD

LOGGER.info("PBRP Module by @manjotsidhu for PitchBlack Recovery Project")

org_slug = "PitchBlackRecoveryProject"

# Builds up Project Slug for Device Tree
def project_slug_device_tree(vendor, codename):
	return f'{org_slug}/android_device_{vendor}_{codename}-pbrp'

# Circle CI Request Header format
def circleci_request_headers():
	return {
		'Content-Type': 'application/json',
		'Accept': 'application/json',
		'Circle-Token': os.environ.get("CIRCLE_TOKEN", None)
	}

# GH Request Header format
def ghci_headers():
	return {'Authorization': 'token ' + os.environ.get("GH_TOKEN", "")}

@user_admin
@run_async
def circleci(bot: Bot, update: Update, args: List[str]):

	message = update.effective_message
	reply_text = ""
	
	if len(args) < 2:
		update.effective_message.reply_text("Please specify correct parameters. /circleci [vendor] [codename] [branch] (Optional)")
		return
		
	project_slug = "gh/" + project_slug_device_tree(args[0], args[1])
	
	if len(args) > 2:
		fetch = post(f'https://circleci.com/api/v2/project/{project_slug}/pipeline', json={"branch":args[2]}, headers = circleci_request_headers())
	else:
		fetch = post(f'https://circleci.com/api/v2/project/{project_slug}/pipeline', json={}, headers = circleci_request_headers())
		
		
	if fetch.status_code == 201:
		reply_text = f'Successfully triggered Circle CI pipeline for {args[0]}/{args[1]}. Good Luck with that!'
	else:
		reply_text = f'There is some error making request to Circle CI. Tagging @manjotsidhu. Here are the logs: ```\n{fetch.json()}```'

	message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@user_admin
@run_async
def ghci(bot: Bot, update: Update, args: List[str]):

	message = update.effective_message
	reply_text = ""
	
	if len(args) < 5:
		update.effective_message.reply_text("Please specify correct parameters. /ghci [TEST/BETA/OFFICIAL] [vendor] [codename] [branch] [changelog]")
		return
		
	project_slug = project_slug_device_tree(args[1], args[2])
	body = {'ref': args[3], 'inputs': { 'DEPLOY_TYPE': args[0], 'ChangeLogs': args[4]}}

	fetch = post(f'https://api.github.com/repos/{project_slug}/actions/workflows/PBRP.yml/dispatches', json=body, headers=ghci_headers())
			
	if fetch.status_code == 204:
		reply_text = f'Successfully triggered {args[0]} build for {args[1]}/{args[2]}. Good Luck with that!'
	else:
		reply_text = f'There is some error making request to GitHub Actions. Contact @manjotsidhu. Here are the logs: ```\n{fetch.json()}```'

	message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


__help__ = """
 - /circleci [vendor] [codename] [branch]: Triggers the pipeline for the device. If branch is not provided, default branch is used.
 - /ghci [TEST/BETA/OFFICIAL] [vendor] [codename] [branch] [changelog]: Triggers a dispatch_workflow for the device.
"""

__mod_name__ = "PBRP CI/CD"



CIRCLECI_TRIGGER_HANDLER = DisableAbleCommandHandler("circleci", circleci, pass_args=True, filters=CustomFilters.sudo_filter)
GHCI_TRIGGER_HANDLER = DisableAbleCommandHandler("ghci", ghci, pass_args=True, filters=CustomFilters.sudo_filter)


dispatcher.add_handler(CIRCLECI_TRIGGER_HANDLER)
dispatcher.add_handler(GHCI_TRIGGER_HANDLER)
