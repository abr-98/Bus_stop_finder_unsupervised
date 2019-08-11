import sys

def read_data(file_name):
	"""

	read the data from a csv file

	"""
	raw= open(file_name).read().split('\n')[1:]
	data=[]
	for line in raw:
		if '\r' in line:
			line=line.split('\r')[0]
		line=line.split(',')
		data.append(line)

	while len(data[-1]) <  3:
		data.pop()

	return data

def write_file(data,file_name):
	out_file = open(file_name+"_out","w")
	i=1
	out_file.write("stop_number,latitude,longitude\n")
	for each_point in data:
		s = str(each_point[0])+","+str(each_point[1])
		out_file.write(str(i)+","+s+"\n")
		i+=1




def main():
	file_name=sys.argv[1]
	data = read_data(file_name);
	write_file(data,file_name)
	print data[:2]

main()