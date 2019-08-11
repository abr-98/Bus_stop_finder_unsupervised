import first_level_cluster
import second_level_cluster
import new_groundtruth
import sys
import os
import read_config

threshold_fp_fn={}



INPUT_FILE,OUTPUT_FOLDER,GROUND_TRUTH,DISTANCE_THRESHOLD,TIME_START,TIME_END,THRESHOLD, TRAIL_ID_RANGE,GROUND_TRUTH_THRESHOLD, FP_DISTANCE \
= read_config.read_config()

print INPUT_FILE,OUTPUT_FOLDER,GROUND_TRUTH,DISTANCE_THRESHOLD,TIME_START,TIME_END,THRESHOLD,TRAIL_ID_RANGE,GROUND_TRUTH_THRESHOLD,FP_DISTANCE

local_groups,num_trails= first_level_cluster.main(INPUT_FILE,DISTANCE_THRESHOLD,TIME_START,TIME_END,TRAIL_ID_RANGE)  #both arguments are directories (input and output, respectively)

print "Num trails: ",num_trails

def write_fp_fn(data):
    outfile= open(OUTPUT_FOLDER+os.sep+"detected_fp_fn.csv","w")
    outfile.write("DISTANCE_THRESHOLD,MIN_PTS,TRUE_POSIITIVE,FALSE_POSITIVE,FALSE_NEGATIVE\n")
    for line in data:
        line = [str(i) for i in line]
        line =",".join(line)+"\n"
        outfile.write(line)


def run_program(threshold):

    print "THRESHOLD ",threshold


    if OUTPUT_FOLDER not in os.listdir('.'):
        os.mkdir(OUTPUT_FOLDER)
    
    if str(threshold) not in os.listdir(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER+"/"+str(int(threshold)))


    second_level_cluster.main(OUTPUT_FOLDER, "bus_stops.csv",local_groups,threshold,num_trails,DISTANCE_THRESHOLD) #first argument is the input directory and the second argument is the output file

    # file_name = arguments.input_directory_name.split('_')[-1]
    
    #UNCOMMENT TO GET GROUND-TRUTH COMPARISON
    
    detected,fp,fn = new_groundtruth.compare_ground_truth(GROUND_TRUTH,OUTPUT_FOLDER+"/"+str(threshold)+'/bus_stops.csv',OUTPUT_FOLDER,threshold,GROUND_TRUTH_THRESHOLD,FP_DISTANCE)
    
    new_groundtruth.write_file(OUTPUT_FOLDER+os.sep+str(threshold)+os.sep+ "detected_stoppages.csv","gt_id,latitude,longitude,timestamp,total_wait_time,trail_number,spatial_spread,local_group_number,global_group_no",detected)
    new_groundtruth.write_file(OUTPUT_FOLDER+os.sep+str(threshold)+os.sep+"False_Positive.csv","latitude,longitude,timestamp,total_wait_time,trail_number,local_group_number,global_group_no",fp)
    new_groundtruth.write_file(OUTPUT_FOLDER+os.sep+str(threshold)+os.sep+"False_Negative.csv","gt_id,latitude,longitude",fn)

    # write_fp_fn(threshold,len(detected),len(fp),len(fn))

    # threshold_fp_fn[threshold]= [fp,fn]

    return len(detected),len(fp),len(fn)


if '-' in THRESHOLD:
    interval = THRESHOLD.split('-')
    first = int(interval[0])
    last = int(interval[1])

    data=[]

    for i in xrange(first,last+1,10):
        dt,fp,fn= run_program(i)
        data.append([DISTANCE_THRESHOLD,i,dt,fp,fn])

    write_fp_fn(data)

    #merge 0-thresholds (stops_vs_threshold) and individual threshold's fp/fn
    # f = open(OUTPUT_FOLDER+"/0/stops_vs_threshold.csv","r")
    # f_new = open(OUTPUT_FOLDER+"/0/stops_vs_threshold_merged.csv","w")

    # f_new.write("threshold%,stops%,false_positive%,false_negative%\n")

    # #read data from stops_vs_threshold and store it in a list of the form [[a,b],[c,d],..]
    # f_data = dict([[int(i.split(',')[0]),float(i.split(',')[1])] for i in f.read().split()[1:]])

    # for i,j in sorted(threshold_fp_fn.items()):

    #     if i in f_data:
    #         if j[0]== None:
    #             j[0]= 0
    #         if j[1]== None:
    #             j[1]= 100
    #         f_new.write(str(i)+","+str(f_data[i])+","+str(j[0])+","+str(j[1])+"\n")

else:
    dt,fp,fn=run_program(int(THRESHOLD))

    data=[]
    
    data.append([DISTANCE_THRESHOLD,THRESHOLD,dt,fp,fn])

    write_fp_fn(data)