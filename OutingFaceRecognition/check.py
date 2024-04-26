import face_recognition
import numpy as np
import pandas as pd
f=pd.read_csv('facedata.csv')
# Assuming all_img_encoding is a list where you want to store image encodings
my= face_recognition.load_image_file("sri1.jpg")
mye=face_recognition.face_encodings(my)[0]
# thiru= face_recognition.load_image_file("./E-2/200999.jpg")
# thirue=encoding = face_recognition.face_encodings(thiru)[0]

# sri= face_recognition.load_image_file("./E-2/200997.jpg")
# srie=encoding = face_recognition.face_encodings(sri)[0]

t=np.array(f)
results = face_recognition.face_distance(t,mye)
print(np.where(results==np.min(results)))   
# print(np.count_nonzero(results==np.min(results)))
# results = list(results)
# print(results)