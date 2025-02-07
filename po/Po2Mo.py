#!/usr/bin/env python3

import os, glob, sys, time
import subprocess

PONAME = 'btkivy.po'
MONAME = 'btkivy.mo'
PODIR = os.getcwd()
MODIR = os.path.join(os.path.dirname(os.getcwd()), 'locale')
# MODIR = '/home/stas/SVN-WORK/schoolsplay/branches/seniorplay/locale'
# For testing purposes
# #PODIR = os.path.join('/tmp/gvr','po')
# #MODIR = os.path.join('/tmp/gvr','locale')

print("podir =", PODIR)
print("modir =", MODIR)

log = []

lines = [time.asctime() + '\n']

if len(sys.argv) == 2:
    print("Only generating %s" % sys.argv[1])
    files = ["%s/btkivy_%s.po" % (PODIR, sys.argv[1])]
    if not os.path.exists(files[0]):
        print("Can't find %s" % files[0])
        sys.exit(1)
else:
    files = glob.glob("%s/*.po" % PODIR)
# generate a list with locale names from the files.
# we check these to determinate if we generate full locales mo dirs
loclist = []
for name in files:
    loclist.append(os.path.basename(name).split('btkivy_')[1][:5])
print(loclist)

for pofile in files:
    # pofile = os.path.join(popath,PONAME)
    print("===================================================================")
    print("Processing", pofile)
    if os.path.exists(pofile) and 'latest' not in pofile:
        langlist = os.path.basename(pofile).split('btkivy_')
        print(langlist)
        langname0, langname1 = langlist[1].split('_')
        langname1 = langname1.split('.')[0]
        print(langname0, langname1)
        if langname0.upper() != langname1 and "%s_%s" % (langname0, langname1.upper()) in loclist:
            langname0 = "%s_%s" % (langname0, langname1)
            print("lang variant: %s" % langname0)
        modir = os.path.join(MODIR, langname0, 'LC_MESSAGES', MONAME)
        if not os.path.exists(os.path.join(MODIR, langname0, 'LC_MESSAGES')):
            os.makedirs(os.path.join(MODIR, langname0, 'LC_MESSAGES'))
        lines.append('============================ %s =================================\n' % langname0)
        line = "Result of compiling %s %s into %s:\n" % (PONAME, langname0, MONAME)
        lines.append(line)

        cmd = 'msgfmt -c -v -o %s %s' % (modir, pofile)
        print("Compiling po to mo", cmd)
        out = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE).communicate()[1]
        line = "output: %s" % out
        lines.append(line)
        print(line)


f = open('Po2Mo.log', 'w')
f.writelines(lines)
f.close()




