import os
import sys
from lib import *

local_groups=[] #store all the local group leaders per group per trail in a file

# num_trails= 0
ignored_trails=[]

class First_level_cluster():

    def __init__(self):
        self.data_lines=[]         #contains latitude, longitude, time-stamp,trail_number
        self.zero_speed_data=[]    # contains latitude, longitude, time-stamp, count, trail_number
        self.local_group_data=[]   # contains latitude, longitude, time-stamp, count, trail_number, local_group_number
        self.local_group_leader=[] # contains latitude, longitude, time-stamp, total_wait_time, trail_number, local_group_number
        #self.distance_threshold= 100

    def compare_time(self,time1,time2):

        for i in xrange(0,len(time1)):
            if(time1[i] > time2[i] ):
                return 1
            elif(time1[i] < time2[i] ):
                return -1
            else:
                continue
        return 0

    def read_data(self,file_name,TIME_START,TIME_END):
        """ reads the file named file_name and stores it in data_lines """

        print file_name,TIME_START,TIME_END
        input_file= open(file_name,'r')
        temp= input_file.readlines()[1:]
        #print temp

        time_stamp = temp[0].split()[0].split(',')
        time = [int(i) for i in time_stamp[-1].split(':')]
        # hour = int(time_stamp[-1].split(':')[0])
        global ignored_stops

        if(self.compare_time(time,TIME_START) < 0):
            ignored_trails.append(file_name)
            return 0

        if(self.compare_time(time,TIME_END) >= 0):
            ignored_trails.append(file_name)
            return 0


        # num_trails+=1

        for i in temp:
            each_line = i
            line = each_line.split(',')
            time_stamp = line[2].split()[0]
            time = [int(float(j)) for j in time_stamp.split(':')]
            #print i
            #hour = int(time_stamp.split(':')[0])
            # print time, TIME_START,TIME_END
            # print self.compare_time(time,TIME_START), self.compare_time(time,TIME_END)
            if self.compare_time(time,TIME_START)>=0 and self.compare_time(time,TIME_END) < 0:
                    self.data_lines.append(each_line)
                    #print "YES"
            # else:
            #     print "NO"
        #print self.data_lines
        input_file.close()
        return 1

    def print_data(self, data_list):
        """ prints the data_list. For test purposes only. """
        j=1
        for i in data_list:
            print j,i
            j+=1

    def process_line(self,raw_data,trail_number):
        """ Takes a line of raw gps data and returns latitude,longitude and timestamp """

        line= raw_data.split(',')
        #print line
        latitude, longitude, timestamp = line[0],line[1], line[2].split()[0]
        return latitude,longitude, timestamp,trail_number

    def get_zero_speed_data(self,trail_number):
        """
            stores the duplicate contiguous points in a list.
            compare each line of gps data with the next one, group them if they are same
            and store them in the list zero_speed_data once a different line of data has been
            found and start a new group.
            the list zero_speed_data contains only the first point of each group and contains
            an additional attribute count to store the number of duplicate contiguous points present (excluding itself).

            output list: latitude,longitude,timestamp,count,local_group_number
                         where count= number of duplicate contiguous points

        """
        #print ">",self.data_lines
        count=0
        #get the first point from the raw trail data

        if self.data_lines == []:
            return

        current_latitude, current_longitude, current_timestamp, trail_number= self.process_line(self.data_lines[0],trail_number)

        for next_line in self.data_lines[1:]:
            #get the next point
            next_latitude, next_longitude, next_timestamp,trail_number= self.process_line(next_line,trail_number)
            #if current and next points are same, duplicate points found, increment count
            if (str(current_latitude),str(current_longitude)) == (str(next_latitude),str(next_longitude)):
                count+=1
            else:
                #if there is at least one additional duplicate point
                if count>0:
                    #add the first point of the group to the zero_speed_list
                    self.zero_speed_data.append([current_latitude,current_longitude,current_timestamp,count,trail_number])
                    count=0 #reset count so as to mark the beginning of a new group
                current_latitude, current_longitude, current_timestamp = next_latitude, next_longitude, next_timestamp
                #assign the next point to be the current point, ie, it is probably the first point of a next zero-speed group


    def get_local_groups(self,DISTANCE_THRESHOLD):
        """
        assign local group number to each point
        """
        #assign first point of zero_speed_data to be in local group 1
        local_group_no=1

        if self.zero_speed_data == []:
            return

        current_point = self.zero_speed_data[0]+[local_group_no]
        self.local_group_data.append(current_point)

        #for each point in the zero_speed_data list
        for each_point in self.zero_speed_data[1:]:
            #get distance between the current_point and each_point
            distance= get_spherical_distance(float(current_point[0]),float(each_point[0]),float(current_point[1]),float(each_point[1]))
            # if current_point[2]=='09:51:38':
            #     print current_point,"===>",each_point,"====>",distance,DISTANCE_THRESHOLD

            if distance > DISTANCE_THRESHOLD:
                #create a new group
                local_group_no+=1
            #assign each point to local_group_no
            #point to note: local_group_no doesn't change if the distance between two points is <= distance_threshold.

            each_point= each_point + [local_group_no] #append the local_group_no (changed/unchanged) to the next point
            self.local_group_data.append(each_point)
            current_point= each_point #assign each_point to the current_point


    def get_local_group_leaders(self):

        """ get all of the local group leader points for all groups in a trail
            we store the group leader points for a trail in local_group_leader[]
        """

        #group the points based on local group_number and store the local group leader of each group


        #attach a dummy variable to the end of local_group_data
        #we'll remove it after operation
        #significance: to append the new group formed after the operation on last element of the list
        #since we add a new group only when we find a change in the local_group_number between consecutive
        #elements, we need to make sure that we have a dummy variable to check the last element of the list with.
        #and form the last group

        self.local_group_data.append([-12])

        group=[] #stores a group of points temporarily
        group_number=1
        for each_point in self.local_group_data:
            #check the local group number for each point, if it is equal to  group_number append it to group
            if each_point[-1] == group_number:
                group.append(each_point)
            else:
                #get the group leader of the current group
                group_leader= get_group_leader(group)
                #and append it to local_group_leader[]
                self.local_group_leader.append(group_leader)
                group_number+=1 #create a new group
                group=[] #reset group[]
                group.append(each_point) #add the current point to the new group
        self.local_group_data.pop() # removing the dummy variable

    def write_data(self,file_name):
        """write the local group leader data to file_name"""
        write_trail= open(file_name,'w')
        for data_line in self.local_group_leader:
            data_line= [str(el) for el in data_line]
            write_trail.write(','.join(data_line)+"\n")
        write_trail.close()


