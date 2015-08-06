import os, sys
import json
import time
import csv
import urllib.parse as parse
import urllib.request as request
import http.client as client

#Force connections to the previous HTTP 1.0 standard as this is faster with chunked responses, which is typically what you'll get
client.HTTPConnection._http_vsn= 10
client.HTTPConnection._http_vsn_str='HTTP/1.0'

licenseLookup = {"A" : 'desktopAdvN',
                 "S" : 'desktopStdN',
                 "B" : 'desktopBasicN',
                 "1" : 'spatialAnalystN',
                 "2" : '3DAnalystN',
                 "3" : 'networkAnalystN',
                 "4" : 'geostatAnalystN',
                 "5" : 'dataReviewerN',
                 "6" : 'workflowMgrN' }

class ARCGIScom(object):
    
    def __init__(self, username, password, orgURL):
        now = time.time()
        self.username = username
        self.password = password
        if "/sharing/rest" not in orgURL: orgURL += "/sharing/rest"        
        self.ORGURL = orgURL                
        self.LocalPortal = True if '7443' in orgURL else False   #TO-DO, may need to revist this logic        
        
        self.token, self.expires, self.referer = self.getToken(username, password, orgURL)  
        self.OrgTitle, self.PortalURL = self.getPortalInfo()
        self.adminEmail, self.adminFName, self.adminLName, self.orgID = self.getAdminUserInfo()
        self.IdentityStoreType = self.getIdentityStore() if self.LocalPortal else "arcgiscom"                  
        self.orgEntitlements, self.orgProvision, self.ProID = self.getOrgProvision()
        self.LicensedUser, self.AllUser = self.getUserLicenseInfo()                        
        self.LicensedUserCount = len(self.LicensedUser['userEntitlements'])
        self.AllUserCount = len(self.AllUser['users'])        
        self.license = self.setLicenseCounts()
                
        print("<<<TOTAL TIME to make requests: {0}>>>\n".format(time.time()-now))

      
    def getToken(self, username, password, orgURL, exp=60):  #expires in 60minutes
        """Generates a token."""
        
        #TOKENURL = "https://www.arcgis.com/sharing/rest/generateToken"
        if "https" not in orgURL:
            orgURL = orgURL.replace("http", "https")
        TOKENURL = orgURL + "/generateToken"        
        
        if "arcgis.com" in orgURL:  referer = "http://www.arcgis.com/" 
        else:              
            referer = orgURL[:orgURL.rfind(":",2)]  #eg. 'https://server.domain.com'
            
        tokenParams = {'username' : username,
                       'password' : password,
                       'client' : 'referer',
                       'referer' : referer,
                       'f' : 'json' } 
        
        token = sendReq(TOKENURL, tokenParams)

        if "token" not in token:
            print(token['error'])
            sys.exit()
        else:
            return token['token'], token['expires'], referer
        
        
    def getOrgProvision(self):
        """Get basic information about the org from the user assigned to it"""
        
        orgURL = self.ORGURL + '/portals/self/purchases'        
        
        orgReqParms = {'token': self.token,
                       'f' :'json' } 
        
        orgData = sendReq(orgURL, orgReqParms)        
        
        try:
            purchaseNum = len(orgData['purchases'])
        except: #If user is not an admin it will error, display that error msg.
            print ("You do not appear to be an admin for any Orgs. Goodbye.")
            sys.exit()
            
        if purchaseNum < 1:
            print("User does not appear to have any valid licenses. Goodbye")
            sys.exit()
        else:
            for i, val in enumerate(orgData['purchases']):  
                try:
                    if val['listing']['title'] == 'ArcGIS Pro':
                        orgEntitlment = val['provision']['orgEntitlements']
                        orgProvision = val['provision']  
                        proID = val['provision']['itemId']
                        return orgEntitlment, orgProvision, proID
                except:
                    continue
    
    def getAdminUserInfo(self):
        """Collect details on the admin user"""
        
        orgURL = self.ORGURL + '/community/self'        
        
        orgReqParms = {'token': self.token,
                       'f' :'json' } 
        
        orgData = sendReq(orgURL, orgReqParms)
        try:
            firstName = orgData['firstName']
            lastName =  orgData['lastName']
        except KeyError:
            firstName = ' '
            lastName = ' '
        
        return orgData['email'], firstName, lastName, orgData['orgId']
    
    def getPortalInfo(self):
        """Portal name and URL"""
        
        orgURL = self.ORGURL + '/portals/self'        
        
        portalParms = {'token': self.token,
                       'f' :'json' } 
        #There is a lot of data in here, but we only want the org title.
        portalData = sendReq(orgURL, portalParms) 
        try:
            portalURL = "http://" + portalData['urlKey'] + "." + portalData['customBaseUrl']
        except KeyError:
            portalURL = "https://" + portalData['portalLocalHostname']            
        
        return portalData['name'], portalURL

    def getUserLicenseInfo(self):        
        """Get active users with license assignments"""
        
        licensedUserDict = {'token': self.token,
                           'f' :'json' } 
        
        actURL = self.ORGURL + '/content/listings/{0}/userEntitlements'.format(self.ProID)        
        
        self.LicensedUser = sendReq(actURL, licensedUserDict)          
        
        #Get all users, 20 at a time, regardless of licensed or not
        userCnt = 0
        totalUsers = 1
        start = 1
        self.AllUser = {'users':[]}
        allURL = self.ORGURL + '/portals/self/users'   
        
        while (userCnt < totalUsers) or (start != -1):
            
            allUsersDict = {'start' : start,
                            'sortOrder' : 'asc',
                            'num' : 20,
                            'token': self.token,
                            'f' :'json' }
                    
            userResp = sendReq(allURL, allUsersDict)   
            
            totalUsers = userResp['total']
            userCnt += len(userResp['users']) 
            start = userResp['nextStart']
            
            self.AllUser['users'] += userResp['users']   
            
        #Mash the 2 dicts together
        reset = True
        for i, allUsersVal in enumerate(self.AllUser['users']):
            user = ''
            for j, entitledUsersVal in enumerate(self.LicensedUser['userEntitlements']): 
                reset = False                
            
                if allUsersVal['username'] == entitledUsersVal['username']:
                    user = allUsersVal['username']           
                    allUsersVal.update(entitledUsersVal)
                    reset = True
                    break   
                
            if reset == True:
                continue       
 
        return self.LicensedUser, self.AllUser
        
    
    def setLicenseCounts(self):
        """Keep track of number of used licenses"""
        
        #key: ['Nice name', Entitled to #, Number Used]
        self.license = {'desktopAdvN':["Advanced", 0, 0],
                        'desktopStdN':["Standard", 0, 0],
                        'desktopBasicN':["Basic", 0, 0],           
                        'spatialAnalystN':["Spatial Statistics", 0, 0],
                        'geostatAnalystN':["GeoStatistical Analyst", 0, 0],
                        'workflowMgrN':["Workflow Manager", 0, 0],
                        'networkAnalystN':["Network Analyst", 0, 0],
                        'dataReviewerN':["Data Reviewer", 0, 0],
                        '3DAnalystN':["3D Analyst", 0, 0]
                        }            
        
        #Populate how many license each product has
        for k,v in self.orgEntitlements['entitlements'].items():
            self.license[k][1] = v['num']        

        
        for i, allUserVal in enumerate(self.AllUser['users']):            
            for k, v in allUserVal.items():
                if k == 'entitlements':
                    for i in range(0, len(v)):
                        self.license[v[i]][2] +=1        
        
        return self.license 
    
    def getIdentityStore(self):
        """Examine what type of identity store is being used if local portal"""
        
        URL = self.PortalURL + ":7443/arcgis/portaladmin/security/config"
        if "https" not in URL:
            URL = URL.replace("http", "https")
        
        # This particular end point needs a GET request, not POST
        URL += "?f=json&token={0}".format(self.token)
        identityRes = sendReq(URL) 

        if len(identityRes) == 0:
            return "builtin"
        else:
            #WINDOWS or LDAP
            return identityRes['userStoreConfig']['type']   
        
    
    #### - Local portal only functions - ####
    
    def releaseProLicense(self, user):
        """Release an offline license from the LOCAL portal"""
        
        URL = self.PortalURL + ":7443/arcgis/portaladmin/system/licenses/releaseLicense"
        releaseDict = {'token': self.token,
                       'f' :'json',
                       'username': user}   
        
        releaseRes = sendReq(URL, releaseDict)          
        
        return releaseRes
    
    def getUsersByGroup(self, group):
        """Return all users part of a found group for a local portal with a windows/ldap security store"""
        
        URL = self.PortalURL + ":7443/arcgis/portaladmin/security/groups/getUsersWithinEnterpriseGroup"
        searchGroupDict = {'token': self.token,
                           'f' :'json',
                           'groupName': group}   
        
        EusersInGroup = sendReq(URL, searchGroupDict)      
        
        return EusersInGroup
    
    def searchEUsers(self, userName):
        """Search for a user from a local portal that is using windows/ldap security store"""
        
        URL = self.PortalURL + ":7443/arcgis/portaladmin/security/users/searchEnterpriseUsers"
        searchEUserDict = {'token': self.token,
                           'f' :'json',
                           'filter': userName}       
        
        eUserList = sendReq(URL, searchEUserDict)  
        
        return eUserList
    
    def createUserLocalPortal(self, userPayload):
        """Add a local, enterprise windows/ldap user to the portal"""
        
        URL = self.PortalURL + ":7443/arcgis/portaladmin/security/users/createUser"
        header =  { 'Referer' : self.referer}
        newUsers = []    
        
        for i, userVal in enumerate(userPayload['users']): 
    
            userVal['token'] = self.token
            userVal['f'] = 'json'
            userVal['role'] = 'org_user'
            userVal['provider'] = 'enterprise'
            try:
                userVal['email']
            except KeyError as e:
                print("{0} key not found from group search.".format(e))
                if e == "email":
                    print("Ensure the identity store is setup with 'mail', not 'email':")
                    print("   \"userEmailAttribute\": \"mail\"  ") 
                return 0
    
            createUserRes = sendReq(URL, userVal, header)   
            
            #If user was added, collect that name, but change to the NAME@DOMAIN style so we can license
            if 'status' in createUserRes:
                if createUserRes['status'] == 'success':
                    if "\\" in userVal['username']:
                        username =  userVal['username'][userVal['username'].find("\\"):].strip("\\") +"@"+ userVal['username'][:userVal['username'].find("\\")]
                    else:
                        username =userVal['username']                
                    newUsers.append(username)
            else:
                print(createUserRes)          
        
        
        return newUsers
    
    #### //END - Local portal only functions - ####    
   
    #### ArcGIS.com Portal functions - ####    
      
    def listActiveUsers(self):    
        """Return all user information as JSON"""
        #Currently not used anywhere
        
        activeUserDict = {'token': self.token,
                          'f' :'json' } 
        
        URL = self.ORGURL + '/content/listings/{0}/userEntitlements'.format(self.ProID)
        
        print("\nQuerying for active users, this may take a few seconds....\n")
        activeUsers = sendReq(URL, activeUserDict)       
        
        return activeUsers
    
    
    def checkUser(self, username):
        """Check that a username is available and can be created in the Portal"""
        
        URL = self.ORGURL + "/community/checkUsernames"
        
        checkUserDict = {'token': self.token,
                         'f': 'json',
                         'usernames': username}
        
        checkUserRes = sendReq(URL, checkUserDict)
        
        if "usernames" in checkUserRes:
            if checkUserRes['usernames'][0]['suggested'] == checkUserRes['usernames'][0]['requested']:
                return username
            else:
                #print("Requested user name {0} is unavailable. Using {1}\n".format(username, checkUserRes['usernames'][0]['suggested']))
                return checkUserRes['usernames'][0]['suggested']
        else:
            print("Error checking username: {0}\n".format(username))
            print(checkUserRes)        
            return ""  #Return an empty string, logic on the other side needs to catch the error
    
    
    def createUser(self, userPayload):
        ''' Create a user account with password
        Accepts a list of lists. Lists must be properly order:
           username, password, firstname, lastname, fullname, email, role
           Note: This is the only function that accepts a list. Everything else is singular.
        '''
        create = False
        if "Password" in userPayload[0]:
            create = True
            print("Passwords found: >creating<, not inviting users by email.")        
        
        URL = self.ORGURL + "/portals/self/invite"
        
        newUsers = []    
        for i in range(0, len(userPayload)):
        
            newUserDict = {'token': self.token,
                              'f' :'json',
                              'invitationList': {"invitations":[
                                  {"username":userPayload[i]['Username'],
                                   #"password": "password123",
                                   "firstname":userPayload[i]['First Name'],
                                   "lastname":userPayload[i]['Last Name'],
                                   "fullname":userPayload[i]['First Name'] +" "+ userPayload[i]['Last Name'],
                                   "email":userPayload[i]['Email'],
                                   "role":userPayload[i]['Role']}]},
                              'subject':'An invitation to join an ArcGIS Online Organization, {0}. DO NOT REPLY'.format(self.OrgTitle),
                              'html': '<html><body><p>{0} {1} has invited you to join an ArcGIS Online Organization, {2}.</p><p> \
                              Please click this link to finish setting up your account and establish your password:\
                              <a href="https://www.arcgis.com/home/newuser.html?invitation=@@invitation.id@@">\
                              https://www.arcgis.com/home/newuser.html?invitation=@@invitation.id@@</a></p><p>\
                              Note that your account has already been created for you with the username, <strong>@@touser.username@@</strong>\
                              and that usernames are case sensitive.  </p><p>If you have difficulty signing in, please contact your \
                              administrator {1} {2} ({3}). Be sure to include a description of the problem, the error message, and a \
                              screenshot.</p><p>For your reference, you can access the home page of the organization here: \
                              <br>{4}</p><p>This link will expire in two weeks.</p><p style="color:gray;">\
                              This is an automated email, please do not reply.</p></body></html>'.format(self.OrgTitle, self.adminFName, self.adminLName, self.adminEmail, self.PortalURL)
                              }
            
            #If a password exists, we're creating users, not inviting them: add password into the payload.
            if create:
                password = userPayload[i]['Password']
                if len(password) < 8:
                    print("Password must be at least 8 characters. User: {0} not created".format(userPayload[i]['Username']))
                    continue
                newUserDict['invitationList']['invitations'][i]['password'] = password
                newUserDict['subject'] = "Some place holder text."                  
        
            inviteRes = sendReq(URL, newUserDict)                   
            if 'success' in inviteRes:    
                if inviteRes['success'] == True:
                    if inviteRes['notInvited']: pass
                    else:                        
                        newUsers.append(userPayload[i]['Username'])
            else:
                print(inviteRes)    
        
        return newUsers
    
    def deleteUser(self, user):    
        '''Deletes the user from the portal.
              BE CAREFUL, THERE IS NO UNDO!'''
        
        URL = self.ORGURL + "/community/users/{0}/delete".format(user)
        
        deleteUserDict = {'token': self.token,
                          'f' :'json'} 
        
        deleteRes = sendReq(URL, deleteUserDict)            
        
        return deleteRes    
        
    
    def assignProPermissions(self, user, entitlements):     
        '''User is a simple string, entitlements need to be a list'''
        
        #URL = CON.PortalURL + "/sharing/rest/content/listings/{0}/provisionUserEntitlements".format(CON.ProID)
        URL = self.ORGURL + "/content/listings/{0}/provisionUserEntitlements".format(self.ProID)
            
        permissionDict = {'token': self.token,
                          'f' :'json',
                          'userEntitlements': {'users':[user],                
                                               'entitlements':entitlements } 
                         }             
        
        assignPermRes = sendReq(URL, permissionDict)          
        
        return assignPermRes
    
    
    def createGroup(self, title, description, snippet, tags):
        '''Create an inivte only group inside ArcGIS.com. This group creation is designed to help manage accounts for license
           management. Groups can be manually modified after creation to perform other functions.
           '''
        
        URL = self.ORGURL + "/community/createGroup"
        
        createDict = {'token': self.token,
                      'f' :'json',
                      'title': title,
                      'access': 'org',
                      'description': description,
                      'snippet': snippet,
                      'tags': tags,
                      'isViewOnly': 'true',
                      'isInvitationOnly': 'true',
                      'sortField': 'avgrating',
                      'sortOrder': 'desc'                                     
                      }              
        
        createGroupRes = sendReq(URL, createDict)          
        
        return createGroupRes    
    

    def searchGroups(self):
        '''Find all groups matching a criteria. Function will continue to loop and return all groups as JSON, thus this
           function only needs to be called once.
        '''
        
        URL = self.ORGURL + "/community/groups"
        
        start = 1
        groups = []        
        
        while start >=1:
            searchDict = {'token': self.token,
                          'f':'json',                          
                          'q': 'orgid:' + self.orgID,
                          'start': start,
                          'num': 50,
                          'sortField': 'title'                          
                          }
            
            createGroupRes = sendReq(URL, searchDict)    
            start = createGroupRes['nextStart']
            groups += createGroupRes['results']
        
        return groups  
  

    def addUserToGroup(self, groupID, users):
        '''Assign 1 or more users to an existing group.'''
        
        URL = self.ORGURL + "/community/groups/{0}/addUsers".format(groupID)
        
        if type(users) == list:
            users = ','.join(users)
        
        addUsersDict = {'token': self.token,
                      'f':'json', 
                      'users': users                       
                      }
        
        addedUserResp = sendReq(URL, addUsersDict)          
        
        return addedUserResp
    
    #### //END ArcGIS.com Portal functions - ####    
 
        
