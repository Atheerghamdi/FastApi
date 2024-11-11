
# from fastapi import FastAPI, HTTPException
# import mysql.connector
# import pandas as pd
# import requests
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # السماح بطلبات CORS من localhost:8101
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

# API_KEY = 'AIzaSyCMSB58R5jEPTFXpiEvhMOlM03YQBnweU4'
# CLUSTER_LABEL = "Cluster 2"

# @app.get("/calculate-path")
# async def calculate_path(cluster_label: str = "Cluster 2"):
#     try:
#         # تحقق من الاتصال بقاعدة البيانات
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="root",
#             database="locations"
#         )
#         query = f"SELECT latitude, longitude FROM EX WHERE cluster_label = '{CLUSTER_LABEL}'"
#         data_frame = pd.read_sql(query, connection)
#         connection.close()

#         # تحقق من عدد الطلاب
#         if len(data_frame) != 8:
#             return {"error": "Expected 8 students in the specified cluster, but got a different count."}

#         # تحويل مواقع الطلاب إلى قائمة من الإحداثيات
#         student_locations = list(zip(data_frame['latitude'], data_frame['longitude']))
#         optimal_path = calculate_optimal_path(student_locations)

#         return {"route": optimal_path}

#     except mysql.connector.Error as err:
#         print("Database connection error:", err)
#         raise HTTPException(status_code=500, detail=f"Database connection error: {err}")
#     except Exception as e:
#         print("Error:", e)
#         raise HTTPException(status_code=500, detail="An error occurred")

# def calculate_optimal_path(locations):
#     if len(locations) > 8:
#         raise HTTPException(status_code=400, detail="Too many locations provided.")

#     waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
#     start = f"{locations[0][0]},{locations[0][1]}"
#     end = f"{locations[-1][0]},{locations[-1][1]}"

#     url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&waypoints=optimize:true|{waypoints}&key={API_KEY}"
#     response = requests.get(url)
#     data = response.json()

#     if data["status"] != "OK":
#         print("Google Maps API error:", data["status"])
#         raise HTTPException(status_code=500, detail="Error from Google Maps API")

#     ordered_student_locations = [(leg["start_location"]["lat"], leg["start_location"]["lng"]) for leg in data["routes"][0]["legs"]]
#     return ordered_student_locations
# import os
# from fastapi import FastAPI, HTTPException
# import mysql.connector
# import pandas as pd
# import requests
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # السماح بطلبات CORS من localhost:8101
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

# API_KEY = 'AIzaSyCMSB58R5jEPTFXpiEvhMOlM03YQBnweU4'

# @app.get("/calculate-path")
# async def calculate_path(cluster_label: str = "Cluster 2"):
#     try:
#         # جلب بيانات الاتصال بقاعدة البيانات من متغيرات البيئة
#         db_host = os.getenv("DB_HOST", "localhost")
#         db_user = os.getenv("DB_USER", "root")
#         db_password = os.getenv("DB_PASSWORD", "root")
#         db_name = os.getenv("DB_NAME", "locations")

#         connection = mysql.connector.connect(
#             host=db_host,
#             user=db_user,
#             password=db_password,
#             database=db_name
#         )
#         query = f"SELECT latitude, longitude FROM EX WHERE cluster_label = %s"
#         data_frame = pd.read_sql(query, connection, params=(cluster_label,))
#         connection.close()

#         if len(data_frame) != 8:
#             return {"error": "Expected 8 students in the specified cluster, but got a different count."}

#         student_locations = list(zip(data_frame['latitude'], data_frame['longitude']))
#         optimal_path = calculate_optimal_path(student_locations)

#         return {"route": optimal_path}

#     except mysql.connector.Error as err:
#         raise HTTPException(status_code=500, detail=f"Database connection error: {err}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An error occurred")

# def calculate_optimal_path(locations):
#     if len(locations) > 8:
#         raise HTTPException(status_code=400, detail="Too many locations provided.")

#     waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
#     start = f"{locations[0][0]},{locations[0][1]}"
#     end = f"{locations[-1][0]},{locations[-1][1]}"

#     url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&waypoints=optimize:true|{waypoints}&key={API_KEY}"
#     response = requests.get(url)
#     data = response.json()

#     if data["status"] != "OK":
#         raise HTTPException(status_code=500, detail="Error from Google Maps API")

#     ordered_student_locations = [(leg["start_location"]["lat"], leg["start_location"]["lng"]) for leg in data["routes"][0]["legs"]]
#     return ordered_student_locations
from fastapi import FastAPI, HTTPException
import mysql.connector
import pandas as pd
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for the specified origins
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

API_KEY = 'AIzaSyCMSB58R5jEPTFXpiEvhMOlM03YQBnweU4'  # replace with your actual API key
CLUSTER_LABEL = "Cluster 2"

@app.get("/calculate-path")
async def calculate_path(cluster_label: str = "Cluster 2"):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="locations"
        )
        query = f"SELECT latitude, longitude FROM EX WHERE cluster_label = '{CLUSTER_LABEL}'"
        data_frame = pd.read_sql(query, connection)
        connection.close()

        # Verify number of students
        if len(data_frame) != 8:
            return {"error": "Expected 8 students in the specified cluster, but got a different count."}

        # Convert student locations to list of coordinates
        student_locations = list(zip(data_frame['latitude'], data_frame['longitude']))
        optimal_path = calculate_optimal_path(student_locations)

        return {"route": optimal_path}

    except mysql.connector.Error as err:
        print("Database connection error:", err)
        raise HTTPException(status_code=500, detail=f"Database connection error: {err}")
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="An error occurred")

def calculate_optimal_path(locations):
    if len(locations) > 8:
        raise HTTPException(status_code=400, detail="Too many locations provided.")

    waypoints = '|'.join([f"{lat},{lng}" for lat, lng in locations[1:-1]])
    start = f"{locations[0][0]},{locations[0][1]}"
    end = f"{locations[-1][0]},{locations[-1][1]}"

    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&waypoints=optimize:true|{waypoints}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        print("Google Maps API error:", data["status"])
        raise HTTPException(status_code=500, detail="Error from Google Maps API")

    ordered_student_locations = [(leg["start_location"]["lat"], leg["start_location"]["lng"]) for leg in data["routes"][0]["legs"]]
    return ordered_student_locations
