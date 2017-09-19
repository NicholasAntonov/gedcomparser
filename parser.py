# Author: Nicholas Antonov
import sys
import re
import json
import datetime
import time
from copy import deepcopy


correct_format = r'([012]) (\S{3,})(?:\s|$)?(.*)$'
indi_fam_format = r'0 (\S+) (INDI|FAM)'
allowed_tags = set(['INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE', 'HEAD', 'TR:R', 'NOTE'])
namedict = {}
famdict = {}
tag_levels = {
    'INDI': 0,
    'NAME': 1,
    'SEX': 1,
    'BIRT': 1,
    'DEAT': 1,
    'FAMC': 1,
    'FAMS': 1,
    'FAM': 0,
    'MARR': 1,
    'HUSB': 1,
    'WIFE': 1,
    'CHIL': 1,
    'DIV': 1,
    'DATE': 2,
    'HEAD': 0,
    'TRLR': 0,
    'NOTE': 0
}

people = []
families = []

with open(sys.argv[1]) as f:
    content = f.readlines()

    current_type = None
    current = None
    prev = None
    for line in content:
        print('-->{}'.format(line.strip()))
        analysis = ''
        if re.match(indi_fam_format, line):
            # Handle saving the last object we were parsing
            if current != None:
                if current_type == 'INDI':
                    now = datetime.datetime.now()
                    #spouse = spousedict.get(name)
                    #children = childdict.get(name)
                    #i['spouse'] = namedict.get(spouse)
                    #i['spouseID'] = spouse
                    #i['children'] = children
                    date = current.get('birt-date')
                    if date != None:
                        delta = now - date
                        current['age'] = delta.days / 365.25
                    namedict[current['id']] = current
                    people.append(current)
                else:
                    famdict[current['id']] = current
                    families.append(current)

            # Parse and start handling the new object
            m = re.match(indi_fam_format, line)
            tag = m.group(2)
            identifier = m.group(1)

            current_type = tag
            if current_type == 'INDI':
                current = {
                    'id': identifier,
                    'dead': 'N'
                }
            else:
                current = {
                    'id': identifier,
                    'children': []
                }

            analysis = '0|{}|Y|{}'.format(tag, identifier)

        elif re.match(correct_format, line):
            m = re.match(correct_format, line)
            level = m.group(1)
            tag = m.group(2)
            args = m.group(3).strip()

            valid = 'Y' if (m.group(2) in allowed_tags) and (int(m.group(1)) == tag_levels[m.group(2)]) else 'N'
            analysis = '{}|{}|{}|{}'.format(level, tag, valid, args)

            # Individuals
            if tag == 'NAME':
                current['name'] = args
            elif tag == 'SEX':
                current['sex'] = args
            elif tag == 'DEAT':
                current['dead'] = args
            elif tag == 'DATE':
                current[prev + '-date'] = datetime.datetime.strptime(args, '%d %b %Y')
            # Families
            elif tag == 'HUSB':
                current['husband'] = args
                current['husbandname'] = namedict[args].get('name')
            elif tag == 'WIFE':
                current['wife'] = args
                current['wifename'] = namedict[args].get('name')
            elif tag == 'CHIL':
                current['children'].append(namedict[args].get('name'))
                husband = current.get('husband')
                wife = current.get('wife')
                if husband != None:
                    husbchildren = namedict.get(husband).get('children')
                    if husbchildren == None:
                        namedict[husband]['children'] = [args]
                    else:
                        namedict[husband]['children'].append(args)   
                if wife != None:
                    wifechildren = namedict.get(wife).get('children')
                    if wifechildren == None:
                        namedict[wife]['children'] = [args]
                    else:
                        namedict[wife]['children'].append(args)
                        
        else:
            analysis += 'INPUT FORMAT INCORRECT'
        print('<--{}'.format(analysis))
        # used when date is encountered
        prev = tag.lower()


def format_for_output(item):
    out = deepcopy(item)
    for key in item:
        if type(item[key]) == datetime.datetime:
            out[key] = item[key].strftime('%Y-%m-%d')
    return out

def output_list(ls):
    return json.dumps(list(map(format_for_output, ls)), indent=4)


print(output_list(people))
print(output_list(families))

with open('people.json', 'w') as outfile:
    outfile.write(output_list(people))

with open('families.json', 'w') as outfile:
    outfile.write(output_list(families))
