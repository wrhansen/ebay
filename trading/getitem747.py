#Encoding: UTF-8
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

__author__ = "Wesley Hansen"
__email__ = "wes@ridersdiscount.com"
__date__ = "06/15/2012 11:38:39 AM"

from ebay.trading.__trading import *
class GetItemRequest(TradingApiRequest):
	'''
	Ebay Trading API GetItem Request
	
	GetItem allows you to retrieve item information about a listing	
	This class accepts a data struture to create the single <GetItemRequest> container from.
	It can also generate the required headers and the <RequesterCredentials> elements for the
	request if the proper arguments are specified.
	
	This class uses the GlobalTrading configuration
	'''
	
	required_keys = ('item_id|sku',)
	other_keys = ('include_cross_promotion', 'include_item_compatibility_list', 'include_item_specifics', 'include_tax_table', 'transaction_id', 'variation_sku', 'variation_specifics')
	
	def __init__( self, *args ):
		self.call_name = 'GetItem'
		self.request_name = 'GetItemRequest'
		self.api_version = '747'
		TradingApiRequest.__init__(self, *args )
		self.help_string = """
%s
Required Keys: %s
Other Acceptable Keys: %s

Basic structure:
	{
		'item_id': "230525235",
	}
	""" % (self.request_name, self.required_keys, self.other_keys )
		

	'''
	_validate_[fields] methods here...
	'''
	
