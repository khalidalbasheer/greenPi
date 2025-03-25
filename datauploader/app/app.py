from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, auth, initialize_app 

app = Flask(__name__)

cred = credentials.Certificate('serviceAccountKey.json')
default_app = initialize_app(cred)
db = firestore.client()
list_ref = db.collection('nodes_list')
data_ref = db.collection('nodes_data')

def authenticate_user(email, password):
    try:
        user = auth.get_user_by_email(email='kh.moharib@gmail.com')
        print(f'Authenticated user: {user.uid}')
        return user.uid
    except Exception as e:
        print(f'Error authenticating user: {e}')
        return None

@app.route('/', methods=['GET'])
def is_work():
    return 'The process work'

@app.route('/send', methods=['POST'])
def add():
    try:
        content = request.json
        data = {'node_name':content['node_name'],'moisture':content['moisture'],'rain':content['rain'],'temprature':content['temprature'],'humidity':content['humidity'],'battery_level':content['battery_level'],'d_date':content['d_date']}
        data_ref.document().set(data)
        list_ref.document(content['node_name']).set(data)
        return jsonify({"Success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)
    authenticate_user()
