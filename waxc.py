import sys
import argparse
import shutil
import subprocess
from pathlib import Path

import waxc
import waxc.cfg


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
	config = waxc.cfg.read('../waxc.ini')
else:
	config = waxc.cfg.read('waxc.ini')

if (args.command == 'dump'):
	pkgname = ''
	with open(Path(args.filepath).with_suffix('.pkgname.txt')) as f:
		pkgname = f.read()
	
	x = waxc.dump(args.filepath, pkgname, config)
	fp = Path(args.filepath).with_suffix('.xml')
	write(fp, x)
elif (args.command == 'parse'):
	pkgname, x = waxc.parse(args.filepath, config)
	
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
	pkgname, x = waxc.parse(args.filepath, config)
	csvfp = Path(TmpDir + '/' + fname).with_suffix('.csv')
	write(csvfp, x, False)
	
	# dump
	x = waxc.dump(csvfp, pkgname, config)
	xmlfp = Path(TmpDir + '/' + fname)
	write(xmlfp, x, False)
	
	with open(TmpDir + '/x.diff', 'w') as f:
		subprocess.run(f'diff {tidyfp} {xmlfp}', stdout=f, shell=True, text=True)

