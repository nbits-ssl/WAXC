import sys
import re
import itertools
import xml.etree.ElementTree as ET

HeaderKeys = 'default actor interaction prop event'.split()
SortedHeaders = {'default': [], 'actor': [], 'interaction': [], 'prop': [], 'event': []}
KeyTable = {'receiving_actor_id': 'interaction', 'prop_id': 'prop'}
# NoneString = '$$NONE$$'
NoneString = ''
QString = '"%s"'

ActorSuffix = '$ACT'
PropSuffix = '$PROP'
EventSuffix = '$EVENT'

def HeadersAppend(header, sortkey):
	key = KeyTable[sortkey] if sortkey in KeyTable else sortkey
	SortedHeaders[key].append(header)

def getText(text):
	if text:
		return QString % text
	else:
		return QString % NoneString

def loopAppend(suffix, elm, key, addchar, dic):
	id = 0
	for _elm in elm:
		for e in _elm:
			ename = e.attrib['n']
			text = e.text
			
			if ename == key:
				id = text
			
			if ename == 'dont_run_if':  # effect
				for dri in e:
					_ename = 'dont_run_if-' + dri.attrib['n'] + '_' + str(id) + suffix
					HeadersAppend(_ename, key)
					dic[_ename] = getText(dri.text)
			else:
				_ename = ename + addchar + '_' + str(id) + suffix
				HeadersAppend(_ename, key)
				dic[_ename] = getText(text)
			
		if key == 'event':  # increment for event list
			id += 1

def generateHeaders(priority):
	print(priority)
	actlst = [[]  for x in range(10)]
	for i in range(10):
		resuffix = re.compile('\D_%d%s$' % (i, re.escape(ActorSuffix)))
		actlst[i] = [x for x in SortedHeaders['actor'] if resuffix.search(x)]
	
	SortedHeaders['actor'] = list(itertools.chain(*actlst))
	
	lst = list(itertools.chain(*[SortedHeaders[key] for key in HeaderKeys]))  # merge
	lst = sorted(set(lst), key=lst.index)  # uniq
	
	prilst = []
	for x in priority:
		for head in lst:
			if head.startswith(x):
				lst.remove(head)
				prilst.append(head)
	
	return prilst + lst


def parse(path, config, priority, alternative):
	_lists = []
	
	print('Parse from: %s' % path)
	root = ET.parse(path).getroot()
	pkgname = root.attrib.get('n')
	
	for anim in root.find(".//*[@n='animations_list']"):
		d = dict()
		for content in anim:
			attname = content.attrib['n']
			if attname.endswith('_display_name'):
				print('# %s' % content.text)
			else:
				print('  %s' % attname)
			
			if attname == 'animation_actors_list':
				actor_id = 0
				for actor in content:
					for actcontent in actor:
						acname = actcontent.attrib['n']
						
						if acname == 'actor_interactions':
							loopAppend(ActorSuffix, actcontent, 'receiving_actor_id', '_' + str(actor_id), d)
						else:
							text = actcontent.text
							
							if acname == 'actor_id':
								actor_id = text
							
							_acname = acname + '_' + actor_id + ActorSuffix
							
							HeadersAppend(_acname, 'actor')
							d[_acname] = getText(text)
				
			elif attname == 'animation_props_list':
				loopAppend(PropSuffix, content, 'prop_id', '', d)
			elif attname == 'animation_events_list':
				loopAppend(EventSuffix, content, 'event', '', d)
			else:
				HeadersAppend(attname, 'default')
				d[attname] = getText(content.text)
		
		_lists.append(d)
	
	x = []
	headers = generateHeaders(priority)
	
	x.append('\t'.join(headers))
	for dic in _lists:
		x.append('\t'.join([dic.get(header, getText(NoneString)) for header in headers]))
	
	return (pkgname, '\n'.join(x))