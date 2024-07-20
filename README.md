# The Drug Dealer - An Electronic Assistant for Prescription Drugs

## Overview & Goals
The project aims to simplify the process of purchasing prescription medicines by creating a distributed, scalable service that helps patients find necessary medicines without multiple trips to different pharmacies. The service requires patients to upload their prescriptions, extracts the medicine list using OCR, checks the availability of these medicines across various pharmacies in a database, and provides the patient with the optimal number of pharmacies to visit.

## Components
<li> Google Cloud Vision API: For OCR processing of prescription images. <br>
<li> REST API: For handling client requests. <br>
<li> Kubernetes: For deploying and managing containers. <br>
<li> MySQL: For storing pharmacy inventory data. <br>
<li> Min.io: For storing prescription images. <br>
<li> Redis: For queue management. <br>
<li> SendGrid API: For sending email notifications to clients. <br>

## Architecture & Implementation
<li> Client Request Handling: A REST API receives the prescription image and patient email. <br>
<li> Image Processing: The prescription image is uploaded to Min.io and its hash is added to a Redis queue. <br>
<li> Worker Processing: A worker pod retrieves the image from Min.io, uses Google Vision API to extract medicine names, and queries MySQL for medicine availability in pharmacies. <br>
<li> Output Generation: The optimal list of pharmacies is generated and emailed to the patient using SendGrid. <br>

## Debugging & Testing
<li> REST Server: Tested with Flask application locally. <br>
<li> MySQL: Tested queries locally with SQLite and within the Kubernetes cluster. <br>
<li> Worker: Tested by SSHing into containers. <br>
<li> Redis & Min.io: Tested with port-forwarding and logs. <br>
<li> Google Vision API & SendGrid API: Verified locally before container deployment. <br>

## Scalability
Implemented horizontal pod autoscaling for workers to handle variable loads efficiently, with testing indicating the system can handle significant simultaneous requests.

## Future Enhancements
<li> Incorporate patient location to find nearby pharmacies. <br>
<li> Optimize for medicine cost variations across pharmacies. <br><br>
This project provides a foundation for a service that can greatly ease the process of obtaining prescription drugs, with potential for further enhancement to improve accuracy and cost-effectiveness.<br>

## Links
[Project Report](https://github.com/mukundkalantri23/drug-dealer-project/blob/main/DrugDealer-Final%20Project%20Report.pdf)<br>
[Demo Video](https://youtu.be/H7XsY34ja_I)<br>
  
## Team Members
Mukund Kalantri, Medha Rudra, Sai Divya Sivani Pragadaraju
