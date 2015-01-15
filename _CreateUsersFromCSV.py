#This sample shows how to read a CSV with usernames and create users in ArcGIS.com
#Simple fill in the username, password, and update the path to the CSV below

import ProLicense as pro
import os
import time

curDir = os.path.dirname(os.path.realpath(__file__)) 

username = '   '
password = '   '    
#This uses a sample file in the sampleCSV directory. Update the below path to your CSV file.
CSVFile  = os.path.join(curDir, "sampleCSV/usersPassword.csv") 

orgURL = 'http://www.arcgis.com/sharing/rest'

#CSV file of usernames, with passwords
users2Create = pro.readUserCSV(CSVFile)

CON = pro.ARCGIScom(username, password, orgURL) 

#Create the user
print("\nNow creating user accounts....\n")
createdUsers = CON.createUser(users2Create)

for user in createdUsers:
    print("{0} was created".format(user))

#Wait a second to ensure accounts are created in ArcGIS.com
time.sleep(2)

#Assign a license
print("\nAssigning those new users a Pro licenses as specified in the CSV\n")
for i in range(0, len(users2Create)):
    workingUser = users2Create[i]['Username']       
    entitlements = users2Create[i]['License']
    
    if workingUser in createdUsers:
        licResponse = CON.assignProPermissions(workingUser, entitlements.split(','))
        try:        
            if licResponse['success'] == True:
                print("{0} was assigned license: {1}".format(workingUser, entitlements))
        except:
            print(licResponse)             
    else:
        print("Not assigning a license for user {0}: they were not created in the portal".format(workingUser))
    
    
        
