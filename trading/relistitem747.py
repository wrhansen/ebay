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
class RelistItemRequest(TradingApiRequest):
	'''
	Ebay Trading API RelistItem Request
	
	RelistItem allows you to relist a listing that has already ended on eBay
	
	This class accepts a data struture to create the single <RelistItemRequest> container from.
	It can also generate the required headers and the <RequesterCredentials> elements for the
	request if the proper arguments are specified.
	
	This class uses the GlobalTrading configuration
	'''
	
	required_keys = ('item',)
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
		self.call_name = 'RelistItem'
		self.request_name = 'RelistItemRequest'
		self.api_version = '747'
		TradingApiRequest.__init__(self, *args )
		self.help_string = """
%s
Required Keys: %s
Other Acceptable Keys: %s

Basic structure:
	{
		'item': {
			'item_id': '131541515',
		},
		'deleted_field': [],
	}
	""" % (self.request_name, self.required_keys, self.other_keys )
	
	"""
	VALIDATION FUNCTIONS
	"""
	
	def _validate_item( self, item ):
		'''
		Validate the item container. The item container contains elements that need to be changed
		from the original listing. It can be any of the accepted additem calls.
		At the very least, the 'ItemID' field is required for this call. So this function
		should check for that.
		
		Args:
			item[dict]: The structure of AddItem-type fields that need to be changed
		'''
		if not isinstance( item, dict):
			raise InvalidFieldType( "Invalid Field Type: 'item' value must be a dict" )
			
		if 'item_id' not in item:
			raise MissingFieldError( "Missing Field Error: 'item' container is missing a required 'item_id' field")

	def _validate_deleted_field( self, field ):
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
class MissingFieldError( Exception ): pass	
class InvalidFieldType( Exception ): pass
