import sys
import argparse
import shutil
import subprocess
from pathlib import Path

import waxc
import waxc.cfg

fpath = {
	'config': 'waxc.ini',
	'defaultconfig': 'res/waxc.ini.default',
	'alternative': 'res/alternative.txt',
	'priority': 'res/priority.txt',
}

def readpriority(filepath):
	lst = []
	
	if filepath.exists():
		with filepath.open('r', encoding='utf-8') as f:
			lst = f.read().splitlines()
	
	return lst

def readalternative(filepath):
	table = {}
	
	if filepath.exists():
		with filepath.open('r', encoding='utf-8') as f:
			for line in f.read().splitlines():
				if ': ' in line:
					lst = line.split(': ')
					table[lst[0]] = lst[1]
	
	return table

def write(filepath, x, backup = True):
	if filepath.exists() and backup:
		backup_fp = filepath.with_suffix('.backup' + filepath.suffix)
		shutil.copy2(filepath, backup_fp)
	with open(filepath, 'w', encoding='utf-8') as f:
		f.write(x)


p = argparse.ArgumentParser()
p.add_argument('command', choices=['parse', 'dump', 'tidy', 'test'])
p.add_argument('filepath')

args = p.parse_args()

scriptname = Path(sys.argv[0]).name
if scriptname == 'waxc.exe':  # py2exe
	for key, value in fpath.items():
		fpath[key] = '../' + value

cfgpath = Path(fpath['config'])
if not cfgpath.exists():
	shutil.copy(Path(fpath['defaultconfig']), cfgpath)

config = waxc.cfg.read(cfgpath)
priority = readpriority(Path(fpath['priority']))
alternative = readalternative(Path(fpath['alternative']))

if (args.command == 'dump'):
	pkgname = ''
	with open(Path(args.filepath).with_suffix('.pkgname.txt')) as f:
		pkgname = f.read()
	
	x = waxc.dump(args.filepath, pkgname, config, alternative)
	fp = Path(args.filepath).with_suffix('.xml')
	write(fp, x)
elif (args.command == 'parse'):
	pkgname, x = waxc.parse(args.filepath, config, priority, alternative)
	
	fp = Path(args.filepath).with_suffix('.csv')
	write(fp, x)
	fp = Path(args.filepath).with_suffix('.pkgname.txt')
	write(fp, pkgname, False)

elif (args.command == 'tidy'):
	x = waxc.tidy(args.filepath)
	fp = Path(args.filepath).with_suffix('.tidy.xml')
	write(fp, x, False)

elif (args.command == 'test'):
	TmpDir = 'tmp'
	Path(TmpDir).mkdir(exist_ok=True)
	fname = Path(args.filepath).name
	
	# tidy
	x = waxc.tidy(args.filepath)
	tidyfp = Path(TmpDir + '/' + fname).with_suffix('.tidy.xml')
	write(tidyfp, x, False)  # tidy xml
	
	# parse
	pkgname, x = waxc.parse(args.filepath, config, priority, alternative)
	csvfp = Path(TmpDir + '/' + fname).with_suffix('.csv')
	write(csvfp, x, False)
	
	# dump
	x = waxc.dump(csvfp, pkgname, config, alternative)
	xmlfp = Path(TmpDir + '/' + fname)
	write(xmlfp, x, False)
	
	with open(TmpDir + '/x.diff', 'w') as f:
		subprocess.run(f'diff {tidyfp} {xmlfp}', stdout=f, shell=True, text=True)

