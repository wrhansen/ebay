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
class EndItemRequest(TradingApiRequest):
	'''
	Ebay Trading API EndItem Request
	
	EndItem allows you to end listings that are already running on eBay
	
	This class accepts a data struture to create the single <EndItemRequest> container from.
	It can also generate the required headers and the <RequesterCredentials> elements for the
	request if the proper arguments are specified.
	
	This class uses the GlobalTrading configuration
	'''
	
	required_keys = ('item_id', 'ending_reason')
	other_keys = ()
	
	def __init__( self, *args ):
		self.call_name = 'EndItem'
		self.request_name = 'EndItemRequest'
		self.api_version = '747'
		TradingApiRequest.__init__(self, *args )
		self.help_string = """
%s
Required Keys: %s
Other Acceptable Keys: %s

Basic structure:
	{
		'item_id': "230525235",
		'ending_reason': "NotAvailable",
	}
	""" % (self.request_name, self.required_keys, self.other_keys )
		

	'''
	_validate_[fields] methods here...
	'''

	def _validate_ending_reason( self, reason ):
		'''
		Validates the ending_reason key. ending_reason can be only one of:
		['Incorrect', 'LostOrBroken', 'NotAvailable', 'OtherListingError', 'SellToHighBidder']
		If it isn't one of these values, an exception is raised
		
		Args:
			reason[str]: The value at key 'ending_reason' in the data structure
		'''

		accepted_reasons = ('Incorrect', 'LostOrBroken', 'NotAvailable', 'OtherListingError', 'SellToHighBidder')
		
		if not isinstance( reason, basestring ):
			raise InvalidReasonError( "Invalid Ending Reason: must be an instance of basestring, not a %s" % type(reason) )
		
		if reason not in accepted_reasons:
			raise InvalidReasonError( "Invalid Ending Reason: ending_reason must be one of: %s",list(accepted_reasons)) 


class InvalidReasonError( Exception ): pass
			
		

