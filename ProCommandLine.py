import os
import sys
import getpass
import time
import shutil
import ProLicense as pro

# The following variables can be hardcoded so you dont need to enter credentials.
# Simply press enter (blank input) when running the program to use these values
hardUser = '   '
hardPass = '   '
hardOrg =  'http://www.arcgis.com/sharing/rest'

pyVersion = sys.version_info[0]

def getInput(promptTxt):
    # Handle raw_input vs input py2/py3 diffs
    if pyVersion == 2:
        selection = raw_input(promptTxt)
    else:
        selection = input(promptTxt)

    return selection

def Menu():
    print(" 1 - Get Portal info ")
    print(" 2 - Show license counts")
    print(" 3 - Show used licenses")
    print(" 4 - Create and Invite user")
    print(" 5 - Add users from CSV file")
    print(" 6 - Modify user account (Add/Change/Revoke a license)")
    print(" 7 - Group management (search/create)")
    if CON.LocalPortal:
        print(" 8 - Manage enterprise users (Local Portals only)")
    print(" U - Utilities: csv creation")
    print(" R - Refresh token and user references")
    print(" q - quit")

def subMenu_ModifyUser():
    print(" =Modify User= \n")
    print(" 0 - return")
    print(" 1 - Add/Remove licenses")
    print(" 2 - Delete user account")

def subMenu_Utilities():
    print(" =CSV utilities= \n")
    print(" 0 - return")
    print(" 1 - Create template CSV file")
    print(" 2 - Export users to CSV file")

def subMenu_Groups():
    print(" =Group Management= \n")
    print(" 0 - return")
    print(" 1 - List groups")
    print(" 2 - Create Group")

def subMenu_EnterpriseUsers():
    print(" =Local portal utilities= \n")
    print(" 0 - return")
    print(" 1 - Search for enterprise user account")
    print(" 2 - List users by group")
    print(" 3 - Add enterprise users to Portal")
    print(" 4 - Release license (local Portal only)")

def Clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def SelectTxt(CON):

    expires = int((CON.expires - (time.time()*1000)) / 1000 / 60) #minutes

    print("\n[{0} - {1} - token:{2}]".format(CON.username, CON.PortalURL, expires))
    if pyVersion == 2:
        selection = raw_input("Selection ([enter] for menu):  ")
    else:
        selection = input("Selection ([enter] for menu):  ")

    return selection

def makeLicense(user):
    '''Creates a list of proper ArcGIS Pro licenses and extensions'''

    licLevel = ""
    while True:
        print("Configure license for: {0}".format(user))
        print("A - Advanced")
        print("S - Standard")
        print("B - Basic")
        print("R - REVOKE ALL")
        licLevel = getInput("[A|S|B|R]  ")
        if licLevel in ['A', 'S', 'B', 'R']:  break
        else: print("\nSelect a valid input.")

    if licLevel == 'R':
        entitlements = []

    else:
        extLics = []
        extensions = 0
        print("\nExtensions")
        print("1 - Spatial Analyst")
        print("2 - 3D Analyst")
        print("3 - Network Analyst")
        print("4 - Geostatistical Analyst")
        print("5 - Data Reviewer")
        print("6 - Workflow Manager")
        print("7 - Data Interop")
        print("8 - St Map NA")
        print("9 - St Map Euro")
        cExtensions = getInput("<123456789> or enter for none  ")
        if ' ' in cExtensions: cExtensions = cExtensions.replace(' ', '') #remove spaces if they were added
        if ',' in cExtensions: cExtensions = cExtensions.replace(',', '') #remove commas if they were added

        if len(tuple(cExtensions)) == 1:
            extLics.append(pro.licenseLookup[cExtensions])
        else:
            for ext in tuple(cExtensions):
                extLics.append(pro.licenseLookup[ext])

        entitlements = [pro.licenseLookup[licLevel]] + extLics

    return entitlements


def displayPortalInfo(CON):

    print("Org         : {0} (id:{1})".format(CON.OrgTitle, CON.orgID))
    print("Admin User  : {0} {1}".format(CON.adminFName, CON.adminLName))
    print("Admin Email : {0}".format(CON.adminEmail))
    print("Portal      : {0}".format(CON.PortalURL))
    if CON.LocalPortal:
        print("\n  Local Portal...")
        print("  Identity Store: {0}".format(CON.IdentityStoreType))

    return

