import face_recognition
import numpy as np
import cv2
import os
import csv
from datetime import date
from .machine_learning import pipeline_model
# import attendence_sys.views 
from .views import *

def Recognizer(details):
	cap = cv2.VideoCapture(0)

# folder for attendences and csv file
	# now = date.today()
	# current_date = now.strftime("%d-%m-%Y")
	# directory = current_date
	# p_dir = "D:\MINI PROJECT\Original_onGo\Code_part\Django_part\FLAMES\Attendances"
	# path = os.path.join(p_dir,directory)
	# if not os.path.exists(path):
	# 	os.makedirs(path);
	# 	os.chdir(path)
	# 	# lnwriter = csv.writer(f);
	# 	with open(current_date+"-"+details['branch']+"-" + details['year'] +"-"+details['section']+"-"+details['period']+"P"+'.csv', 'w+', newline='') as f:
	# 		all_arr = f.readlines()
	# 		nameList = []
	# 		for line in all_arr:
	# 			entry = line.split(',')
	# 			nameList.append(entry[0])  # appending name
	# 		if name not in nameList:
	# 				f.writelines(details['name'],) 
	# else:
    # 	os.chdir(path)
    #    		# lnwriter = csv.writer(f);
    # 	with open(current_date+details['branch'] + details['year'] +details['section']+details['period']+'.csv', 'w+',newline='') as f:
	# 		fieldnames = [details['name'],details[]]
	# 		writer = csv.DictWriter(f,fieldnames=fieldnames)
    #        	all_arr = f.readlines()
	# 		nameList = []
	# 		for line in all_arr:
	# 			entry = line.split(',')
	# 			nameList.append(entry[0])  # appending name
	# 		if name not in nameList:
	# 			f.writelines(details['name'],)

	all_arr=[]
	flag = True
	while(flag==True):
		while True:
			ret, frame = cap.read()
			if ret == False:
				break
			image,namesarr = pipeline_model(frame) #names.append(face_name)
			for i in namesarr:
				if i not in all_arr:
					all_arr.extend(namesarr)
			# cv2.imshow('frame',frame)
			cv2.imshow('face recognition',image)
			if cv2.waitKey(1) == 27:
				flag=False
				break
		

	cap.release()
	cv2.destroyAllWindows()
	return all_arr