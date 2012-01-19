'''
This script will test the entire lifecycle of an eBay API request.
It will test creating a request, and building the xml dom.
And then it will create a connection, building appropriate headers
and send the request to the proper eBay server
'''

from ebay.trading import AddItemRequest
import ebay
import uuid

#Create an AddItemRequest with default settings
#Settings include: GlobalConfiguration of headers and auth-token
#All in the sandbox environment(default)

add_item = AddItemRequest( )


#The data structure to send to the AddItemRequest
#This example creates an auction that lasts 7 days, 
#And offers a flat rate shipping to only the US
data = {
	'listing_type': 'Chinese',
	'picture_details': {
		'picture_url' : 'http://i1.sandbox.ebayimg.com/03/i/00/a6/17/13_1.JPG?set_id=8800005007',
	},
	'subtitle': 'Hello!',
	'sku': '13523-358',
	'uuid': str(uuid.uuid4()).replace("-",""),
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
	'subtitle': 'HELLO THIS IS A STUPID SUBTITLE',
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

	},
	'site': 'eBayMotors',
	'country': 'US',
	'currency': 'USD',
	'item_specifics': {'name_value_list':
						[ {'name': 'Brand', 'value': 'HJC'},
						  {'name': 'Color', 'value': 'Anthracite'},
						  {'name': 'Size', 'value': 'XXL'}
						]
					   },
}

#Update the AddItemRequest data structure that will be used to build the xml request
#This is also the step that validates the incoming structure for correctness
add_item.update( data )

#Build the AddItemRequest xml dom
#This function call also returns the etree._Element that was built
request = add_item.get_element()
add_item.prettyprint()

#Create an EbayAPIConnection for our AddItemRequest
#Once a request is properly built, it's easy to create a connection object
#by simply passing the AddItemRequest object as the argument to 
#the EbayAPIConnection constructor
connection = ebay.EbayAPIConnection( request=add_item )

#Send the request
connection.send_request()

#Get the response
#For now, just print it out
#Eventually will have a response parser
response = connection.get_response().read()
print response










