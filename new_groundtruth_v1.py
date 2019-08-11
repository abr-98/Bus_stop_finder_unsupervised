from lib import get_spherical_distance

def read_file(file_name):

    file_obj = open(file_name).readlines()[1:]
    for i in xrange(len(file_obj)):
        if "\r" in file_obj[i]:
            file_obj[i] = file_obj[i].split("\r")[0]
        if "\n" in file_obj[i]:
            file_obj[i] = file_obj[i].split("\n")[0]
        file_obj[i] = file_obj[i].split(",")
    return file_obj

def write_file(file_name,header,data):

	file_obj = open(file_name,"w")
	file_obj.write(header+"\n")

	for line in data:
		line = [str(i) for i in line]
		line = ",".join(line)+"\n"
		file_obj.write(line)

	file_obj.close()




def compare_ground_truth(ground_truth_file, bus_stop_file,OUTPUT_FOLDER,threshold,GROUND_TRUTH_THRESHOLD,FP_DISTANCE):

	gt = read_file(ground_truth_file)
	bus_stops = read_file(bus_stop_file)

	print "GT: ",len(gt)
	print "all bus_stops: ",len(bus_stops)
	print gt[0]
	print bus_stops[0]

	detected  = []
	false_negative=[]

	gt_dict={}
	used=[]

	for gt_point in gt:

		distances = []

		min_point = None
		min_dist = 100000000000000

		points=[]
		
		for bs_point in bus_stops:

			if bs_point in used:
				continue

			lat1 , long1 = gt_point[1:]

			lat2, long2 = bs_point[:2]

			dist = get_spherical_distance(lat1,lat2,long1,long2)

			#the stoppage at the closest distance goes at the end of the list
			if dist < min_dist and dist< GROUND_TRUTH_THRESHOLD:
				min_dist = dist
				min_point = bs_point
				points.append(bs_point)
				used.append(bs_point)

		gt_dict[gt_point[0]]= points

		if min_dist < GROUND_TRUTH_THRESHOLD:
			detected.append([gt_point[0]]+min_point)
		else:
			false_negative.append(gt_point)


	false_positive = bus_stops[:]

	# for i in gt_dict:
	# 	gt_dict[i].sort()
	for i,j in gt_dict.items():
		print i,len(j)

	for gt_id,bs_stops in gt_dict.items():
		
		for point in bs_stops[:-1]:
			bus_stops.remove(point)



	# print "$ ",len(gt_dict)

	for gt_id,bs_stops in gt_dict.items():
		
		# print "#################"
		for point in bs_stops:
			# print "Deleting ",point
			# print gt_id,point
			false_positive.remove(point)


	##removing false positives who are within 100m distance of each other
	false_positive_copy = false_positive[:]

	for i in xrange(len(false_positive_copy)):
		for j in xrange(i+1, len(false_positive_copy)):

			lat1 , long1 = false_positive_copy[i][:2]
			lat2, long2 = false_positive_copy[j][:2]
			dist = get_spherical_distance(lat1,lat2,long1,long2)

			if dist< FP_DISTANCE:
				if false_positive_copy[j] in false_positive:
					print i,j,dist
					print "removing: ",false_positive_copy[j]
					false_positive.remove(false_positive_copy[j])


	print "effective bus_stops: ", len(bus_stops)



	print "detected ", len(detected)



	# for bs_point in bus_stops:

	# 	found = False

	# 	for detected_point in detected:

	# 		if bs_point[:2] == detected_point[1:3]:
	# 			found = True
	# 			break

	# 	if found == False:
	# 		false_positive.append(bs_point)


	print "FP: ",len(false_positive),"(",len(false_positive)*100.0/len(bus_stops),"%",")"
	print "FN: ", len(false_negative),"(",len(false_negative)*100.0/len(gt),"%",")"

	

	return detected, false_positive, false_negative




# def main():
# 	ground_truth_file = "groundtruth/ukhra"
# 	bus_stop_file= "output_ukhra/25/bus_stops.csv"

# 	compare_ground_truth(ground_truth_file,bus_stop_file,"",25,60)

# main()


