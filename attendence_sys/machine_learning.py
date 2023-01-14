import numpy as np
import cv2
import sklearn
import pickle
import os
from django.conf import settings
import os

STATIC_DIR = settings.STATIC_DIR


# face detection
face_detector_model = cv2.dnn.readNetFromCaffe(os.path.join(STATIC_DIR,'models/deploy.prototxt.txt'),
                                               os.path.join(STATIC_DIR,'models/res10_300x300_ssd_iter_140000.caffemodel'))
# feature extraction
face_feature_model = cv2.dnn.readNetFromTorch(
    os.path.join(STATIC_DIR, 'models/openface.nn4.small2.v1.t7'))
# face recognition
face_recognition_model = pickle.load(open(os.path.join(STATIC_DIR, 'models/machinelearning_face_person_identity.pkl'),
                                          mode='rb'))
# emotion recognition model
# emotion_recognition_model = pickle.load(open(os.path.join(
#     STATIC_DIR, 'models/machinelearning_face_emotion.pkl'), mode='rb'))


def pipeline_model(img):
    #  pipeline model
#     img = cv2.imread(path)
#     img = np.array(path)
    image = img.copy()
    h,w = img.shape[:2]
    # face-detection
    img_blob = cv2.dnn.blobFromImage(img,1,(300,300),(104,177,123),swapRB=False,crop=False)
    face_detector_model.setInput(img_blob)
    detections = face_detector_model.forward()

    
    # machine result
    machinelearning_results = dict(face_detect_score =[],
                                   face_name=[],
                                   face_name_score=[],
#                                    emotion_name=[],
#                                    emotion_name_score=[],
                                   count=[])
    names=[]
    try:
        count=1
        if len(detections) > 0:
            for i,confidence in enumerate(detections[0,0,:,2]):
                if confidence > 0.5:
                    box = detections[0,0,i,3:7]*np.array([w,h,w,h])
                    startx,starty,endx,endy = box.astype(int)
                    cv2.rectangle(image,(startx,starty),(endx,endy),(0,255,0))

                    # Feature Extraction
                    face_roi = img[starty:endy,startx:endx]
                    face_blob = cv2.dnn.blobFromImage(face_roi,1/255,(96,96),(0,0,0),swapRB=True,crop=True)
                    face_feature_model.setInput(face_blob)
                    vectors = face_feature_model.forward()

                    #  predict with machine learning
                    face_name = face_recognition_model.predict(vectors)[0]
                    face_score = face_recognition_model.predict_proba(vectors).max()
                    # Emotion
#                     emotion_name = emotion_recognition_model.predict(vectors)
#                     emotion_score = emotion_recognition_model.predict_proba(vectors).max()


        #             print(face_name)
        #             print(face_score)
        #             print(emotion_name)
        #             print(emotion_score)

                    text_face = '{} : {:.0f}%'.format(face_name,100*face_score)
                    cv2.putText(image,text_face,(startx,starty),cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),2)
#                     text_emotion = '{} : {:.0f}%'.format(emotion_name,100*emotion_score)
#                     cv2.putText(image,text_emotion,(startx,endy),cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),2)



                    machinelearning_results['count'].append(count)
                    machinelearning_results['face_detect_score'].append(confidence)
                    machinelearning_results['face_name'].append(face_name)
                    names.append(face_name)
                    machinelearning_results['face_name_score'].append(face_score)
#                     machinelearning_results['emotion_name'].append(emotion_score)
#                     machinelearning_results['emotion_name_score'].append(emotion_score)

                    count+=1
    except:
        pass

#     return image
#     return image,machinelearning_results,names
    return image,names