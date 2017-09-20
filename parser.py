# Author: Nicholas Antonov
import sys
import re
import json
import datetime
import time
from copy import deepcopy
from prettytable import PrettyTable

def format_for_output(item):
    out = deepcopy(item)
    for key in item:
        if type(item[key]) == datetime.datetime:
            out[key] = item[key].strftime('%Y-%m-%d')
    return out

def output_list(ls):
    return json.dumps(list(map(format_for_output, ls)), indent=4)

def parse(filename):
    correct_format = r'([012]) (\S{3,})(?:\s|$)?(.*)$'
    indi_fam_format = r'0 (\S+) (INDI|FAM)'
    allowed_tags = set(['INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE', 'HEAD', 'TR:R', 'NOTE'])
    namedict = {}
    spousedict = {}
    childdict = {}
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

    with open(filename) as f:
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
                        namedict[current['id']] = current['name']
                        people.append(current)
                    else:
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

            elif (current != None) and re.match(correct_format, line):
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
                    current['husband'] = namedict[args]
                    spousedict[namedict[args]] = args
                    current['husbandID'] = args
                elif tag == 'WIFE':
                    current['wife'] = namedict[args]
                    spousedict[namedict[args]] = args
                    current['wifeID'] = args
                elif tag == 'CHIL':
                    current['children'].append(namedict[args])
                    husband = current.get('husband')
                    wife = current.get('wife')
                    if husband != None:
                        husbchildren = childdict.get(husband)
                        if husbchildren == None:
                            childdict[husband] = [args]
                        else:
                            childdict[husband].append(args)
                    if wife != None:
                        wifechildren = childdict.get(wife)
                        if wifechildren == None:
                            childdict[wife] = [args]
                        else:
                            childdict[wife].append(args)

                prev = tag.lower()
            else:
                analysis += 'INPUT FORMAT INCORRECT'
            print('<--{}'.format(analysis))
            # used when date is encountered

    now = datetime.datetime.now()
    for i in people:
        name = i['name']
        spouse = spousedict.get(name)
        children = childdict.get(name)
        i['spouse'] = namedict.get(spouse)
        i['spouseID'] = spouse
        i['children'] = children
        date = i.get('birt-date')
        if date != None:
            delta = now - date
            i['age'] = delta.days / 365.25

    return (people, families)

if __name__ == "__main__":
    people, families = parse(sys.argv[1])

    print(output_list(people))
    print(output_list(families))

    with open('people.json', 'w') as outfile:
        outfile.write(output_list(people))

    with open('families.json', 'w') as outfile:
        outfile.write(output_list(families))

    pt = PrettyTable()
    pt.field_names = ['ID', 'NAME', 'GENDER', 'BIRTHDAY', 'AGE', 'DEAD', 'DEATH', 'CHILD', 'SPOUSE']
    for person in people:
        pt.add_row([person['id'], person['name'], person['sex'], person.get('birt-date'), person.get('age'), person.get('dead'),person.get('deat-date'),person.get('children'),person.get('spouseID')])
    print(pt)

    with open('people.txt', 'w') as outfile:
        outfile.write(str(pt))

    ptfam = PrettyTable()
    ptfam.field_names = ['ID', 'MARRIED', 'DIVORCED', 'HUSBAND ID', 'HUSBAND NAME', 'WIFE ID', 'WIFE NAME', 'CHILDREN']
    for fam in families:
        ptfam.add_row([fam['id'], fam.get('marr'), fam.get('div'), fam.get('husbandID'), fam.get('husband'), fam.get('wifeID'), fam.get('wife'), fam.get('children')])
    print(ptfam)

    with open('families.txt', 'w') as outfile:
        outfile.write(str(ptfam))

    with open('bothtables.txt', 'w') as outfile:
        outfile.write(str(pt))
        outfile.write('\n\n\n\n\n')
        outfile.write(str(ptfam))