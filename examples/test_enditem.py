"""
This script tests a full lifecycle of an eBay Trading API EndItem call.
It will create a request, build the xml and send it to the proper location
with the correct headers, and auth information, and to the correct environment
"""


from ebay.trading import EndItemRequest
import ebay


#Create the request object with default settings
#Default settings means use GlobalConfiguration settings
#To obtain header info and auth token info
enditem = EndItemRequest()

#Create the data structure that will contain the information needed
#To build the xml dom
#Then pass it to the update() function to send it to the request object
#And validate it for correctness and completeness
enditem.update( {
	'item_id': '110095561188',
	'ending_reason': 'NotAvailable',
})


#Build the request
request = enditem.get_element()
#Print the structure
enditem.prettyprint()

#Create an EbayAPIConnection object
connection = ebay.EbayAPIConnection( request=enditem )

#Send the request
connection.send_request()

#Read the response
response = connection.get_response().read()

print response


