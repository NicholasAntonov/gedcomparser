# Author: Nicholas Antonov
import sys
import re

correct_format = r'([012]) (\S{3,})(?:\s|$)(\S*)\n?'
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

with open(sys.argv[1]) as f:
    content = f.readlines()
    for line in content:
        print('-->{}'.format(line.strip()))
        analysis = ''
        if re.match(indi_fam_format, line):
            m = re.match(indi_fam_format, line)
            analysis = '0|{}|Y|{}'.format(m.group(2), m.group(1))
        elif re.match(correct_format, line):
            m = re.match(correct_format, line)
            analysis = '{}|{}|{}|{}'.format(m.group(1), m.group(2), 'Y' if (m.group(2) in allowed_tags) and (int(m.group(1)) == tag_levels[m.group(2)]) else 'N', m.group(3))
        else:
            analysis += 'INPUT FORMAT INCORRECT'
        print('<--{}'.format(analysis))