def displayLicenseInfo(CON):

    print ("License counts...\n")
    for k, v in CON.license.items():
        print ("{0:23}: {1}/{2} ({3} used)".format(v[0], v[1]-v[2], v[1], v[2]))

    return

def displayUsedLicenses(CON, mainMenuCalled=True):

    def license2code(lic):
        exts = ''
        for l in lic:
            if "desktop" in l:
                level = l[7:-1] # remove "desktop" and "N" from level
            else:
                exts += list( pro.licenseLookup.keys())[list( pro.licenseLookup.values()).index(l)]

        codes = level + "-"  + "".join(str(x) for x in sorted(exts))
        return codes

    #term = shutil.get_terminal_size()
    #availLicLength =  term.columns - 41  #41 = chars used before license info
    # print ('{0:>{width}}'.format(license[len(license)-availLicLength:len(license)], width=term.columns-2))

    print()
    print("1-spatial, 2-3d, 3-network, 4-geostat, 5-datareviewer, 6-workflow, 7- DI, 8-STMapNA, 9-StMapEuro")
    print()
    print("{0:3}|{1:3}|{2:19}|{3:16}|{4:13}|{5:10}|{6}  ".format("ID#","OFF","User","LastLogin", "Licenses", "ActCreate", "ChkedOut"))
    print("----------------------------------------------------------------------------------")
    for i, allUserVal in enumerate(CON.AllUser['users']):
        license=' '
        offline=' '
        disconnectSince = ' '
        for k, v in allUserVal.items():
            if k == 'disconnected':  offline = "*" if v == True else " "
            if k == 'username':  name = v
            if k == 'lastLogin':  lastlogin = pro.convertTime(v)
            if k == 'created':  created = pro.convertTime(v, mins=False)
            if k == 'disconnectedInfo': disconnectSince = pro.convertTime(v['disconnectedSince'], mins=False)
            if k == 'entitlements':  license = license2code(v)

        print("{0:3}| {1} | {2:18}| {3:15}| {4:12}| {5:9}| {6}".format(i, offline, name, lastlogin, license, created, disconnectSince ))

    userSelect = getInput("Select user [#] or [enter] to return:  ")
    if userSelect == "" or userSelect.isdigit() == False:
        return 9999
    if mainMenuCalled:
        Clear()
        print("User {0} selected. Select an action:".format(CON.AllUser['users'][int(userSelect)]['username']))
        subMenu_ModifyUser()
        subSelection = SelectTxt(CON)
        if subSelection == "0": return  # Exit submenu
        if subSelection == "1": subSelection = changeLicense(CON, CON.AllUser['users'][int(userSelect)]['username']) # Add/Remove licenses
        if subSelection == "2": subSelection = deleteUserUI(CON, CON.AllUser['users'][int(userSelect)]['username'])  # Delete user account

    # Return the selected username
    return CON.AllUser['users'][int(userSelect)]['username']


def inviteUserUI(CON):

    if CON.LocalPortal:
        print("This end point for creating ArcGIS.com users. Use the LocalPortals option to create user accounts.")
        time.sleep(3)
        return 0

    Clear()
    print("Create a new user and email them an invitation\n")

    cUser = getInput("Username:  ")
    if cUser == '': return 0 # oops, didnt want to be here, return
    userCheck = CON.checkUser(cUser)
    if cUser == userCheck:
        print("  >Requested username > {0} < is available".format(cUser))
    else:
        while True:
            YesNo = getInput("  >Requested username not available. Use suggested name: {0}? [y|n|q]  ".format(userCheck))
            if YesNo.lower() == "y":
                cUser = userCheck
                break      # All good, carry on
            elif YesNo.lower() == 'n':
                return 1   # Go back and try a different username
            elif YesNo.lower() == 'q':
                return 0   # Quit, dont want to make a user

    cFName = getInput("First name:  ")
    cLName = getInput("Last name:  ")
    cEmail = getInput("Email:  ")
    cRole = getInput("Role[{0}]:  ".format("account_user"))
    if cRole == "" or cRole == None:
        cRole = "account_user"

    # Creating a dict of dicts as create wants this (easier for CSV management)
    userPayload = {0: {'Last Name': cLName,
                       'Email': cEmail,
                       'First Name': cFName,
                       'Username': cUser,
                       'Role': cRole}}

    print("\nAbout to create a user with the following:")
    for k,v in userPayload[0].items():
        print("  {0} : {1}".format(k,v))

    while True:
        cUser = getInput("   Create users? [y|n]  ")
        if cUser.lower() == 'y': break  # carry on
        elif cUser.lower() == 'n': return 0 # exit back

    invitedUser = CON.createUser(userPayload)

    if len(invitedUser) > 0:
        while True:
            assign = getInput("Do you want to assign them a license now? [y|n]  ")
            if assign.lower() == 'y' or assign.lower() == 'n': break

        if assign == "y":
            changeLicense(CON, invitedUser[0])
        else:
            refreshUI(CON, False) # Refresh is called in changeLicense, so only need to refresh if no license added

    return 0

