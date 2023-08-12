# from flask import Flask, request

# app = Flask(__name__)

# @app.route('/', methods=['POST'])

# def receive_gsi_data():
#     if request.method == 'POST':
#         data = request.get_json()
#         if "round" in data:
#             print("Received GSI data:")
#             print(data)
#             return "Data received successfully.", 200
#         else:
#             print("Received data but round field is not present")
#             print(data)
#             return "data received, but....."
    
# if __name__=='__main__':
#     app.run(host='0.0.0.0', port=27015)

import socket

def is_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.close()
        return True
    except socket.error:
        return False
    
port = 27015
if is_port(port):
    print("Yes")
else:
    print("No")