#############          End of class definition     #############################


def get_file_names(path):
    """ Helper function: returns all the files in a directory named path

    For example:
    if path= 'up/'
    then this function returns all the file names present inside the directory 'up/'
    """
    names= os.listdir(path)
    return names

def get_output_file_name(path,name):
    """returns output file name depending on the trail"""
    out_name= path+'/'+name.split('.')[0]+'_out.txt'
    return out_name

def comp(a):
    """comparison function to sort the file_names lexicographically.... eg, up_1 comes before up_2"""
    a= a.split('_')
    a= int(a[1].split('.')[0])
    return a

def write_data_to_file(file_name,object_name,header):

    if object_name == None:
        print "Can't write to file "
    write_file= open(file_name,'w')
    write_file.write(header+'\n')
    for i in object_name:

        if i==None:
            continue
        #print i
        i=[str(j) for j in i]
        write_file.write(','.join(i)+'\n')
    write_file.close()

def clean_directory(directory_name):
    for i in os.listdir(directory_name):
        #print "removing ",i
        os.remove(directory_name+'/'+i)


def main(directory,DISTANCE_THRESHOLD,TIME_START,TIME_END,TRAIL_ID_RANGE):
    """ First-level-clustering algorithm
    Input: set of trails containing points (latitude,longitude, altitude, timestamp)
    output: leader points (latitude, longitude, timestamp, wait_time, local_group_number) for all groups in each trail
    """
    call_algo= First_level_cluster()

    #get all the file_names in the directory into a list and sort them up lexicographically
    trails= sorted(get_file_names(directory),key=comp)[: TRAIL_ID_RANGE]
    print "number of trails ",len(trails)
    #print trails,len(trails)


    #for each file in the list trails

    if 'details' not in os.listdir('.'):
        os.mkdir('details')
    else:
        clean_directory('details')

    trail_index=1
    num_trails=0

    for trail in trails:
        input_trail= directory +'/'+ trail #get the path of the input file | for example, up/up_1.txt
        successs = call_algo.read_data(input_trail,TIME_START,TIME_END) #read all the points in the input_trail and store it in data_lines[]

        if successs==1:
            num_trails+=1

        call_algo.get_zero_speed_data(trail_index)  #get all the zero-speed points and store it in zero_speed_data[]
        header= "latitude, longitude, time-stamp,count,trail_number"
        write_data_to_file('details/'+trail+'_zero_speed.txt',call_algo.zero_speed_data,header)

        call_algo.get_local_groups(DISTANCE_THRESHOLD)     #get all local groups from zero-speed points and store in local_group_data[]
        header= "latitude, longitude, time-stamp, count, trail_number, local_group_number"
        write_data_to_file('details/'+trail+'_local_groups.txt',call_algo.local_group_data,header)

        call_algo.get_local_group_leaders() #get all local group leaders from local_group_data and store in local_group_leader[]
        header= "latitude, longitude, time-stamp, count, trail_number, local_group_number"
        write_data_to_file('details/'+trail+'_local_group_leader.txt',call_algo.local_group_leader,header)

        local_groups.append(call_algo.local_group_leader)

        trail_index+=1

        call_algo.__init__();  #re-initialize all attributes of the object call_algo for the next trail

    print "IGNORED: ",ignored_trails,len(ignored_trails)
    print "Effective no of trails: ",num_trails
    return local_groups,num_trails
