from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app 

app = Flask(__name__)

cred = credentials.Certificate('serviceAccountKey.json')
default_app = initialize_app(cred)
db = firestore.client()
list_ref = db.collection('nodes_list')
data_ref = db.collection('nodes_data')

@app.route('/', methods=['GET'])
def is_work():
    return 'The process work'

@app.route('/send', methods=['POST'])
def add():
    try:
        content = request.json
        data = {'node_name':content['node_name'],'moisture':content['moisture'],'temprature':content['temprature'],'humidity':content['humidity'],'battery_level':content['battery_level'],'d_date':content['d_date']}
        data_ref.document().set(data)
        list_ref.document(content['node_name']).set(data)
        return jsonify({"Success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"


# @app.route('/send', methods=['GET','POST', 'PUT'])
# def add():
#     try:
#         node_name = request.args['node_name']
#         moisture = int(request.args['moisture'])
#         temprature = int(request.args['temprature'])
#         humidity = int(request.args['humidity'])
#         battery_level = int(request.args['battery_level'])
#         data = {'node_name':node_name,'moisture':moisture,'temprature':temprature,'humidity':humidity,'battery_level':battery_level}
#         db_ref.document().set(data)
#         db_ref.document(node_name).update(data)
#         return jsonify({"Success": True}), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"


# @app.route('/update', methods=['GET','PUT'])
# def update():
#     try:
#         node_name = request.args['node_name']
#         moisture = int(request.args['moisture'])
#         temprature = int(request.args['temprature'])
#         humidity = int(request.args['humidity'])
#         battery_level = int(request.args['battery_level'])
#         data = {'node_name':node_name,'moisture':moisture,'temprature':temprature,'humidity':humidity,'battery_level':battery_level}
#         db_ref.document(node_name).update(data)
#         return jsonify({"Success": True}), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)
