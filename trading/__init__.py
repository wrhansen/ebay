#    This module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.#
#
#    This module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = ["Ben DeMott", "Wesley Hansen"]
__email__ = "wes@ridersdiscount.com"
__date__ = "06/15/2012 11:38:39 AM"
'''
This module contains data and functions that are common to all 
'''


import uuid
import os.path
from lxml import etree
import sys
from ebay import *
from __trading import *

############################
#
#	Import version 747
#
############################
from additem747 import AddItemRequest
from enditem747 import EndItemRequest
from reviseitem747 import ReviseItemRequest
from relistitem747 import RelistItemRequest
from getitem747 import GetItemRequest
from getorders747 import GetOrdersRequest
from getebaydetails747 import GetEbayDetailsRequest
