@echo off
title terminal for AI DM server
cd C:\Users\alawl\Desktop\Game Dev Projects\AI-DM-v2\AI-DM-v2
watchmedo auto-restart --patterns="*.py;*.html;*.js;*.css" --recursive -- python server.py