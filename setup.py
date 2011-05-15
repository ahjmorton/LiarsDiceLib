"""
***** BEGIN LICENSE BLOCK *****
Version: MPL 1.1

The contents of this file are subject to the Mozilla Public License Version 
1.1 (the "License"); you may not use this file except in compliance with 
the License. You may obtain a copy of the License at 
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
for the specific language governing rights and limitations under the
License.

The Original Code is LiarsDiceLib.

The Initial Developer of the Original Code is
Andrew Morton <ahjmorton@gmail.com> .
Portions created by the Initial Developer are Copyright (C) 2011
the Initial Developer. All Rights Reserved.

Contributor(s):
     
***** END LICENSE BLOCK *****
Standard distutils build script
"""
try :
    from setuptools import setup
except ImportError :
    from distutils.core import setup

setup(name='liarsdicelib',
      description="""A pure Python library for the implementation of the game rules of Liars dice""",
      author="Andrew Morton",
      author_email="ahjmorton@gmail.com",
      url="https://github.com/ahjmorton/LiarsDiceLib",
      license="MPL 1.1",
      packages=['liarsdicelib'],
      version="0.0.1"
      )
