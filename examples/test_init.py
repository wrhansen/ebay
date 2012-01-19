from ebay.trading import AddItemRequest
import ebay


#############################################################
#Testing default condition( No arguments passed)
#Expecting global headers to be used
#And sandbox token to be used
#############################################################
add_item = AddItemRequest( )

print "*"*30
print "Testing no arguments passed ( defaults on None )"
print "Headers: %s" % add_item.headers
print "Token: %s" % add_item.token
print "*"*30

##############################################################
#Testing condition when headers and token are user input
#Expecting headers and token to be set to those values(given that headers is correct)
#
##############################################################

headers = {
	"X-EBAY-API-COMPATIBILITY-LEVEL": '666',
	"X-EBAY-API-CALL-NAME": "SOMETHING RIDICULOUS",
	"X-EBAY-API-SITEID": "0",
	"Content-Type": "text/xml"
}
add_item1 = AddItemRequest(headers, 'ABC...123')

print "*"*30
print "Testing user input on headers and token"
print "Headers: %s" % add_item1.headers
print "token: %s" % add_item1.token
print "*"*30


##############################################################
#Testing condition when headers and token are set to false
#Expecting headers is False
#And token is also False
###############################################################

add_item2 = AddItemRequest(False, False)

print "*"*30
print "Testing headers and token are False"
print "Headers: %s" % add_item2.headers
print "token: %s" % add_item2.token
print "*"*30


#############################################################
#
# Testing connection using an EbayApiRequest object
#
#############################################################

connection = ebay.EbayAPIConnection( request=add_item )
print connection.headers