def addUserFromCSV(CON):

    csvFile = getInput("Enter path to CSV file:  ")
    userPayload = pro.readUserCSV(csvFile)
    if (userPayload == None) or (not userPayload):
        print("No users to load from CSV file.")
        return 0

    # Check each username in the CSV. If it cant be used, remove it from the payload.
    for i in range(0, len(userPayload)):
        checkedUser = CON.checkUser(userPayload[i]['Username'])
        if checkedUser != userPayload[i]['Username']:
            userPayload.pop(i)
    if not userPayload:
        print("No names inside the CSV can be used")

    userList = CON.createUser(userPayload)

    if len(userList) > 0:
        while True:
            groupAssign = getInput("Do you want to assign new users to a group? [y|n]  ")
            if groupAssign.lower() == 'y' or groupAssign.lower() == 'n': break

        if groupAssign.lower() == 'y':
            while True:
                cGroupChoice = getInput("Add user to an [E]xisting or [N]ew group?  ")
                if cGroupChoice.lower() == 'e' or cGroupChoice.lower() == 'n': break
            if cGroupChoice.lower() == 'e':
                groupID = listGroupsUI(CON, False)
            else:
                groupID = createGroupUI(CON, False)
            addedUserResp = CON.addUserToGroup(groupID, userList)

            for user in addedUserResp['notAdded']:
                print("{0} was not added to the group. Investigate this user manually.".format(user))


        if "License" in userPayload[0]:
            print("\nPlease wait a second while user accounts are created before permissions can be assigned")
            time.sleep(2)

            for i in range(0, len(userPayload)):
                workingUser = userPayload[i]['Username']
                permResp = CON.assignProPermissions(workingUser, userPayload[i]['License'].split(','))
                if "success" in permResp:
                    print("{0} assigned licenses: {1}".format(workingUser, userPayload[i]['License']))
                else:
                    print("FAILED to assign {0} to {1}".format(userPayload[i]['License'], workingUser))
                    print(permResp)

        else:
            while True:
                assign = getInput("Do you want to assign new users a license now? [y|n]  ")
                if assign.lower() == 'y' or assign.lower == 'n': break

            if assign == "y":
                for user in userList:
                    changeLicense(CON, userList)


    refreshUI(CON, False) # Update as new users added
    return 0

def changeLicense(CON, user=None, entitlements=None):

    if user is None:
        user = getInput("User name: [<username> | l(ist users)]  ")
        if user == 'l':
            user = displayUsedLicenses(CON, False)
            if user == 9999:
                print("No user selected, return to menu main.")
                return 0

    if entitlements == None or entitlements == "":
        entitlements = makeLicense(user)

    status = CON.assignProPermissions(user, entitlements)

    if 'success' in status:
        if status['success'] == True:
            print("{0} was licensed".format(user))
    else:
        print(status)


    time.sleep(1)

    refreshUI(CON, False) # Update references
    return 0 # Exit from the submenu

