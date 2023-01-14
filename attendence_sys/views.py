from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.conf import settings

from .forms import *
from .models import Student, Attendence
from .filters import AttendenceFilter
import os
import csv
from django.core.mail import send_mail,EmailMessage
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# from django.views.decorators import gzip

from .recognizer import Recognizer
from datetime import date

@login_required(login_url = 'login')
def home(request):
    studentForm = CreateStudentForm()

    if request.method == 'POST':
        studentForm = CreateStudentForm(data = request.POST, files=request.FILES)
        # print(request.POST)
        stat = False 
        try:
            student = Student.objects.get(registration_id = request.POST['registration_id'])
            stat = True
        except:
            stat = False
        if studentForm.is_valid() and (stat == False):
            studentForm.save()
            name = studentForm.cleaned_data.get('firstname') +" " +studentForm.cleaned_data.get('lastname')
            messages.success(request, 'Student ' + name + ' was successfully added.')
            return redirect('home')
        else:
            messages.error(request, 'Student with Registration Id '+request.POST['registration_id']+' already exists.')
            return redirect('home')

    context = {'studentForm':studentForm}
    return render(request, 'attendence_sys/home.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'attendence_sys/login.html', context)

@login_required(login_url = 'login')
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url = 'login')
def updateStudentRedirect(request):
    context = {}
    if request.method == 'POST':
        try:
            reg_id = request.POST['reg_id']
            branch = request.POST['branch']
            student = Student.objects.get(registration_id = reg_id, branch = branch)
            updateStudentForm = CreateStudentForm(instance=student)
            context = {'form':updateStudentForm, 'prev_reg_id':reg_id, 'student':student}
        except:
            messages.error(request, 'Student Not Found')
            return redirect('home')
    return render(request, 'attendence_sys/student_update.html', context)

@login_required(login_url = 'login')
def updateStudent(request):
    if request.method == 'POST':
        context = {}
        try:
            student = Student.objects.get(registration_id = request.POST['prev_reg_id'])
            updateStudentForm = CreateStudentForm(data = request.POST, files=request.FILES, instance = student)
            if updateStudentForm.is_valid():
                updateStudentForm.save()
                messages.success(request, 'Updation Success')
                return redirect('home')
        except:
            messages.error(request, 'Updation Unsucessfull')
            return redirect('home')
    return render(request, 'attendence_sys/student_update.html', context)


