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

        # print(result)
    
        json_data = dumps(result) # json string the list with dumps (Mongo ObjectId won't jsonify)

        # print(json_data)

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

        json_data_details = dumps(details_result)

        return jsonify({'details' : json_data_details})
    except Exception as e:
        return jsonify({'error' : e})
    
def fetchStudentDetails(client, student_id):
    # print("making call to db for student details with", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)

    result = client["m2m_math_db"]["students"].find_one({"_id" : student_id_obj})

    return result
    
@student_bp.route("/packets", methods=['POST'])
def studentPackets():
    data = request.get_json() # Get body of post request
    student_id = data.get("studentId")

    print(f"Fetching student {student_id} packets")

    try:
        client = get_client()

        # print(f"Here is the client: {client}")

        packets_result = fetchStudentPackets(client, student_id)
        submissions_result = getSubmissions(client, packets_result)

        for packet in packets_result:
            packet["submission_details"] = submissions_result[str(packet["_id"])]

        json_data_packets = dumps(packets_result)

        return jsonify({'packets' : json_data_packets})
    except Exception as e:
        return jsonify({'error' : e})
    
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

@student_bp.route("/submissions", methods=['POST'])
def studentSubmissions():
    data = request.get_json()
    student_id = data.get("studentId")

    print(f"Fetching student {student_id} submissions")

    try:
        client = get_client()

        # print(f"Here is the client: {client}")

        submission_results = fetchStudentSubmissions(client, student_id)

        json_data_submissions = dumps(submission_results)
        # print(json_data_submissions)

        return jsonify({'submissions' : json_data_submissions})
    except Exception as e:
        return jsonify({'error' : e})

def fetchStudentSubmissions(client, student_id):
    # print("Checking packets for student id: ", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    
    cursor = client["m2m_math_db"]["submissions"].find({"student_id" : student_id_obj})
    
    list_cur = list(cursor)
    return list_cur

@student_bp.route("/levels")
def getLevels():
    print(f"Fetching levels")
    try:
        client = get_client() # Get the client

        result = fetchLevels(client)

        # print(result)
    
        json_data = dumps(result) # json string the list with dumps (Mongo ObjectId won't jsonify)

        # print(json_data)

        return ({"levels" : json_data})
    
    except Exception as e:
        print(f"Levels fetching error: {e}")
        return jsonify({'error' : e})
    
def fetchLevels(client):
    cursor = client["m2m_math_db"]["levels"].find({})
    # convert mongo cursor to python list
    list_cur = list(cursor)
    return list_cur

@student_bp.route("/level/objectives", methods=['POST'])
def getLevelObjectives():
    data = request.get_json()
    level_id = data.get("levelId")

    print(f"Fetching levels")
    try:
        client = get_client() # Get the client

        result = fetchObjectives(client, level_id)

        # print(result)
    
        json_data = dumps(result) # json string the list with dumps (Mongo ObjectId won't jsonify)

        # print(json_data)

        return ({"objectives" : json_data})
    
    except Exception as e:
        print(f"Objectives fetching error: {e}")
        return jsonify({'error' : e})
    
def fetchObjectives(client, level_id):
    level_id_obj = ObjectId(level_id['$oid']) if isinstance(level_id, dict) else ObjectId(level_id)

    cursor = client["m2m_math_db"]["objectives"].find({"level_id" : level_id_obj})
    # convert mongo cursor to python list
    list_cur = list(cursor)
    return list_cur