def deleteUserUI(CON, user=None):

    print("WARNING!! This will delete the user account from your org and ArcGIS.com. This cannot be un-done.")
    if user is None:
        user = getInput("User name: [<username> | l(ist users)]  ")
        if user.lower() == 'l':
            user = displayUsedLicenses(CON, False)
            if user == 9999: return 9999

    proceed = ''
    while proceed not in ['Y', 'N']:
        proceed = getInput("Proceed with deleting << {0} >> [Y|N]  ".format(user))  # NOT casting to lower, must use UPPERCASE letter
        if proceed == 'N': return 9999 # This will return to the sub-menu

    #revoke the users licenses
    status = CON.assignProPermissions(user, [])
    #delete user
    deleteRes = CON.deleteUser(user)

    try:
        if deleteRes['success'] == True:
            print("\n{0:^} was deleted".format(user))
    except:
        print(deleteRes)

    refreshUI(CON, False) # Update as new users added
    return 0 # Exit from the submenu


def searchEUsersUI(CON):

    userSearch = getInput("Enter user name to search: ")

    userList = CON.searchEUsers(userSearch)

    if "users" not in userList:
        print ("No users matched")
        return 0
    else:
        print("{0} |{1:30} |{2:20}".format("ID#", "Name", "userID"))
        for i, userVal in enumerate(userList['users']):
            print("{0:3} |{1:30} |{2:20}".format(i, userVal['fullname'], userVal['username']))

        userID = getInput("Select user by ID # to add to Portal:  ")
        if not userID.isdigit(): return 0

        userDict = {'users': [userList['users'][int(userID)]]}
        addedUser = CON.createUserLocalPortal(userDict)

        if len(addedUser) > 0:
            print("Added {0} users to the Portal".format(len(addedUser)))
            while True:
                cLic = getInput("\nSet a license for all users: [y|n] ")
                if cLic.lower() == 'y':
                    entitlements = makeLicense("all users")
                    for user in addedUser:
                        status = CON.assignProPermissions(user, entitlements)
                        print(status)
                    break  # carry on
                elif cLic.lower() == 'n': break
            refreshUI(CON, False)

    return 0


def listEUsersByGroupUI(CON):

    group = getInput("Enter group name to search: ")
    if group == '': return 0
    else: userList = CON.getUsersByGroup(group)

    if "users" in userList:

        while True:
            showUsers = getInput("Found {0} users, do you want to list them [y|n]  ".format(len(userList['users'])))
            if showUsers.lower() == 'y' or showUsers.lower() == 'n': break

        if showUsers.lower() == 'y':
            for i, euser in enumerate(userList['users']):
                print ("User: {0} ==> {1}".format(euser['fullname'], euser['username'] ))

        while True:
            addToPortal = getInput("Do you want to add these users to Portal [y|n]  ")
            if addToPortal.lower() == 'y' or addToPortal.lower() == 'n': break

        if addToPortal == "y":
            for user in userList:
                addedUsers = CON.createUserLocalPortal(userList)
        else:
            return 0

        if len(addedUsers) > 0:
            print("Added {0} users to the Portal".format(len(addedUsers)))
            while True:
                cLic = getInput("\nSet a license for all users: [y|n] ")
                if cLic.lower() == 'y':
                    entitlements = makeLicense("all users")
                    for user in addedUsers:
                        status = CON.assignProPermissions(user, entitlements)
                        print(status)
                    break  # carry on
                elif cLic.lower() == 'n': break
            refreshUI(CON, False)
    else:
        # Error, no users in group: show the returned JSON
        print(userList)

    return 0

def AddEUserToPortal(CON):
    # accept both a list, or just single users? check how other functions did it above.

    userPayload = {}

    cUserName = getInput("   Username [user@DOMAIN]:  ")
    if cUserName == '': return 0
    if "@" not in cUserName:
        print("    No '@' found in user name, did you enter the username correctly?\n")
    cName = getInput("   Full Name:  ")
    cEmail = getInput("   Email:  ")
    cDesc = getInput("   Description:  ")
    userPayload = {'users' : [{'fullname': cName,
                              'email': cEmail,
                              'username': cUserName,
                              'description': cDesc}]}
    while True:
        cUser = getInput("   Create user? (this may take a moment) [y|n]  ")
        if cUser.lower() == 'y': break
        elif cUser.lower() == 'n': return 0 # exit back


    invitedUser = CON.createUserLocalPortal(userPayload)

    if len(invitedUser) > 0:
        print("Added {0} users to the Portal".format(len(invitedUser)))
        while True:
            cLic = getInput("\nSet a license for all users: [y|n] ")
            if cLic.lower() == 'y':
                entitlements = makeLicense("all users")
                for user in invitedUser:
                    status = CON.assignProPermissions(user, entitlements)
                    print(status)
                break  # carry on
            elif cLic.lower() == 'n': break

        refreshUI(CON, False)
    return 0

