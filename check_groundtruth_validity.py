#example run:
#python check_groundtruth_validity groundtruth/ukhra

import csv
import sys


file_name = sys.argv[1]
reader = csv.reader(open(file_name,"r"),delimiter=",")
rows= []
for i in reader:
	rows.append(i)

header = rows.pop(0)

flag = True

for i in xrange(len(rows)):
	for j in xrange(i+1,len(rows)):
		if rows[i][1:] == rows[j][1:]:
			print rows[i], rows[j]
			flag = False

if flag == False:
	print "Groundtruth is not valid"
else:
	print "Groundtruth is valid"
