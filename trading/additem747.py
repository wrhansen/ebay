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

class AddItemRequest(TradingApiRequest):
	'''
	Ebay Trading API AddItem Request
	
	AddItem allows you to insert Fixed Price or Auction (chinese) listings into eBay
	
	This class accepts a data structure to create the single <AddItemRequest>
	from.  It can also generate the required headers, and the <RequesterCredentials>
	elements for the request if the proper arguments are specified.
	
	This class uses the GlobalTrading configuration
	'''

	other_keys = ('listing_type', 'picture_details','subtitle', 'sku','uuid','description',
				 'buy_it_now_price','condition_id', 'category_mapping_allowed',
				 'pay_pal_email_address', 'item_specifics' ) #Defines top-level keys that can be set(but aren't required)

	required_keys = ('title', 'primary_category','start_price','dispatch_time_max',
					 'listing_duration', 'payment_methods', 'location|postal_code','quantity',
					 'return_policy', 'shipping_details', 'site', 'country', 'currency' ) #Defines required top-level keys that must be set by the user


	
	def __init__( self, *args ):
		self.call_name = 'AddItem'
		self.request_name = 'AddItemRequest'
		self.api_version = '747'
		TradingApiRequest.__init__(self, *args )
		self.help_string = """
%s
Required Keys: %s
Other Acceptable Keys: %s

Basic structure:
{
	'listing_type': 'Chinese',
	'picture_details': {
		'picture_url' : 'http://i1.sandbox.ebayimg.com/03/i/00/a6/17/13_1.JPG?set_id=8800005007',
	},
	'subtitle': 'Hello!',
	'sku': '13523-358',
	'uuid': '3285-972389-57403587-34957',
	'description': 'THis is a test example, woo hoo!',
	'buy_it_now_price': 100.00,
	'condition_id': '1000',
	'category_mapping_allowed': 'True',
	'pay_pal_email_address': 'wes@ridersdiscount.com',
	'title': 'Super Dooper Awesome Megacool Helmet',
	'primary_category': {
		'category_id': '6749',
	},
	'start_price': 75.00,
	'dispatch_time_max': 3,
	'listing_duration': 'Days_7',
	'payment_methods': ['PayPal', 'VisaMC', 'AmEx', 'Discover'],
	'location': 'Holland, MI, USA',
	'postal_code': '49424',
	'quantity': 1,
	'return_policy': {
		'returns_accepted_option': 'ReturnsAccepted',
		'refund_option': 'MoneyBack',
		'returns_within_option': 'Days_30',
		'description': 'This is the first book in the Harry Potter series. In excellent condition!',
		'shipping_cost_paid_by_option': 'Buyer',
	},
	'shipping_details': {
		'shipping_type': 'Flat',
		'shipping_service_options': {
			'shipping_service_priority': 1,
			'shipping_service': 'ShippingMethodStandard',
			'shipping_service_cost': 19.98,
		},

		'exclude_ship_to_location': [],
	},
	'site': 'eBayMotors',
	'country': 'US',
	'currency': 'USD',
 }
	""" % (self.request_name,self.required_keys, self.other_keys )

		
		
	def _validate_title(self, title):
		'''
		Validates Item.Title
		'''
		if(not title.strip()):
			raise EmptyRequiredField("'title' cannot be empty!")
		if(not isinstance(title, basestring)):
			raise InvalidFieldType("'title' must be an instance of basestring")	
		if(len(title) > 80):
			raise InvalidFieldLength("title must be no more than 80 characters in length")
		if(not title.isupper()):
			#self._log_warning("String is not TitleCased") #TODO: logger?
			print "String is not TitleCased"
		return True
		
	def _validate_primary_category(self, category):
		'''
		Validates Item.PrimaryCategory
		'''
		#Ensure primary category has a dict as a value
		if(type(category) != dict):
			raise InvalidFieldType("'primary_category' must be a dict")
		#Ensure that primary category only contains a category_id element
		if( category.keys() != ['category_id'] ):
			raise InvalidCategoryStructure( "primary_category can only contain a category_id" )
	
	def _validate_shipping_details( self, shipping_details ):
		'''
		Validates the shipping_details structure
		Basic structure:
		{
			'shipping_type': 'Flat',
			'shipping_service_options': [{}*1-4],
			'international_shipping_service_option':[{}*0-5],
			'exclude_ship_to_locations':[''*x],
		}
		'''
		required_keys = set(['shipping_type', 'shipping_service_options'])
		accepted_keys = required_keys | set( ['international_shipping_service_option', 'exclude_ship_to_location'] )
		#Ensure shipping_details is a dict
		if not isinstance( shipping_details, dict ):
			raise InvalidFieldType( "'shipping_details' must be a dict" )
			
		#Check that required keys are there and check that they're all accepted
		unacceptable =  set( shipping_details.keys() ) - accepted_keys
		if len( unacceptable ):
			raise UnacceptableKeysError( "These keys are unacceptable for shipping_details: %s" % list(unacceptable))

		missing = required_keys - set( shipping_details.keys())
		if len( missing ):
			raise MissingRequiredKeys( "shipping_details is missing these required keys:%s" % list(missing))

		#####################################
		#Validate shipping_service_options
		#####################################
		shipping_options = shipping_details['shipping_service_options']
		
		'''
		{
			'shipping_service_priority': '1',
			'shipping_service': 'UPS',
			'shipping_service_cost': 2.50,
		}
		'''
		so_required = set(['shipping_service_priority','shipping_service','shipping_service_cost'])
		so_accepted = so_required | set( ['expedited_service'])
		
		if isinstance( shipping_options, dict):
			shipping_options = [shipping_options]

		if isinstance( shipping_options, list):
			#Check for at least one domestic shipping service (maximum of 4)
			if not len(shipping_options):
				raise InvalidShippingServiceOption( "Must contain at least 1 service_shipping_options dict(Max of 4)" )
			#If more than 4 shipping_options, raise error
			elif len( shipping_options) > 4:
				raise InvalidShippingServiceOption( "Too many shipping_service_options dicts specified. The maximum is 4" )
			for option in shipping_options:
				#If option isn't a dict, raise error
				if not isinstance( option, dict ):
					raise InvalidShippingServiceOption( "shipping_service_options must contain dict(s) that have at least %s required keys" % list(so_required) )
				unacceptable = set( option.keys()) - so_accepted

				if len(unacceptable):
					raise UnacceptableKeysError( "These keys are unacceptable for shipping_service_options: %s" % list(unacceptable))
			
				missing = so_required - set( option.keys() )
				if len(missing):
					raise MissingRequiredKeys( "shipping_service_options is missing these required keys: %s" % list(missing))

		else:
			#shipping_service_options must be either a dict or a list, raise error
			raise InvalidShippingServiceOption( "shipping_service_options must be of type dict or list(of dicts)" )
	
		#Check for zero to 5 international shipping services
		international = None
		if 'international_shipping_service_option' in shipping_details.keys():
			international = shipping_details['international_shipping_service_option']
			
		if international:
			iso_required = set(['shipping_service_priority','shipping_service','shipping_service_cost', 'ship_to_location'])
			iso_accepted = iso_required | set( ['expedited_service'])
		
			if isinstance( international, dict):
				international = [international]

			if isinstance( international, list):
				#If more than 5 international_shipping_service_option, raise error
				if len( international) > 5:
					raise InvalidShippingServiceOption( "Too many international_shipping_service_option dicts specified. The maximum is 5" )
				for option in international:
					#If option isn't a dict, raise error
					if not isinstance( option, dict ):
						raise InvalidShippingServiceOption( "international_shipping_service_option must contain dict(s) that have at least %s required keys" % list(iso_required) )
					unacceptable = set( option.keys()) - iso_accepted

					if len(unacceptable):
						raise UnacceptableKeysError( "These keys are unacceptable for international_shipping_service_option: %s" % list(unacceptable))
			
					missing = iso_required - set( option.keys() )
					if len(missing):
						raise MissingRequiredKeys( "international_shipping_service_option is missing these required keys: %s" % list(missing))
					
					if isinstance( option['ship_to_location'], str ):
						option['ship_to_location'] = [option['ship_to_location']]
						
					if isinstance( option['ship_to_location'], list):
						#Check if acceptable options
						unacceptable = set(option['ship_to_location']) - set( self.ship_to_locations )
						if len( unacceptable):
							raise UnacceptableLocationsError("%s are not acceptable ship_to_location's" % list( unacceptable))
			else:
				#shipping_service_options must be either a dict or a list, raise error
				raise InvalidShippingServiceOption( "international_shipping_service_option must be of type dict or list(of dicts)" )

		#Check that shipping type is correct
		if shipping_details['shipping_type'] not in self.shipping_types:
			raise InvalidShippingType("Invalid Shipping Type specified in shipping_details. Acceptable values are: %s" % list( self.shipping_types) )
		
		#Check that exclude locations is correct
		try:
			exclude_locations = shipping_details['exclude_ship_to_location']
		except KeyError:
			exclude_locations = None
		
		if exclude_locations:
			if isinstance( exclude_locations, basestring ):
				exclude_locations = list( exclude_locations )
				
			if isinstance( exclude_locations, list ):
				unacceptable = set( exclude_locations ) - set( self.ship_to_locations )
				if len( unacceptable):
					raise InvalidLocationsError( "%s are not acceptable exclude_ship_to_location's" % list( unacceptable ) )
				
			else:
				raise InvalidShippingServiceOption( "exclude_ship_to_location must be either a string or a list of strings")

class EmptyRequiredField( Exception ): pass
class InvalidFieldType( Exception ): pass
class InvalidFieldLength( Exception): pass
class InvalidCategoryStructure( Exception ): pass
class InvalidShippingServiceOption( Exception ): pass
class UnacceptableKeysError( Exception ): pass
class InvalidLocationsError( Exception ): pass



