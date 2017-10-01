import sys
import re
import json
import datetime
import time
import math
from copy import deepcopy
from prettytable import PrettyTable
from error import Error

debug = False

def format_for_output(item):
    out = deepcopy(item)
    for key in item:
        if type(item[key]) == datetime.datetime:
            out[key] = item[key].strftime('%Y-%m-%d')
    return out

def output_list(ls):
    return json.dumps(list(map(format_for_output, ls)), indent=4)

# This will end up making the parser O(n^2) but since we are bounded to a small input size its fine
def get_by_id(ls, identifier):
    for item in ls:
        if item.get('id') == identifier:
            return item
    return None

def parse(filename):
    correct_format = r'([012]) (\S{3,})(?:\s|$)?(.*)$'
    indi_fam_format = r'0 (\S+) (INDI|FAM)'
    allowed_tags = set(['INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE', 'HEAD', 'TR:R', 'NOTE'])
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
    errors = []
    allnames = []

    now = datetime.datetime.now()
    with open(filename) as f:
        content = f.readlines()

        current_type = None
        current = None
        prev = None
        for line in content:
            if debug:
                print('-->{}'.format(line.strip()))
            analysis = ''
            if re.match(indi_fam_format, line):
                # Handle saving the last object we were parsing
                if current != None:
                    if current_type == 'INDI':
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
                        'dead': 'N',
                        'children': []
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
                    allnames.append(args)
                elif tag == 'SEX':
                    current['sex'] = args
                elif tag == 'DEAT':
                    current['dead'] = args
                elif tag == 'DATE':
                    current[prev + '-date'] = datetime.datetime.strptime(args, '%d %b %Y')
                    if current[prev + '-date'] >= now:
                        errors.append(Error('Date after current date', 1, [current['id']]))
                # Families
                elif tag == 'HUSB':
                    current['husband'] = args
                elif tag == 'WIFE':
                    current['wife'] = args
                elif tag == 'MARR':
                    current['marr'] = args
                elif tag == 'CHIL':
                    child = args
                    current['children'].append(child)
                    husband = get_by_id(people, current.get('husband'))
                    wife = get_by_id(people, current.get('wife'))
                    if husband != None:
                        husband['children'].append(child)
                    if wife != None:
                        wife['children'].append(child)

                # used when date is encountered
                prev = tag.lower()
            else:
                analysis += 'INPUT FORMAT INCORRECT'
            if debug:
                print('<--{}'.format(analysis))

        if current != None:
            if current_type == 'INDI':
                people.append(current)
            else:
                families.append(current)


    # Final pass through data to do calculations that can only be done after parse
    for person in people:
        date = person.get('birt-date')
        deathdate = person.get('deat-date')
        age_end = deathdate if deathdate != None else now
        if date != None:
            delta = age_end - date
            person['age'] = delta.days / 365.25

        if date and deathdate:
            if deathdate < date:
                errors.append(Error('Death date before birth date', 0, [person]))

        sizeallnames = len(allnames)
        sizeallnamesunique = len(set(allnames))
        if sizeallnamesunique < sizeallnames:
            errors.append(Error('US25: Not all names unique', 3, [person]))



    for family in families:
        #Make sure that the children aren't born within 8 months of each other if they aren't twins
        marrdate = family.get('marr-date')

        for child in family.get('children'):
            childobject = get_by_id(people, child)
            childbirth = childobject.get('birt-date')

            if marrdate != None:
                if ((childbirth - marrdate).days) < 0:
                    errors.append(Error('Anomaly US08: Birth before marriage of parents', 2, [child]))
                    
            for otherchild in family.get('children'):
                if (otherchild == child):
                    continue
                else:
                    otherchildobject = get_by_id(people, otherchild)
                    otherchildbirth = otherchildobject.get('birt-date')
                    if (math.fabs((childbirth-otherchildbirth).days < 240) and math.fabs((childbirth-otherchildbirth).days > 2)):
                        errors.append(Error('Child not a twin and born within 8 months of another child', 1, [child]))


        if family.get('div-date') == None:
            husband = get_by_id(people, family.get('husband'))
            wife = get_by_id(people, family.get('wife'))
            if husband:
                husband['spouse'] = family.get('wife')
            if wife:
                wife['spouse'] = family.get('husband')

    return (people, families, errors)

if __name__ == "__main__":
    people, families, errors = parse(sys.argv[1])

    print(output_list(people))
    print(output_list(families))

    with open('people.json', 'w') as outfile:
        outfile.write(output_list(people))

    with open('families.json', 'w') as outfile:
        outfile.write(output_list(families))

    pt = PrettyTable()
    pt.field_names = ['ID', 'NAME', 'GENDER', 'BIRTHDAY', 'AGE', 'DEAD', 'DEATH', 'CHILD', 'SPOUSE']
    for person in people:
        pt.add_row([person['id'], person['name'], person['sex'], person.get('birt-date'), person.get('age'), person.get('dead'),person.get('deat-date'),person.get('children'),person.get('spouse')])
    print(pt)

    with open('people.txt', 'w') as outfile:
        outfile.write(str(pt))

    ptfam = PrettyTable()
    ptfam.field_names = ['ID', 'MARRIED', 'DIVORCED', 'HUSBAND ID', 'HUSBAND NAME', 'WIFE ID', 'WIFE NAME', 'CHILDREN']
    for fam in families:
        husband = get_by_id(people, fam.get('husband'))
        wife = get_by_id(people, fam.get('wife'))
        ptfam.add_row([fam['id'], fam.get('marr-date'), fam.get('div-date'), fam.get('husband'), None if husband == None else husband.get('name'), fam.get('wife'), None if wife == None else wife.get('name'), fam.get('children')])
    print(ptfam)

    with open('families.txt', 'w') as outfile:
        outfile.write(str(ptfam))

    with open('bothtables.txt', 'w') as outfile:
        outfile.write(str(pt))
        outfile.write('\n\n\n\n\n')
        outfile.write(str(ptfam))

    print(json.dumps([(error.title) for error in errors], indent=4))
