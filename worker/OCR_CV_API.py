from google.cloud import vision
import os

path= 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=path

def text_detection(cont):
  
  client = vision.ImageAnnotatorClient()
  response = client.text_detection({'content' :cont})
  
  if response.error.message:
    raise Exception(f"check the website for {response.error.message}")
  
  return response

def img_txt(img):
  
  with open(img,'rb') as img_file:
    content=img_file.read()
  
  resp= text_detection(content)
  
  texts= resp.text_annotations
  lis = texts[0].description.split('\n')
  
  keys= lis[lis.index('Medicine Name')+1: lis.index('Quantity')]
  val= lis[lis.index('Quantity')+1: lis.index('Signature')]
  val = [int(x) for x in val]
  reciept_data =dict(zip(keys,val))
  
  return reciept_data

reciept_data = img_txt("SampleReciept1.png")
print(reciept_data)

