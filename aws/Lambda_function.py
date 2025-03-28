import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error

print('Loading function')

rekognition = boto3.client('rekognition')
s3 = boto3.resource("s3")


# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_text(bucket, key):
    response = rekognition.detect_text(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    count = len(response['TextDetections'])
    textDetections=response['TextDetections']
    finalResponse =[]
    for text in textDetections:
        textResponse={}
        textResponse = {'Detected text' : text['DetectedText'],
        'Confidence':"{:.2f}".format(text['Confidence']) + "%",
        'Id': '{}'.format(text['Id']),
        'Bounding Polygons':text['Geometry']['Polygon']
        }
        finalResponse.append(textResponse)
    return finalResponse




def SaveFileToS3(bucket,key,fileName,imageData):
    s3Object = s3.Object(bucket,key+fileName+".json")
    
    s3Object.put(
      Body =  (bytes(json.dumps(imageData).encode("UTF-8"))),
      ContentType='application/json'
        )
    # encoded_Json = imageData.encode=("utf-8")
    # s3.Bucket(bucket).put_object(key=key,Body= encoded_Json)
    return {
        'statusCode': 200,
        'body': json.dumps('file is created in:'+key+fileName+".json")
        }
def lambda_handler(event, context):
    
    
    bucket = 'ocr-image-dataset'
    key = 'Google-Street-View-Data/'
    writekey = 'Google-Street-View-Data-Result-Text/'
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        fileName = event['Records'][0]['body']
        print(fileName)
        image = detect_text(bucket,key+fileName) 
        if image is not None:
            fileNameWithoutExt = fileName.split('.')[0]
            fileSaved = SaveFileToS3(bucket,writekey,fileNameWithoutExt,image)
            print(fileSaved)
            
            return fileSaved
       
        else:
            print(fileName)
            return "Image not found on Location: "+bucket+'/'+key+'/'+fileName

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