# Helper functions    
def sendReq(url, qDict=None, headers=None):
    """Robust request maker"""
    #Need to handle chunked response / incomplete reads. 2 solutions here: http://stackoverflow.com/questions/14442222/how-to-handle-incompleteread-in-python
    #This function sends a request and handles incomplete reads. However its found to be very slow. It adds 30 seconds to chunked
    #responses. Forcing the connection to HTTP 10 (1.0) at the top, for some reason makes it faster.         
    
    qData = parse.urlencode(qDict).encode('UTF-8') if qDict else None    
    reqObj = request.Request(url)
    
    if headers != None:
        for k, v in headers.items():
            reqObj.add_header(k, v)
            
    try:
        if qDict == None:  #GET            
            r = request.urlopen(reqObj)
        else:  #POST            
            r = request.urlopen(reqObj, qData)
        responseJSON=""
        while True:
            try:                            
                responseJSONpart = r.read()                
            except client.IncompleteRead as icread:                
                responseJSON = responseJSON + icread.partial.decode('utf-8')
                continue
            else:                
                responseJSON = responseJSON + responseJSONpart.decode('utf-8')
                break       
        
        return (json.loads(responseJSON))
       
    except Exception as RESTex:
        print("Exception occurred making REST call: " + RESTex.__str__()) 
        
        
