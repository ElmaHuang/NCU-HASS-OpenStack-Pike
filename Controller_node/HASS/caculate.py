import os

cwd = os.path.dirname(os.path.abspath(__file__))  # current work directory

count = 0
f = open(cwd + "/Hass.py", 'r')
line = f.readline().rstrip('\n')
print line
while line:
    print count
    if "#" not in line:
        count += 1
    line = f.readline().rstrip('\n')
print count
