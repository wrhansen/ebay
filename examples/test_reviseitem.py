"""
This script tests a full lifecycle of an eBay Trading API ReviseItem call.
It will create a request, build the xml and send it to the proper location
with the correct headers, and auth information, and to the correct environment
"""


from ebay.trading import ReviseItemRequest
import ebay


#Create the request object with default settings
#Default settings means use GlobalConfiguration settings
#To obtain header info and auth token info
reviseitem = ReviseItemRequest()

#Create the data structure that will contain the information needed
#To build the xml dom
#Then pass it to the update() function to send it to the request object
#And validate it for correctness and completeness
reviseitem.update( {
	'item': {
		'item_id':'110095561188',
		'start_price': 75.01,
	},
	'deleted_field': ['Item.SubTitle', 'Item.PostalCode'],
})


#Build the request
request = reviseitem.get_element()
#Print the structure
reviseitem.prettyprint()

#Create an EbayAPIConnection object
connection = ebay.EbayAPIConnection( request=reviseitem )

#Send the request
connection.send_request()

#Read the response
response = connection.get_response().read()

print response
