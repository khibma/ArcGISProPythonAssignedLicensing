import ProLicense as pro
import os


if __name__ == "__main__": 
    
    #Provide credentials for an administrative portal (arcgis.com) user here:
    username = '   '
    password = '   '    
    orgURL = 'http://www.arcgis.com/sharing/rest'
    
    #These will be loaded up dictionaries
    curDir = os.path.dirname(os.path.realpath(__file__))    
    userWpass = pro.readUserCSV(os.path.join(curDir, "sampleCSV/usersPassword.csv"))  #If password: CREATE user
    usersNoPass = pro.readUserCSV(os.path.join(curDir, "sampleCSV/users.csv") ) #If NO password, invite them.
    #print (usersNoPass)
    
    # Fire up the handler and populate settings.    
    CON = pro.ARCGIScom(username, password, orgURL) 
    
    print("Org:  {0} (id:{1})".format(CON.OrgTitle, CON.orgID))
    print("Admin User:   {0} {1}".format(CON.adminFName, CON.adminLName))
    print("Admin Email:  {0}".format(CON.adminEmail))
    print("Portal:       {0}".format(CON.PortalURL))
   
    print ("\n  Org info...")         
    for k, v in CON.orgProvision.items():
        if k != "orgEntitlements":
            if k == 'modified' or k == 'startDate' or k == 'created' or k == 'endDate':
                v = pro.convertTime(v)
            print ("{0} : {1}".format(k, v))    
    
    print ("\nEntitled license counts...")        
    for k, v in CON.orgEntitlements['entitlements'].items():
        print ("{0} : {1}".format(k, v['num']))
        
    
    #Display some users and their license info    
    print ("\n  Found {0} user accounts....".format(CON.AllUserCount))
    for i, allUserVal in enumerate(CON.AllUser['users']): 
        for k, v in allUserVal.items():
            if k == 'username':  name = v
            if k == 'lastLogin':  lastlogin = pro.convertTime(v)
            if k == 'entitlements':  license = v
            if k == 'disconnected':  offline = "YES" if v == True else "NO"
        print("{0} is entitled to: {1}. Last active: {2} | Checked-out:{3}".format(name, license, lastlogin, offline))
    
    userNameTest = "BillyBob"
    print("\nCan I make this user name?   {0}".format(userNameTest))
    userCheck = CON.checkUser(userNameTest)
    if userCheck == userNameTest:
        print("Because the user name was ok, we'd proceed with it. But this is only a demo, not going to make {0}".format(userCheck))
    else:
        print("Because the user name is taken, we'd use the new one, {0}, but this is a demo, so wont use that".format(userCheck))

    print("\nNow lets try to invite some users....\n")
    goodInvites = CON.createUser(usersNoPass)
    print("\nNow lets just make new users straight up\n")
    goodCreates = CON.createUser(userWpass)    
  
    print("\nAssign those INVITED users Pro licenses....\n")    
    for i in range(0, len(usersNoPass)):
        workingUser = usersNoPass[i]['Username']            
        licResponse = CON.assignProPermissions(workingUser, [usersNoPass[i]['License']])
        print(licResponse)
        
    
    print("\nAssign those CREATED users Pro licenses....\n")
    for i in range(0, len(userWpass)):
        workingUser = userWpass[i]['Username']            
        licResponse = CON.assignProPermissions(workingUser, [userWpass[i]['License']])
        print(licResponse)