# global names
# names=[]            
@login_required(login_url = 'login')
def takeAttendence(request):
    if request.method == 'POST':
        details = {
            'branch':request.POST['branch'],
            'year': request.POST['year'],
            'section':request.POST['section'],
            'period':request.POST['period'],
            'faculty':request.user.faculty,
            'email':request.user.email
            }
        # today = date.today().strftime("%d/%m/%Y")
        today = date.today()
        if Attendence.objects.filter(date = str(today),branch = details['branch'], year = details['year'], section = details['section'],period = details['period']).count() != 0 :
            messages.error(request, "Attendence already recorded.")
            return redirect('home')
        else:
            students = Student.objects.filter(branch = details['branch'], year = details['year'], section = details['section'])
            names=Recognizer(details)
            # print(names)
            # print(students)
        #  Storing in database
            for student in students:
                if str(student.registration_id) in names:
                    attendence = Attendence(Faculty_Name = request.user.faculty, 
                    Student_ID = str(student.registration_id), 
                    period = details['period'], 
                    branch = details['branch'], 
                    year = details['year'], 
                    section = details['section'],
                    status = 'Present')
                    attendence.save()
                else:
                    attendence = Attendence(Faculty_Name = request.user.faculty, 
                    Student_ID = str(student.registration_id), 
                    period = details['period'],
                    branch = details['branch'], 
                    year = details['year'], 
                    section = details['section'])
                    attendence.save()
    # ---------------------------------------------------
    # folder for attendences and csv file
            current_date = today.strftime("%d-%m-%Y")
            directory = current_date
            p_dir = "D:\MINI PROJECT\Original_onGo\Code_part\Django_part\FLAMES\Attendances"
            path = os.path.join(p_dir, directory)
            if not os.path.exists(path):
                os.makedirs(path);
                os.chdir(path)
                # lnwriter = csv.writer(f);
                dic = {}
                nameList = []
                for student in students:
                    dic['Roll_no'] = str(student.registration_id)
                    dic['Year'] = details['year']
                    dic['Branch'] = details['branch']
                    dic['Section'] = details['section']
                    dic['Period'] = details['period']
                    if str(student.registration_id) in names:
                        dic['Status'] = 'Present'
                    else:
                        dic['Status'] = 'Absent'
                    # print(dic)
                    nameList.append(dic.copy())
                # print(nameList)
                # print(dic)
                with open(current_date+"-"+details['branch']+"-" + details['year'] + "-"+details['section']+"-"+details['period']+"P"+'.csv',mode='w+', newline='') as f:
                    fieldnames = nameList[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    # names = f.readlines()
                    
                    #     entry = line.split(',')
                    #     nameList.append(entry[0])  # appending name
                    # for row in nameList:
                        # if row[0] not in nameList:
                    writer.writerows(nameList)
                        # f.writelines(details['name'],)
            else:
                os.chdir(path)
                    # lnwriter = csv.writer(f);
                dic = {}
                nameList = []
                for student in students:
                    dic['Roll_no'] = str(student.registration_id)
                    dic['Year'] = details['year']
                    dic['Branch'] = details['branch']
                    dic['Section'] = details['section']
                    dic['Period'] = details['period']
                    if str(student.registration_id) in names:
                        dic['Status'] = 'Present'
                    else:
                        dic['Status'] = 'Absent'
                    # print(dic)
                    nameList.append(dic.copy())
                # print(nameList)
                # print(dic)
                with open(current_date+"-"+details['branch']+"-"+ details['year'] +"-"+ details['section']+"-"+details['period']+"P"+'.csv',   mode='w+',newline='') as f:
                    fieldnames = nameList[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    # names = f.readlines()
                    
                    #     entry = line.split(',')
                    #     nameList.append(entry[0])  # appending name
                    # for row in nameList:
                        # if row[0] not in nameList:
                    writer.writerows(nameList)
                        # f.writelines(details['name'],) 
    # ---------------------------------------------------
        #  Sending the attendance to email
            # Sending text
            # send_mail(
            #     'Attendance',
            #     'Here is the message.',
            #     'demoemail12.2022@gmail.com',
            #     # ['vvaddanki30521@gmail.com',"vvrock63@gmail.com"],
            #     [details['email']],
            #     fail_silently=False,
            # )       
            # ------------------------------
            # Sending attachment
            subject = str('Attendance of '+current_date+"-" +details['branch']+"-" + details['year'] + "-"+details['section']+"-"+details['period']+"P")
            content = str('Attendance of '+current_date+"-" +details['branch']+"-" + details['year'] + "-"+details['section']+"-"+details['period']+"P")
            filename = "D:/MINI PROJECT/Original_onGo/Code_part/Django_part/FLAMES/Attendances/{}/{}-{}-{}-{}-{}P.csv".format(current_date,current_date,details['branch'],details['year'],details['section'],details['period'])
            
            email_message = EmailMessage(subject,content,settings.EMAIL_HOST_USER,[details['email']])
            email_message.attach_file(filename)
            email_message.send()
            
            # -----------------------------------
            attendences = Attendence.objects.filter(date = str(date.today()),branch = details['branch'], year = details['year'], section = details['section'],period = details['period'])
            context = {"attendences":attendences, "ta":True}
            messages.success(request, "Attendence taking Success")
            return render(request, 'attendence_sys/attendence.html', context)        
    context = {}
    return render(request, 'attendence_sys/home.html', context)

def searchAttendence(request):
    attendences = Attendence.objects.all()
    myFilter = AttendenceFilter(request.GET, queryset=attendences)
    attendences = myFilter.qs
    context = {'myFilter':myFilter, 'attendences': attendences, 'ta':False}
    return render(request, 'attendence_sys/attendence.html', context)


def facultyProfile(request):
    faculty = request.user.faculty
    form = FacultyForm(instance = faculty)
    context = {'form':form}
    return render(request, 'attendence_sys/facultyForm.html', context)



# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         ret,image = self.video.read()
#         ret,jpeg = cv2.imencode('.jpg',image)
#         return jpeg.tobytes()


# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield(b'--frame\r\n'
#         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @gzip.gzip_page
# def videoFeed(request):
#     try:
#         return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
#     except:
#         print("aborted")

# def getVideo(request):
#     return render(request, 'attendence_sys/videoFeed.html')