def listGroupsUI(CON, mainMenuCalled=True):

    groups = CON.searchGroups()

    if groups == []:
        print("No groups found")
    else:
        print("\n{0:3}|{1:31}|{2:16}|{3}  ".format("ID#", "Title", "Owner", "Created on"))
        print("----------------------------------------------------------------------------------")
        for i, group in enumerate(groups):
            print("{0:3}| {1:30}| {2:15}| {3}".format(i, group['title'], group['owner'], pro.convertTime(group['created'], False) ))

        if not mainMenuCalled:
            cGroupNum = getInput("\n   Select a group number:  ")
            return groups[int(cGroupNum)]['id']

    getInput("\nPress enter to continue.")
    return 0

def createGroupUI(CON, mainMenuCalled=True):

    cGroupName = getInput("\n   Enter a group name (title):  ")
    if cGroupName == '': return 0
    cGroupDesc = getInput("   Enter a group description:  ")
    cGroupSnippet = getInput("   Enter a group snippet:  ")
    cGroupTags = getInput("   Enter group tags:  ")

    groupCreateResp = CON.createGroup(cGroupName, cGroupDesc, cGroupSnippet, cGroupTags)

    if 'success' in groupCreateResp:
        if groupCreateResp['success'] == True:
            print("Created group {0}".format(groupCreateResp['group']['title']))
            if not mainMenuCalled:
                return groupCreateResp['group']['id']
    else:
        print("Group might not be created, see message:")
        print(groupCreateResp)

    getInput("Press enter to continue.")
    return 0

def releaseLicenseUI(CON, user=None):

    #if CON.LocalPortal == False:
    #    print("License can only be returned for local portals, not ArcGIS.com. \n You'll need to contact customer service.")
    #    time.sleep(4)
    #    return 0

    print("Warning! This will terminate a users disconnected license")
    if user is None:
        user = getInput("User name: [<username> | l(ist users)]  ")
        if user.lower() == 'l':
            user = displayUsedLicenses(CON, False)
            if user == 9999: return 9999

    releaseRes = CON.releaseProLicense(user)

    try:
        if releaseRes['success'] == True:
            print("\n{0} has this disconnected session revoked.".format(user))
    except:
        print(releaseRes)

    return 0 # Exit from the submenu


def createCSVUI():
    """Create a blank template CSV file that can be used to make accounts"""

    location = getInput("Enter the full path to create the CSV file  ")
    if location == "": return 0

    password = ''
    while password.lower() not in ['y', 'n']:
        password = getInput("Passwords will make accounts. No passwords will invite users.\nPut Password header in the CSV file? [y|n]  ")

    success = pro.createCSV(location, password)
    if success != 0:
        print("Problem creating CSV file. Check the location and try again.")
    else:
        print("Created: {0}\n".format(location))

    time.sleep(2)
    return 0

def exportUsersCSVUI(CON):
    """Export all the users in the org to a CSV file"""

    print("Export the users and their license entitlements to a CSV file")
    location = getInput("Enter the full path to create the CSV file  ")
    if location == "": return 0

    success = pro.exportUsersToCSV(location, CON.AllUser)

    if success != 0:
        print("Problem creating CSV file. Check the location and try again.")
    else:
        print("Created: {0}\n".format(location))

    time.sleep(2.5)
    return 0


def refreshUI(CON, token=False):

    if token:
        CON.token, CON.expires, CON.referer = CON.getToken(CON.username, CON.password, CON.ORGURL)
    CON.orgEntitlements, CON.orgProvision, CON.proID = CON.getOrgProvision()
    CON.UserInfo, CON.AllUser = CON.getUserLicenseInfo()
    CON.AllUserCount = len(CON.AllUser['users'])
    CON.setLicenseCounts()
    print("\n  ##Token and ORG info updated##  ")

    return



