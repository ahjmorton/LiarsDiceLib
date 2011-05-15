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
Game test tests the objects in the game module using unit tests.
This module relies on the mock library for mocking of dependencies."""

import unittest
import random

from mock import Mock

import game_common

class DiceRollerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.random = Mock(spec=random.Random)
        self.subject = game_common.roll_set_of_dice

    def testRollingSetOfDice(self) :
        ret = 3
        amount = 6
        face = (1, 6)
        self.random.randint.return_value = ret
        val = self.subject(amount, face, self.random)
        self.assertTrue(val is not None)
        self.assertTrue(len(val) == amount)
        self.assertTrue(reduce(lambda x, y: x and (y == ret), val, True))
        self.assertTrue(self.random.randint.called)
        self.assertTrue(self.random.randint.call_count == amount)
        self.assertTrue(self.random.seed.called)

def suite() :
    """Return a test suite of all tests defined in this module"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(DiceRollerTest))
    return test_suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