def convertTime(intime, mins=True):  
    '''Convert epoch time to human readable'''
    
    if intime == -1 or intime == "":
        return intime
    elif mins:
        return time.strftime('%m-%d-%y %H:%M', time.localtime(intime/1000))
    else:
        return time.strftime('%m-%d-%y', time.localtime(intime/1000))


def readUserCSV(userCSV):
    '''Reads a CSV file into a dictionary'''
    
    if not os.path.isfile(userCSV):
        print("CSV file not found. Check the path.")
        return None
    else:
        userDict = {}
        
        i=0
        with open(userCSV, 'r') as f:
            reader = csv.DictReader( f )
            for line in reader:
                userDict[i] = line
                i+=1                    
        
        return userDict

def createCSV(location, password='y'):
    '''Creates a basic CSV to serve as a template.
    Note: No checking is done here, the function expects a filepath which is ok'''  
    
    licenses= ','.join(list(licenseLookup.values()))
    
    template = {"First Name":"joe",
                "Last Name":'smith',
                "Email":"joe@email.com",
                "Username":"joeUser1234",
                "Password":"joePassword1234",
                "Role":"account_user",
                "License":licenses
                }
    
    if password == 'n':
        template.pop('Password')
    
    try:
        with open(location, 'w', newline='') as f:
            w = csv.DictWriter(f, template.keys())
            w.writeheader()
            w.writerow(template)
            return 0
    except:        
        return 1

def exportUsersToCSV(location, users):
    """Exports all users from self.UserInfo to a CSV file """
    
    # If the first record, which we get headers from doesnt have 'disconnectedInfo', add the key
    try: 
        users['users'][0]['disconnectedInfo']
    except KeyError:
        users['users'][0]['disconnectedInfo'] = {'disconnectedSince':''} 
    
    try:
        with open(location, 'w', newline='') as f:
            w = csv.DictWriter(f, users['users'][0].keys())
            w.writeheader()
            for i, val in enumerate(users['users']):
                w.writerow(val)
            return 0
    except:        
        return 1  

# //End helper functions


if __name__ == "__main__": 
    
    print("Not to be called directly. Goodbye.")
    
