import sys
import io
import re

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

import locale

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def tidy(path):
	tree = ET.parse(path)
	s = ET.tostring(tree.getroot()).decode('utf-8')
	s = ''.join([x.strip() for x in s.splitlines() if not x.strip() == ''])
	
	return minidom.parseString(s).toprettyxml(indent='  ')
