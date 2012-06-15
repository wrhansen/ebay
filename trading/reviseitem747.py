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

class ReviseItemRequest( TradingApiRequest ):
	'''
	Ebay Trading API ReviseItem Request
	
	ReviseItem allows you to revise details about a listing
	that is already active on eBay
	
	This class accpets a data structure to create the single <ReviseItemRequest>
	container from. It can also generate the required headers and the
	 <RequesterCredentials> elements for the request if the proper arguments are
	 specified.
	'''
	
	required_keys = ('item',)#This class will have heavy validation because it is split into two 'root' structures
	other_keys = ('deleted_field',)
	
	deleted_fields = (	"Item.ApplicationData",
						"Item.AttributeSetArray",
						"Item.BuyItNowPrice",
						"Item.ConditionID",
						"Item.ExtendedSellerContactDetails",
						"Item.ClassifiedAdContactByEmailEnabled",
						"Item.ItemSpecifics",
						"Item.ListingCheckoutRedirectPreference.ProStoresStoreName",
						"Item.ListingCheckoutRedirectPreference.SellerThirdPartyUsername",
						"Item.ListingDesigner.LayoutID",
						"Item.ListingDesigner.ThemeID",
						"Item.ListingDetails.MinimumBestOfferMessage",
						"Item.ListingDetails.MinimumBestOfferPrice",
						"Item.ListingEnhancement",
						"Item.PayPalEmailAddress",
						"Item.PictureDetails.GalleryURL",
						"Item.PictureDetails.PictureURL",
						"Item.PostalCode",
						"Item.ProductListingDetails",
						"Item.SellerContactDetails",
						"Item.SellerContactDetails.CompanyName",
						"Item.SellerContactDetails.County",
						"Item.SellerContactDetails.InternationalStreet",
						"Item.SellerContactDetails.Phone2AreaOrCityCode",
						"Item.SellerContactDetails.Phone2CountryCode",
						"Item.SellerContactDetails.Phone2CountryPrefix",
						"Item.SellerContactDetails.Phone2LocalNumber",
						"Item.SellerContactDetails.PhoneAreaOrCityCode",
						"Item.SellerContactDetails.PhoneCountryCode",
						"Item.SellerContactDetails.PhoneCountryPrefix",
						"Item.SellerContactDetails.PhoneLocalNumber",
						"Item.SellerContactDetails.Street",
						"Item.SellerContactDetails.Street2",
						"Item.ShippingDetails.PaymentInstructions",
						"Item.SKU",
						"Item.SubTitle")#A list of all accepted deleted fields
	
	def __init__( self, *args ):
		self.call_name = 'ReviseItem'
		self.request_name = 'ReviseItemRequest'
		self.api_version = '747'
		TradingApiRequest.__init__(self, *args )
		
		self.help_string = """
%s
Required Keys: %s
Other Acceptable Keys: %s

Basic structure:
	{
		'item': {
			'item_id': '135135136'
		},
		'deleted_field': ['Item.SubTitle', 'Item.PostalCode'],
	}
	""" % (self.request_name, self.required_keys, self.other_keys )
	

	'''
	_validate_[field] methods here
	'''
	
	def _validate_item( self, item ):
		'''
		Validate the item tree as if it were an AddItem call
		'''
		if not isinstance( item, dict):
			raise InvalidFieldType( "Invalid Field Type: 'item' value must be a dict" )
			
		if 'item_id' not in item:
			raise MissingFieldError( "Missing Field Error: 'item' container is missing a required 'item_id' field")
	
	def _validate_deleted_field( self, deleted ):
		'''
		Validate the deleted_field tree. Allow for either
		a list of deleted fields, or a single string.
		'''
		if isinstance( deleted, basestring ):
			if deleted not in self.deleted_fields:
				raise InvalidDeletedField( "Only these fields are acceptable: %s"%list(self.deleted_fields))
		elif isinstance( deleted, list ):
			unacceptable = set( deleted) - set( self.deleted_fields )
			if len( unacceptable ):
				raise InvalidDeletedField( "These fields are not accepted: %s" % list(unacceptable) )
							
		else:
			raise InvalidFieldType( "'deleted_fields' must be either a single str or a list of str" )
		

class InvalidDeletedField( Exception ): pass
class InvalidFieldType( Exception ): pass	
class MissingFieldError( Exception ): pass
	
