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

This module defines common classes such as exceptions and common
dice rolling functions"""

import random

def roll_set_of_dice(num, face_vals, rand=random) :
    """Roll a set of dice with values that are 
face_vals[0] <= n <= face_valls[1].
Source of randomness comes from prng module"""
    rand.seed()
    ret_list = list()
    count = 0
    while count < num :
        ret_list.append(rand.randint(face_vals[0], face_vals[1]))
        count = count + 1
    return ret_list



class IllegalBidError(Exception) :
    """This exception occurs when a bid attempt is made that is illegal
given the current state of the game.
For example if the previous bid of the game was two dice showing a five 
then a bid is attempted with one six then this exception is thrown"""
    def __init__(self, value) :
        Exception.__init__(self)
        self.val = value

    def __str__(self) :
        return repr(self.value)

class IllegalStateChangeError(Exception) :
    """This exception occurs when an attempt is made to perform an illegal
state transition"""
    def __init__(self, value) :
        Exception.__init__(self)
        self.val = value

    def __str__(self) :
        return repr(self.value)  

if __name__ == "__main__" :
    pass
