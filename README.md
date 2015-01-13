# ArcGISProPythonAssignedLicensing
The Python scripts here demonstrate how to create users and assign ArcGIS Pro permissions. These scripts offer an alternative to the web ArcGIS.com interface of assigning permissions. In addition to licenses administration, you can also get back basic informaiton about your organization in ArcGIS.com, query license counts, delete user accounts and generate accounts in batch using a CSV file.

Note - If you have a small organization, or only need to assign a few licenses, downloading and working with these scripts will NOT be faster than using the web interface. These scripts will provide the most benefit to organizations that need to assign a large number of licenses or to individuals who are more comfortable working with command line/scripting than a web UI.

The ProLicense.py has all the functions and calls to create users and assign licenses.
The ProAdminDemo.py file demonstrates on a singular basis how to call and use the functions after the ARCGIScom object has been created.
The ProCommandLine.py file is meant to provide a command line (DOS-esq) like experience to assign licenses and query the portal. A numeric menu allows different functions to be called to interact with the portal.

## Requirements

* Python 3.4+
* No ArcGIS products are required
* This will NOT work with Python 2.x

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

##Possible enhancements and areas to improve on
-Better local portal support, or possibly a split of code for ArcGIS.com and LocalPortal specific scripts
-UNIT tests
-WebPage UI (flask?) that could be hosted inside your organization that displays to all users who has a license checked out and/or what extensions are in use. Self-serve section to request a new account/license

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
