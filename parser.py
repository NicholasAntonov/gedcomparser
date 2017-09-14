# Author: Nicholas Antonov
import sys
import re

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

with open(sys.argv[1]) as f:
    content = f.readlines()

    current_type = None
    current = None
    for line in content:
        print('-->{}'.format(line.strip()))
        analysis = ''
        if re.match(indi_fam_format, line):
            # Handle saving the last object we were parsing
            if current_type == 'INDI':
                people.append(current)
            else:
                families.append(current)

            # Parse and start handling the new object
            m = re.match(indi_fam_format, line)
            tag = m.group(2)
            identifier = m.group(1)

            current_type = tag
            current = {'id': identifier}

            analysis = '0|{}|Y|{}'.format(tag, identifier)

        elif re.match(correct_format, line):
            m = re.match(correct_format, line)
            level = m.group(1)
            tag = m.group(2)
            args = m.group(3).strip()

            valid = 'Y' if (m.group(2) in allowed_tags) and (int(m.group(1)) == tag_levels[m.group(2)]) else 'N'
            analysis = '{}|{}|{}|{}'.format(level, tag, valid, args)

            if tag == 'NAME':
                current['name'] = args
            elif tag == 'SEX':
                current['sex'] = args


        else:
            analysis += 'INPUT FORMAT INCORRECT'
        print('<--{}'.format(analysis))


    print(people)
    print(families)
