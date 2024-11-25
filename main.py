# from fastapi import FastAPI, HTTPException
# import pandas as pd
# import requests
# from fastapi.middleware.cors import CORSMiddleware
# import firebase_admin
# from firebase_admin import credentials, firestore
# import os
# import json

# app = FastAPI()

# # تحميل بيانات اعتماد Firebase من متغير البيئة
# cred_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
# if cred_data:
#     cred_json = json.loads(cred_data)
#     cred = credentials.Certificate(cred_json)
#     firebase_admin.initialize_app(cred)
#     print("Firebase initialized successfully")
# else:
#     print("Error: GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable not set")

# # السماح بطلبات CORS
# origins = [
#     "http://localhost:8100",
#     "http://127.0.0.1:8100"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# API_KEY = os.getenv("API_KEY")
# school_location = (21.548888, 39.177222)  # موقع المدرسة

# @app.get("/")
# async def calculate_path(cluster_label: str = "Cluster 1"):
#     try:
#         db = firestore.client()
#         students_ref = db.collection("cluster").where("Final_Cluster", "==", cluster_label)
#         students_docs = students_ref.stream()

#         students_data = []
#         for doc in students_docs:
#             doc_data = doc.to_dict()
#             students_data.append({
#                 'name': doc_data.get('name', 'Unknown'),  # اسم الطالب
#                 'latitude': float(doc_data['lat']),
#                 'longitude': float(doc_data['lng'])
#             })

#         if len(students_data) == 0:
#             return {"error": "No students found in the specified cluster."}

#         data_frame = pd.DataFrame(students_data)

#         # تحويل المواقع إلى قائمة إحداثيات
#         student_locations = list(zip(data_frame['latitude'], data_frame['longitude']))
#         locations_with_school = [school_location] + student_locations + [school_location]

#         # حساب المسار
#         optimal_path = calculate_optimal_path(locations_with_school)

#         # إضافة أسماء الطلاب مع المسار
#         ordered_students = [
#             {
#                 "name": student["name"],
#                 "latitude": location[0],
#                 "longitude": location[1],
#             }
#             for student, location in zip(students_data, optimal_path[1:-1])  # استثناء المدرسة
#         ]

#         return {
#             "route": optimal_path,
#             "students": ordered_students
#         }

#     except Exception as e:
#         print("Error:", e)
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# def calculate_optimal_path(locations):
#     if len(locations) > 8:
#         raise HTTPException(status_code=400, detail="Too many locations provided.")

#     waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
#     start = f"{locations[0][0]},{locations[0][1]}"
#     end = start

#     url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&waypoints=optimize:true|{waypoints}&key={API_KEY}"
#     response = requests.get(url)
#     data = response.json()

#     if data["status"] != "OK":
#         error_message = data.get("error_message", "Unknown error")
#         raise HTTPException(status_code=500, detail=f"Google Maps API error: {error_message}")

#     ordered_student_locations = [(leg["start_location"]["lat"], leg["start_location"]["lng"]) for leg in data["routes"][0]["legs"]]
#     ordered_student_locations.append((locations[0][0], locations[0][1]))  # المدرسة كنهاية

#     if ordered_student_locations[0] == ordered_student_locations[-1]:
#         ordered_student_locations = ordered_student_locations[:-1]

#     return ordered_student_locations
from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import requests
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

app = FastAPI()

# تحميل بيانات اعتماد Firebase من متغير البيئة
cred_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if cred_data:
    cred_json = json.loads(cred_data)
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully")
else:
    print("Error: GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable not set")

# السماح بطلبات CORS
origins = [
    "http://localhost:8100",
    "http://127.0.0.1:8100"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY")
school_location = (21.548888, 39.177222)  # موقع المدرسة

@app.get("/")
async def calculate_path(
    cluster_label: str = "Cluster 1",
    start_lat: float = Query(..., description="Latitude of the start point"),
    start_lng: float = Query(..., description="Longitude of the start point"),
):
    try:
        db = firestore.client()
        students_ref = db.collection("cluster").where("Final_Cluster", "==", cluster_label)
        students_docs = students_ref.stream()

        students_data = []
        for doc in students_docs:
            doc_data = doc.to_dict()
             # تحقق من أن الإحداثيات موجودة وصحيحة
            if 'lat' in doc_data and 'lng' in doc_data and doc_data['lat'] is not None and doc_data['lng'] is not None:
                students_data.append({
                    'name': doc_data.get('name', 'Unknown'),  # اسم الطالب
                    'latitude': float(doc_data['lat']),
                    'longitude': float(doc_data['lng'])
                })
            else:
                print(f"Skipping student with missing or invalid coordinates: {doc_data}")

        if len(students_data) == 0:
            return {"error": "No students found in the specified cluster."}

        data_frame = pd.DataFrame(students_data)

        # تحويل المواقع إلى قائمة إحداثيات
        student_locations = list(zip(data_frame['latitude'], data_frame['longitude']))
        locations_with_school = [(start_lat, start_lng)] + student_locations + [school_location]

        # حساب المسار
        optimal_path = calculate_optimal_path(locations_with_school)

        # إضافة أسماء الطلاب مع المسار
        ordered_students = [
            {
                "name": student["name"],
                "latitude": location[0],
                "longitude": location[1],
            }
            for student, location in zip(students_data, optimal_path[1:-1])  # استثناء المدرسة
        ]

        return {
            "route": optimal_path,
            "students": ordered_students
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def calculate_optimal_path(locations):
    if len(locations) > 8:
        raise HTTPException(status_code=400, detail="Too many locations provided.")

    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
    start = f"{locations[0][0]},{locations[0][1]}"
    end = f"{school_location[0]},{school_location[1]}"  # المدرسة كوجهة نهائية

    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&waypoints=optimize:true|{waypoints}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        error_message = data.get("error_message", "Unknown error")
        raise HTTPException(status_code=500, detail=f"Google Maps API error: {error_message}")

    ordered_student_locations = [(leg["start_location"]["lat"], leg["start_location"]["lng"]) for leg in data["routes"][0]["legs"]]
    ordered_student_locations.append((school_location[0], school_location[1]))  # المدرسة كنهاية

    return ordered_student_locations
