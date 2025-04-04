from flask import Blueprint, jsonify, request

from bson.json_util import dumps
from bson.objectid import ObjectId

from backend.db import get_client

# Create a blueprint
student_bp = Blueprint('student', __name__)

# Get all students
@student_bp.route("/all")
def students():
    print("Fetching students")
    try:
        client = get_client() # Get the client

        result = fetchStudents(client)
    
        json_data = dumps(result) # json string the list with dumps (Mongo ObjectId won't jsonify)

        return json_data
    
    except Exception as e:
        print(f"Student fetching error: {e}")
        return jsonify({'error' : e})
    
def fetchStudents(client):
    cursor = client["m2m_math_db"]["students"].find({})
    # convert mongo cursor to python list
    list_cur = list(cursor)
    return list_cur

# Get student details, packets, and submissions

@student_bp.route("/details", methods=['POST'])
def studentDetails():

    data = request.get_json() # Get body of post request
    student_id = data.get("studentId")

    print(f"Fetching student {student_id} details")

    try:
        client = get_client()

        # print(f"Here is the client: {client}")

        details_result = fetchStudentDetails(client, student_id)
        packets_result = fetchStudentPackets(client, student_id)
        submissions_result = getSubmissions(client, packets_result)

        for packet in packets_result:
            packet["submission_details"] = submissions_result[str(packet["_id"])]

        json_data_details = dumps(details_result)
        json_data_packets = dumps(packets_result)

        return jsonify({'result' : json_data_details, 'packets' : json_data_packets})
    except Exception as e:
        return jsonify({'error' : e})
    
def fetchStudentDetails(client, student_id):
    # print("making call to db for student details with", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)

    result = client["m2m_math_db"]["students"].find_one({"_id" : student_id_obj})

    return result

def fetchStudentPackets(client, student_id):
    # print("Checking packets for student id: ", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    
    cursor = client["m2m_math_db"]["packets"].find({"student_id" : student_id_obj})
    
    list_cur = list(cursor)
    return list_cur

def getSubmissions(client, packets):
    packets_dict = {}
    for packet in packets:
        submissions = packet["submissions"]
        submissions_list = []
        for submission in submissions:
            result = client["m2m_math_db"]["submissions"].find_one({"_id" : submission})
            submissions_list += [[result["datetime"], result["score"]]]
        packets_dict[str(packet["_id"])] = submissions_list

    return packets_dict