if __name__ == "__main__":

    print("Welcome to ArcGIS Pro Python based license management.")
    print("To get started, you'll need to supply some authentication information")
    print("An account with portal administrator level permissions is required.\n")
    username = getInput("User name: ") or hardUser
    password = getpass.getpass('Password: ') or hardPass

    print("\nConnect to ArcGIS.com or a local portal. For a local portal, use the full portalAdmin URL with port.")
    print("     Eg. https://server.domain.com:7443/arcgis/sharing/rest")
    orgURL = getInput("\nEnter Org URL, or accept default [{0}]:  ".format(hardOrg))
    if orgURL == None or orgURL == "":
        orgURL = hardOrg

    print("  Looking up Org Info. This may take a few seconds....\n")
    CON = pro.ARCGIScom(username, password, orgURL)

    Clear()
    Menu()
    selection = SelectTxt(CON)

    while True:

        if selection == "1":  # Get Portal info
            Clear()
            displayPortalInfo(CON)
            selection = SelectTxt(CON)

        elif selection == "2":  # Show license counts
            Clear()
            displayLicenseInfo(CON)
            selection = SelectTxt(CON)

        elif selection == "3":  # Show used licenses
            Clear()
            displayUsedLicenses(CON, True)
            selection = SelectTxt(CON)

        elif selection == "4":  # Add single user
            Clear()
            while True:
                response = inviteUserUI(CON)
                if response == 0: break # Break the loop if good user names have come back, or forced quit (0)
            selection = SelectTxt(CON)

        elif selection == "5": # Add users from CSV file
            Clear()
            addUserFromCSV(CON)
            selection = SelectTxt(CON)

        elif selection == "6":   # Add/Change/Delete a license from a user
            while True:
                Clear()
                subMenu_ModifyUser()
                subSelection = SelectTxt(CON)
                if subSelection == "1": subSelection = changeLicense(CON, None) # Add/Remove licenses
                if subSelection == "2": subSelection = deleteUserUI(CON, None)  # Delete user account
                if subSelection == "0" or subSelection =='': break  # 0-return
            selection = SelectTxt(CON)

        elif selection == "7":   # Group management
            while True:
                Clear()
                subMenu_Groups()
                subSelection = SelectTxt(CON)
                if subSelection == "1": subSelection = listGroupsUI(CON, True) # List groups
                if subSelection == "2": subSelection = createGroupUI(CON, True)  # Create group
                if subSelection == "0" or subSelection =='': break  # 0-return
            selection = SelectTxt(CON)

        elif selection == "8":   # Manage enterprise users
            if not CON.LocalPortal:
                selection = SelectTxt(CON)
            else:
                while True:
                    Clear()
                    subMenu_EnterpriseUsers()
                    subSelection = SelectTxt(CON)
                    if subSelection == "1": subSelection = searchEUsersUI(CON) # Search for a user by string
                    if subSelection == "2": subSelection = listEUsersByGroupUI(CON) # List users by group
                    if subSelection == "3": subSelection = AddEUserToPortal(CON)  # Add enterprise users to Portal
                    if subSelection == "4": subSelection = releaseLicenseUI(CON, None)  # Release license
                    if subSelection == "0" or subSelection =='': break  # 0-return
                selection = SelectTxt(CON)

        elif selection.lower() == "u": # Utilities
            while True:
                Clear()
                subMenu_Utilities()
                subSelection = SelectTxt(CON)
                if subSelection == "1": subSelection = createCSVUI() # Template CSV"
                if subSelection == "2": subSelection = exportUsersCSVUI(CON) # Export users to CSV file
                if subSelection == "0" or subSelection =='': break  # 0-return
            selection = SelectTxt(CON)

        elif selection.lower() == "r": # Refresh
                Clear()
                refreshUI(CON, True)
                selection = SelectTxt(CON)

        elif selection.lower() == 'q': # Quit.
            print("EXIT...")
            sys.exit()

        else:
            Clear()
            Menu()
            selection = SelectTxt(CON)