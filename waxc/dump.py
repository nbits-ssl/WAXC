import sys
import re
import csv
import hashlib
import xml.etree.ElementTree as et
import xml.dom.minidom as minidom

import waxc.fnv

ActorSuffix = '$ACT'
PropSuffix = '$PROP'
EventSuffix = '$EVENT'

DontRunIf = 'dont_run_if'
TagName = {'U': 'U', 'L': 'L', 'T': 'T'}

def getEntryIndex(keys, key, suffix):
	n = 0
	while True:
		_key = key + '_' + str(n) + suffix
		if _key in keys:
			n += 1
		else:
			break
	
	return n

def getInteractionIndexes(keys, keystring, suffix):
	indexes = []
	reintr = re.compile('^%s_\d+_(\d)+%s$' % (keystring, re.escape(suffix)))
	
	for key in keys:
		match = reintr.match(key)
		if match:
			indexes.append(match.group(1))
	
	return indexes

def loopGenerate(tree, parent, entrystring, keys, datadic, keystring, suffix):
	idx = getEntryIndex(keys, keystring, suffix)
	if idx == 0:
		return
	
	root = et.SubElement(parent, TagName['L'], {'n': entrystring})
	
	for n in range(idx):
		entry = tree.SubElement(root, TagName['U'])
		interactionkeys = []
		dontrunifkeys = []
		
		resuffix = re.compile('\D_%d$' % n)
		reintr = re.compile('_%d_\d+$' % n)
		
		for key in keys:
			_key = key.rstrip(suffix)
			rid = '_' + str(n)
			if _key.startswith(DontRunIf):  # must first
				dontrunifkeys.append(key)
			elif resuffix.search(_key):
				e = tree.SubElement(entry, TagName['T'], {'n': _key.rstrip(rid)})
				e.text = datadic[key]
			elif reintr.search(_key):
				interactionkeys.append(key)
		
		if interactionkeys:
			interactionGenerate(tree, entry, interactionkeys, datadic, 'receiving_actor_id', suffix)
		
		if dontrunifkeys:
			dontrunifGenerate(tree, entry, dontrunifkeys, datadic, n, suffix)

def interactionGenerate(tree, parent, keys, datadic, keystring, suffix):
	intrentry = tree.SubElement(parent, TagName['L'], {'n': 'actor_interactions'})
	
	for x in getInteractionIndexes(keys, keystring, suffix):
		entry = tree.SubElement(intrentry, TagName['U'])
		reintr = re.compile('_\d+_%s$' % x)
		
		for key in keys:
			_key = key.rstrip(suffix)
			match = reintr.search(_key)
			
			if match:
				e = tree.SubElement(entry, TagName['T'], {'n': _key.rstrip(match.group())})
				e.text = datadic[key]

def dontrunifGenerate(tree, parent, keys, datadic, effectid, suffix):
	drientry = None
	
	prefix = DontRunIf + '-'
	_suffix = '_' + str(effectid) + suffix
	
	for key in keys:
		if key.startswith(prefix) and key.endswith(_suffix):
			if not drientry:
				drientry = tree.SubElement(parent, TagName['U'], {'n': 'dont_run_if'})
			
			_key = key.lstrip(prefix).rstrip(_suffix)
			e = tree.SubElement(drientry, TagName['T'], {'n': _key})
			e.text = datadic[key]


def dump(path, pkgname, config):
	if config.get('TagName') == 'classic':
		global TagName
		TagName = {'U': 'T', 'L': 'T', 'T': 'T'}

	csvfile = open(path, encoding='utf-8')

	_d = {'c': 'WickedWhimsAnimationPackage', 'i': 'snippet', 'm': 'wickedwhims.sex.animations.animations_tuning'}
	_d['n'] = pkgname
	_d['s'] = str(waxc.fnv.fnv1_64(pkgname.encode().lower())) # FNV 64 decimal hash.
	root = et.Element('I', _d)

	wwanim = et.SubElement(root, 'T', {'n': 'wickedwhims_animations'})
	wwanim.text = "1"

	animlist = et.SubElement(root, 'L', {'n': 'animations_list'})  # this 'L' is always

	f = csv.DictReader(csvfile, delimiter = '\t')

	for d in f:  # d = 1 line = 1 animation
		entry = et.SubElement(animlist, TagName['U'])
		actkeys = []
		propkeys = []
		eventkeys = []
		
		for key, value in d.items():
			if key is not None and value != '':
				if key.endswith(ActorSuffix):
					actkeys.append(key)
				elif key.endswith(PropSuffix):
					propkeys.append(key)
				elif key.endswith(EventSuffix):
					eventkeys.append(key)
				else:
					elm = et.SubElement(entry, TagName['T'], {'n': key})
					elm.text = str(value)
		
		loopGenerate(et, entry, 'animation_actors_list', actkeys, d, 'actor_id', ActorSuffix)
		loopGenerate(et, entry, 'animation_props_list', propkeys, d, 'prop_id', PropSuffix)
		loopGenerate(et, entry, 'animation_events_list', eventkeys, d, 'event_type', EventSuffix)
	
	
	s = et.tostring(root)
	return minidom.parseString(s).toprettyxml(indent='  ')
