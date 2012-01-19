import sys
from ebay.trading import AddItemRequest
from ebay.trading import EndItemRequest
#		OR
#from ebay.trading import *
from lxml import etree



##########################################
#
#		Testing AddItem
#
##########################################

request = AddItemRequest( False, 'ABC...123' )

request.update( {
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
		'international_shipping_service_option':[
		{
			'shipping_service': 'StandardInternational',
			'shipping_service_cost': 29.98,
			'shipping_service_priority': 2,
			'ship_to_location': 'CA',
		},
		{
			'shipping_service': 'StandardInternational',
			'shipping_service_cost': 39.98,
			'shipping_service_priority': 3,
			'ship_to_location': ['Americas', 'Europe', 'Asia', 'AU'],
		},],
		'exclude_ship_to_location': [],
	},
	'site': 'eBayMotors',
	'country': 'US',
	'currency': 'USD',
 } )

print etree.tostring( request.get_element(), pretty_print=True )


'''
##########################################
#
#		Testing EndItem
#
##########################################
end_item = EndItemRequest( False, False )
end_item.update( { 'item_id': '033195015359',
	'ending_reason': 'Hmmm',
})
print etree.tostring( end_item.get_element(), pretty_print=True )
'''
"""

##############################################################
#
#Testing appending a TradingApiRequest to a BulkDataFile
#
###############################################################

bulkfile = api_prototype.BulkDataFile( 'AddItem', 'Request', '747', '100' )
bulkfile.open( 'bulk_file_request_02.xml', 'w' )
bulkfile.append( request )
bulkfile.close()
bulkfile.open( 'bulk_file_request_02.xml', 'a' )
bulkfile.append( request )
bulkfile.append( end_item )#Testing appending an item that doesn't match
"""

