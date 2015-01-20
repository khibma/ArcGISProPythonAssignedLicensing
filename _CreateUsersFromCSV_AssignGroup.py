#This sample shows how to read a CSV with usernames and create users in ArcGIS.com
#Simple fill in the username, password, and update the path to the CSV below

import ProLicense as pro
import os
import time

curDir = os.path.dirname(os.path.realpath(__file__)) 

username = '   '
password = '   '
groupTitle = "TestGroup"
groupDescription = "This is a description of a test group"
groupSnippet = "This is the snippet, a quick description"
groupTags = "Pro, license, GroupZ"

#This uses a sample file in the sampleCSV directory. Update the below path to your CSV file.
CSVFile  = os.path.join(curDir, "sampleCSV/usersPassword.csv") 

orgURL = 'http://www.arcgis.com/sharing/rest'

#CSV file of usernames, with passwords
users2Create = pro.readUserCSV(CSVFile)

CON = pro.ARCGIScom(username, password, orgURL) 

#Create the user
print("\nNow creating user accounts....\n")
createdUsers = CON.createUser(users2Create)

#Create the group and get the ID
groupResp = CON.createGroup(groupTitle, groupDescription, groupSnippet, groupTags)
groupID = groupResp['group']['id']

#Add the users to the group
addedUserResp = CON.addUserToGroup(groupID, createdUsers)
for user in addedUserResp['notAdded']:
    print("{0} was not added to the group. Investigate this user manually.".format(user))

#Assign the same license to all users.
for user in createdUsers:
    print("\n{0} was created. Please select their license level".format(user))    
    
    licLevel = ""
    while True:        
        print("A - Advanced")
        print("S - Standard")
        print("B - Basic")
        print("N - no license will be set")
        licLevel = input("[A|S|B|N]  ")
        if licLevel in ['A', 'S', 'B', 'N']:  break
        else: print("\nSelect a valid input.")  
    if licLevel == 'N': 
        print("No license set for {0}".format(user))
        continue
    
    extLics = []
    extensions = 0    
    print("\nExtensions")
    print("1 - Spatial Analyst")
    print("2 - 3D Analyst")
    print("3 - Network Analyst")
    print("4 - Geostatistical Analyst")
    print("5 - Data Reviewer")
    print("6 - Workflow Manager")
    cExtensions = input("<123456> or enter for none  ") 
    if ' ' in cExtensions: cExtensions = cExtensions.replace(' ', '') #remove spaces if they were added
    if ',' in cExtensions: cExtensions = cExtensions.replace(',', '') #remove commas if they were added
       
    if len(tuple(cExtensions)) == 1:
        extLics.append(pro.licenseLookup[cExtensions])
    else:    
        for ext in tuple(cExtensions):
            extLics.append(pro.licenseLookup[ext])

    entitlements = [pro.licenseLookup[licLevel]] + extLics    
    
    licResponse = CON.assignProPermissions(user, entitlements)

    try:        
        if licResponse['success'] == True:
            print("{0} was assigned license: {1}".format(user, entitlements))
    except:
        print(licResponse)             
    
    
