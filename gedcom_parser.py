#!/usr/bin/env python3

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

        def append_current():
            if current != None:
                if current_type == 'INDI':
                    people.append(current)
                else:
                    families.append(current)

        for line in content:
            if debug:
                print('-->{}'.format(line.strip()))
            analysis = ''
            if re.match(indi_fam_format, line):
                # Handle saving the last object we were parsing
                append_current()

                # Parse and start handling the new object
                m = re.match(indi_fam_format, line)
                tag = m.group(2)
                identifier = m.group(1)
                if get_by_id(people, identifier) or get_by_id(families, identifier):
                    firstperson = get_by_id(people, identifier)
                    firstfamily = get_by_id(families, identifier)
                    offender = firstperson if firstperson else firstfamily
                    errors.append(Error('Error US25: Not all names unique', 1, [offender]))

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

                    if args in allnames:
                        errors.append(Error('Error US25: Not all names unique', 1, [args]))
                    else:
                        allnames.append(args)

                elif tag == 'SEX':
                    current['sex'] = args
                elif tag == 'DEAT':
                    current['dead'] = args
                elif tag == 'DATE':
                    current[prev + '-date'] = datetime.datetime.strptime(args, '%d %b %Y')
                    if current[prev + '-date'] >= now:
                        errors.append(Error('Error US01: Date after current date', 1, [current['id']]))
                # Families
                elif tag == 'HUSB':
                    husband = get_by_id(people, args)
                    if husband != None and husband.get('sex') != 'M':
                        errors.append(Error('Error US21: Incorrect gender for role', 1, current['id']))
                    current['husband'] = args
                elif tag == 'WIFE':
                    wife = get_by_id(people, args)
                    if wife != None and wife.get('sex') != 'F':
                        errors.append(Error('Error US21: Incorrect gender for role', 1, current['id'])) 
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

        append_current()

    # Final pass through data to do calculations that can only be done after parse
    for person in people:

        birthdate = person.get('birt-date')
        marrdate = person.get('marr-date')
        deathdate = person.get('deat-date')
        age_end = deathdate if deathdate != None else now
        if birthdate != None:
            delta = age_end - birthdate
            person['age'] = delta.days / 365.25
            if (delta.days / 365.25) >= 150:
                errors.append(Error('Error US07: Greater than 150 years of age', 0, [person]))

        if birthdate and deathdate:
            if deathdate < birthdate:
                errors.append(Error('Error US03: Death date before birth date', 0, [person]))

    for family in families:
        husband = get_by_id(people, family.get('husband'))
        wife = get_by_id(people, family.get('wife'))
        hussurrname = ""
        if husband != None:
            namelist = husband.get('name').split()
            hussurrname = namelist[len(namelist)-1]
        childlist = family.get('children')

        for child in childlist:
            childobject = get_by_id(people, child)
            namelist = (childobject.get('name').split())
            childsurrname = namelist[len(namelist)-1]
            childbirth = childobject.get('birt-date')
            if husband != None:
                diff = (childbirth - husband.get('birt-date')).days / 365.25
                if diff > 80:
                    errors.append(Error('US12: Dad too old', 0, [husband, childobject]))
                if husband.get('deat-date') != None:
                    delta = (now - childbirth) - (now - husband.get('deat-date')) 
                    if (delta.days / 365.25) < 0.75:
                        errors.append(Error('US09: Child born after Father death', 0, [husband, childobject]))
            if wife != None:
                diff = (childbirth - wife.get('birt-date')).days / 365.25
                if diff > 60:
                    errors.append(Error('US12: Mom too old', 0, [wife, childobject]))
                if wife.get('deat-date') != None:
                    delta = (now - childbirth) - (now - wife.get('deat-date'))
                    if (delta.days / 365.25) < 0:
                        errors.append(Error('US09: Child born after Mother death', 0, [wife, childobject]))

            sex = childobject.get('sex')
            if sex == 'M':
                if childsurrname != hussurrname:
                    errors.append(Error('Error US16: Not Male last name', 0, [childobject.get('id')]))
            if sex == 'F':
                #If the child is a female and is married they will be a family so
                #they will still be checked for errors
                #Yes I know this can be put in the other loop, I'm going to do
                #that during refactor
                #Is a girl and is not married
                if childobject.get('spouse') == None:
                    if childsurrname != hussurrname:
                        errors.append(Error('Error US16: Not Male last name', 0, [childobject.get('id')]))


        #Make sure there are no more than 15 children per family
        if len(childlist) > 15:
            errors.append(Error('Error US15: More than 15 children in a family', 0, [family.get('id')]))           


        #Make sure that the children aren't born within 8 months of each other if they aren't twins
        #Also make sure siblings aren't married to each other
        marrdate = family.get('marr-date')
        husband = get_by_id(people, family.get('husband'))
        wife = get_by_id(people, family.get('wife'))

        for p in [husband, wife]:
            if p:
                birthdate = p.get('birt-date')
                deathdate = p.get('deat-date')

                if marrdate and deathdate:
                    if deathdate < marrdate:
                        errors.append(Error('Error US05: Marriage date after Death Date', 0, [p]))

                if birthdate and marrdate:
                    if marrdate < birthdate:
                        errors.append(Error('Error US02: Marriage date before birth date', 0, [p]))

        for child in childlist:
            childobject = get_by_id(people, child)
            childbirth = childobject.get('birt-date')
            childspouse = childobject.get('spouse')

            daysbornon = []
            daysdone = 0
            daysbornon.append(childbirth)
            for day in daysbornon:
                daysdone = daysbornon.count(day)
                if daysdone>=5:
                    errors.append(Error('Error US14: More than 5 birthdates', 4, [child]))

            if marrdate != None:
                if ((childbirth - marrdate).days) < 0:
                    errors.append(Error('Error US08: Birth before marriage of parents', 2, [child]))

            for otherchild in family.get('children'):
                if (otherchild == child):
                    continue
                else:
                    otherchildobject = get_by_id(people, otherchild)
                    otherchildbirth = otherchildobject.get('birt-date')
                    if (math.fabs((childbirth-otherchildbirth).days < 240) and math.fabs((childbirth-otherchildbirth).days > 2)):
                        errors.append(Error('Error US03: Child not a twin and born within 8 months of another child', 1, [child]))
                if (otherchild == childspouse):
                    errors.append(Error('Error US18: Siblings should not marry', 1, [child, childspouse]))


        if family.get('div-date') == None:
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


    iseedeadpeople = PrettyTable()
    iseedeadpeople.field_names = ['Dead People','Death Date']
    for person in people:
        if person.get('deat-date')!=None:
            iseedeadpeople.add_row([person['name'],person.get('deat-date')])
    print(iseedeadpeople)

    marriedlivingpeople = PrettyTable()
    marriedlivingpeople.field_names = ['Married People']
    for person in people:
        if person.get('spouse')!=None:
            if person.get('deat-date')==None: 
                marriedlivingpeople.add_row([person['name']])
    print(marriedlivingpeople)
        


    singlelivingpeople = PrettyTable()
    singlelivingpeople.field_names = ['Single Living People']
    for person in people:
        if person.get('deat-date')==None and person.get('spouse')==None:
                singlelivingpeople.add_row([person['name']])
    print(singlelivingpeople)

    with open('families.txt', 'w') as outfile:
        outfile.write(str(ptfam))

    with open('bothtables.txt', 'w') as outfile:
        outfile.write(str(pt))
        outfile.write('\n\n\n\n\n')
        outfile.write(str(ptfam))

    with open('errors.txt', 'w') as outfile:
        for error in errors:
            outfile.write(error.title + ': ')
            outfile.write(str(error.offenders))
            outfile.write('\n')

    with open('deadpeople.txt', 'w') as outfile:
        outfile.write(str(iseedeadpeople))

    with open('marriedlivingpeople.txt', 'w') as outfile:
        outfile.write(str(marriedlivingpeople))

    with open('singlelivingpeople.txt', 'w') as outfile:
        outfile.write(str(singlelivingpeople))

    print(json.dumps([(error.title) for error in errors], indent=4))

