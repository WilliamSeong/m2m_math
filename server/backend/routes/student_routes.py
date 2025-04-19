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

        return json_data_details
    except Exception as e:
        return jsonify({'error' : e})
    
def fetchStudentDetails(client, student_id):
    # print("making call to db for student details with", student_id)
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)

    result = client["m2m_math_db"]["students"].find_one({"_id" : student_id_obj})

    return result

@student_bp.route("/objectives", methods=['POST'])
def getObjectivesList():
    data = request.get_json()
    objective_list = data.get("objectiveIds")
    # print(objective_list)
    try:
        client = get_client()
        objectives = fetchObjectivesList(client, objective_list)
        json_objectives = dumps(objectives)
        return json_objectives
    except Exception as e:
        return jsonify({'error' : e})
    
def fetchObjectivesList(client, objective_list):
    # print(objective_list)
    object_id_list = [ObjectId(id) for id in objective_list]
    cursor = client["m2m_math_db"]["objectives"].find({"_id" : {"$in" : object_id_list}})

    list_cur = list(cursor)
    return list_cur

    
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

@student_bp.route("/objectives/add", methods=['POST'])
def addObjectivesInprogress():
    data = request.get_json()
    objective_ids = data.get("objectiveIds")
    student_id = data.get("studentId")
    
    try:
        client = get_client() # Get the client

        addObjectives(client, student_id, objective_ids)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Objectives adding error: {e}")
        return jsonify({'error' : e})

def addObjectives(client, student_id, objective_ids):
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    for id in objective_ids:
        client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$set" : {f"objectives_inprogress.{id}" : True}})

@student_bp.route("/objectives/complete", methods=['POST'])
def completeObjectivesInprogress():
    data = request.get_json()
    objective_id = data.get("objectiveId")
    student_id = data.get("studentId")
    
    try:
        client = get_client() # Get the client

        completeObjective(client, student_id, objective_id)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Objectives adding error: {e}")
        return jsonify({'error' : e})

def completeObjective(client, student_id, objective_ids):
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    # client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$unset" : {f"objectives_inprogress.{objective_ids}" : True}})
    client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$set" : {f"objectives_complete.{objective_ids}" : True}})

@student_bp.route("/objectives/incomplete", methods=['POST'])
def incompleteObjectivesInprogress():
    data = request.get_json()
    objective_id = data.get("objectiveId")
    student_id = data.get("studentId")
    
    try:
        client = get_client() # Get the client

        incompleteObjective(client, student_id, objective_id)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Objectives adding error: {e}")
        return jsonify({'error' : e})

def incompleteObjective(client, student_id, objective_ids):
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$unset" : {f"objectives_complete.{objective_ids}" : True}})
    client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$set" : {f"objectives_inprogress.{objective_ids}" : True}})

@student_bp.route("/objectives/remove", methods=['POST'])
def removeInprogressObjective():
    data = request.get_json()
    objective_id = data.get("objectiveId")
    student_id = data.get("studentId")

    # print(f"Removing {objective_id}")
    
    try:
        client = get_client() # Get the client

        removeObjective(client, student_id, objective_id)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Objectives adding error: {e}")
        return jsonify({'error' : e})

def removeObjective(client, student_id, objective_ids):
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$unset" : {f"objectives_inprogress.{objective_ids}" : True}})

@student_bp.route("/packet/remove", methods=['POST'])
def removePacket():
    data = request.get_json()
    packet_id = data.get("packetId")
    student_id = data.get("studentId")

    # print(f"Removing {packet_id}")
    
    try:
        client = get_client() # Get the client

        removePacket(client, student_id, packet_id)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Objectives adding error: {e}")
        return jsonify({'error' : e})

def removePacket(client, student_id, packet_id):
    student_id_obj = ObjectId(student_id['$oid']) if isinstance(student_id, dict) else ObjectId(student_id)
    client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$unset" : {f"packets_inprogress.{packet_id}" : True}})
    client["m2m_math_db"]["students"].update_one({"_id" : student_id_obj}, {"$set" : {f"packets_complete.{packet_id}" : True}})
