   @echo off
   echo Building EXE...
   python -m PyInstaller --onefile --strip --add-data ".env;." --hidden-import discord --hidden-import asyncio --hidden-import urllib --hidden-import requests --hidden-import json --hidden-import logging --hidden-import sys --hidden-import os --hidden-import dotenv DndAutoClickBot.py
   echo Build complete!
   pause