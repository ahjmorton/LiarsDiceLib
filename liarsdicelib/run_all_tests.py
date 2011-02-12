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
Convience script to run all tests.
"""
import unittest

import game_test
import game_data_test
import game_proxy_test
import game_state_test
import game_integration_test

def suite() :
    """Return all tests known about"""
    return unittest.TestSuite([game_test.suite(), 
           game_integration_test.suite(),
           game_proxy_test.suite(),
           game_data_test.suite(),
           game_state_test.suite()])

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
