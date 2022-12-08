import base64
import json                    
import requests

for i in range(100):
    api = 'http://localhost/get_min_shops'
    image_file = 'SampleReciept1.png'

    with open(image_file, "rb") as f:
        im_bytes = f.read()        
    im_b64 = base64.b64encode(im_bytes).decode("utf8")

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
    payload = json.dumps({"image": im_b64, "email_id": "muka4041@colorado.edu"})
    response = requests.post(api, data=payload, headers=headers)
    try:
        data = response.json()     
        print(data)                
    except requests.exceptions.RequestException:
        print(response.text)

# api = 'http://localhost/sql'

# headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# cmd = 'delete'

# if cmd == 'insert':

#     sql = f'INSERT INTO data VALUES (%s, %s, %s, %s, %s)'

#     val = [
#         ('hello1', 'tablet', 12.0, 2, 'pharmacy_98'),
#         ('world2', 'syrup', 12.0, 12, 'pharmacy_99'),
#         ('howdy3', 'leaves', 120.0, 20, 'pharmacy_99'),
#     ]

# elif cmd  == 'update':

#     sql = f'UPDATE data SET medicine = %s WHERE medicine = %s AND pharmacy_name = %s'

#     val = [
#         ('med_new_1', 'hello1', 'pharmacy_98'),
#         ('med_new_2', 'world2', 'pharmacy_99'),
#         ('med_new_3', 'howdy3', 'pharmacy_99'),
#     ]

# elif cmd  == 'delete':

#     sql = f'DELETE FROM data WHERE medicine = %s AND pharmacy_name = %s'

#     val = [
#         ("med_new_1", "pharmacy_98"),
#         ("med_new_2", "pharmacy_99"),
#         ("med_new_3", "pharmacy_99"),
#     ]
  
# payload = json.dumps({"sql": sql, "val": val})
# response = requests.post(api, data=payload, headers=headers)
# try:
#     data = response.json()     
#     print(data)                
# except requests.exceptions.RequestException:
#     print(response.text)