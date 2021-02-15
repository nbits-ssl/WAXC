cd /d %~dp0
cd win32

for %%f in (%*) do (
	waxc.exe tidy %%f
)

pause