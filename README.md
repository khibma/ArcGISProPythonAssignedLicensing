# ArcGISProPythonAssignedLicensing
These Python scripts demonstrate how to create users and assign ArcGIS Pro permissions. These scripts offer an alternative to the web ArcGIS.com interface for assigning permissions, specifically they are designed to simplify the administrative of licensing and permissions for large organizations.

In addition to licenses administration, you can get basic information about your organization in ArcGIS.com, query license counts, delete user accounts and generate accounts in batch using a CSV file. 

These scripts *will* work with a local Portal for ArcGIS 10.3. They provide some useful functions for querying and adding enterprise users from your LDAP or Windows store. (Some of the user administrative functions provided here will overlap with the [PortalPy](https://github.com/Esri/portalpy) scripts.)

**Note - _If you have a small organization, or only need to assign a few licenses, downloading and working with these scripts will NOT be faster than using the web interface. These scripts will provide the most benefit to organizations that need to assign a large number of licenses or to individuals who are more comfortable working with command line/scripting than a web UI_**.

The **ProLicense.py** has all the functions and calls to create users and assign licenses.

The **ProAdminDemo.py** file demonstrates on a singular basis how to call and use the functions after the ARCGIScom object has been created.

The **ProCommandLine.py** file is meant to provide a command line (DOS-esq) like experience to assign licenses and query the portal. A numeric menu allows different functions to be called to interact with the portal.

The **_something.py** files are specific examples on how to perform one task, such as using a CSV file to create user accounts. Use these files if you have no desire to enhance or modify the code as you only want to perform a specific action.

## Instructions
1. Download the Python files. Use the [Download Zip](https://github.com/khibma/ArcGISProPythonAssignedLicensing/archive/master.zip) to download all files
2. Run either the applicable script, such as Demo, Admin or specific example:
  * >>C:\Python34\python.exe c:\codeDownloaded\ProCommandLine.py
  * >>C:\Python34\python.exe c:\codeDownloaded\ProAdminDemo.py
  * >>C:\Python34\python.exe c:\codeDownloaded\_CreateUsersFromCSV.py

```
     1 - Get Portal info
     2 - Show license counts
     3 - Show used licenses
     4 - Create and Invite user
     5 - Add users from CSV file
     6 - Modify user account (Add/Change/Revoke a license)
     if LocalPortal:
         7 - Manage enterprise users (Local Portals only)
     U - Utilities: csv creation
     R - Refresh token and user references
```
![alt tag](https://cloud.githubusercontent.com/assets/2514926/5730877/08c1f702-9b4c-11e4-97eb-91ac5bcfca42.jpg)
![alt tag](https://cloud.githubusercontent.com/assets/2514926/5730878/09de5306-9b4c-11e4-80ed-492ec0e28058.jpg)
## Requirements
* ArcGIS for Organization (to be acted against with a named, administrative user) or Portal for ArcGIS
* Python 2.7 or 3.4+
* No ArcGIS software products are required to use these scripts

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

##Possible enhancements and areas to improve on
* Better local portal support, or possibly a split of code for ArcGIS.com and LocalPortal specific scripts
* UNIT tests
* WebPage UI (flask?) that could be hosted inside your organization that displays to all users who has a license checked out and/or what extensions are in use. Self-serve section to request a new account/license

## Licensing
Copyright 2015 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

[](Esri Tags: ArcGIS.com Python Pro ArcGIS Pro License administration)
[](Esri Language: Python)​
