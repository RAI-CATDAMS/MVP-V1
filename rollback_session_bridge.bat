@echo off
echo Rolling back session bridge changes...
echo Restoring original content.js...
copy catdams-browser-extension\content.js.pre_bridge_backup catdams-browser-extension\content.js
echo.
echo Rollback complete! Original content.js has been restored.
echo You may need to reload the browser extension for changes to take effect.
pause 