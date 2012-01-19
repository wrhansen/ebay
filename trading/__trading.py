from ebay import *
class GlobalConfiguration():
	'''
	Holds static global configuration for the entire Trading API
	All calls will use this configuration by default if they don't receive
	a configuration of their own.
	'''
	headers = {
		'X-EBAY-API-COMPATIBILITY-LEVEL': None,
		'X-EBAY-API-DEV-NAME': None,
		'X-EBAY-API-APP-NAME': None,
	}
	token   = ""
	
	header_keys     = ('X-EBAY-API-COMPATIBILITY-LEVEL', 'X-EBAY-API-DEV-NAME', 'X-EBAY-API-APP-NAME', 'X-EBAY-API-CERT-NAME', 'X-EBAY-API-SITEID', 'X-EBAY-API-CALL-NAME')
	

	@classmethod
	def set_headers(cls, headers):
		assert type(headers) == dict
		missing = set(header_keys) - set(headers.keys())
		if(len(missing)):
			raise ValueError("You are missing these keys from your headers dict: %s" % list(missing))
		cls.headers = headers
		
	@classmethod
	def set_token(cls, credentials):
		assert type(credentials) == str

	@classmethod
	def get_token(cls, token):
		if token in ['production', 'sandbox']:
			cls.token= EbayAPIConnection( environment=token ).token
			return cls.token
		
	@classmethod
	def get_headers(cls, environment):
		#Grab connection headers
		connection = EbayAPIConnection( None, "trading_api", environment )
		return connection.headers

class TradingApiRequest(EbayApiRequest):
	'''
	A Superclass for all TradingApi Requests
	'''
	call_name = None
	request_name = None
	api_version = None
	message_id = None

	token = None
	namespace = "urn:ebay:apis:eBLBaseComponents"
	
	site_id = 100#Site ID for the eBay site you're using the TradingAPI for(default is 100[eBayMotors] )


	use_headers = False#True if we are to use headers and the xml header, False(default) otherwise
	use_token = False# True if we are to use the auth token in the request, False( default) otherwise
	
	has_item_container = ('AddItem', 'AddFixedPriceItem')#A list of all TradingApi calls that contain an <Item> container as their 'root' in their xml request

	headers = {
		#The subclass must set the first two...
		'X-EBAY-API-COMPATIBILITY-LEVEL': None,
		'X-EBAY-API-CALL-NAME': None,
		'X-EBAY-API-DEV-NAME' : None,
		'X-EBAY-API-APP-NAME' : None,
		'X-EBAY-API-CERT-NAME': None,
		'X-EBAY-API-SITEID'   : None,
		'Content-Type': "text/xml",
	}
	environment = 'sandbox' #Which eBay environment to connect to( either 'sandbox' or 'production' )
	
	ship_to_locations = ("AA","AD","AE","AF","AG","AI","AL","AM","AN","AO","AQ","AR","AS","AT","AU",
"AW","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BM","BN","BO","BR","BS","BT","BV","BW","BY","BZ",
"CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CU","CV","CX","CY","CZ","DE","DJ","DK","DM",
"DO","DZ","EC","EE","EG","EH","ER","ES","ET","FI","FJ","FK","FM","FO","FR","GA","GB","GD","GE","GF","GG","GH",
"GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GW","GY","HK","HM","HN","HR","HT","HU","ID","IE","IL","IN",
"IO","IQ","IR","IS","IT","JE","JM","JO","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ","LA","LB",
"LC","LI","LK","LR","LS","LT","LU","LV","LY","MA","MC","MD","ME","MG","MH","MK","ML","MM","MN","MO","MP","MQ",
"MR","MS","MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ","OM",
"PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY","QA","QM","QN","QO","QP","RE","RO","RS",
"RU","RW","SA","SB","SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","ST","SV","SY","SZ","TC",
"TD","TF","TG","TH","TJ","TK","TM","TN","TO","TP","TR","TT","TV","TW","TZ","UA","UG","UM","US","UY","UZ","VA",
"VC","VE","VG","VI","VN","VU","WF","WS","YE","YT","YU","ZA","ZM","ZW","ZZ", "Africa", "Americas", "Asia", 
"Caribbean", "Europe", "EuropeanUnion", "LatinAmerica", "MiddleEast", "NorthAmerica", "Oceania", "SouthAmerica",
"WillNotShip", "WorldWide")#List of acceptable shiptolocations as well as exclude locations
	
	shipping_types = ('Calculated', 'CalculatedDomesticFlatInternational', 'Flat', 'FlatDomesticCalculatedInternational')#List of acceptable values for shipping_types

	#A map of all TradingAPI dictionary keys to their XML tag names
	key_map = {
		'listing_type': 'ListingType',
		'picture_details': 'PictureDetails',
		'picture_url': 'PictureURL',
		'subtitle': 'SubTitle',
		'sku': 'SKU',
		'uuid': 'UUID',
		'description': 'Description',
		'buy_it_now_price': 'BuyItNowPrice',
		'condition_id': 'ConditionID',
		'category_mapping_allowed': 'CategoryMappingAllowed',
		'pay_pal_email_address': 'PayPalEmailAddress',
		'title': 'Title',
		'primary_category':'PrimaryCategory',
		'start_price': 'StartPrice',
		'dispatch_time_max': 'DispatchTimeMax',
		'listing_duration': 'ListingDuration',
		'payment_methods': 'PaymentMethods',
		'location': 'Location',
		'postal_code': 'PostalCode',
		'quantity': 'Quantity',
		'return_policy': 'ReturnPolicy',
		'shipping_details': 'ShippingDetails',
		'site': 'Site',
		'country': 'Country',
		'currency': 'Currency',
		'returns_accepted_option': 'ReturnsAcceptedOption',
		'refund_option': 'RefundOption',
		'returns_within_option': 'ReturnsWithinOption',
		'shipping_cost_paid_by_option': 'ShippingCostPaidByOption',
		'category_id': 'CategoryID',
		'shipping_type': 'ShippingType',
		'shipping_service_options': 'ShippingServiceOptions',
		'shipping_service': 'ShippingService',
		'shipping_service_cost': 'ShippingServiceCost',
		'shipping_service_priority': 'ShippingServicePriority',
		'international_shipping_service_option': "InternationalShippingServiceOption",
		'ship_to_location': "ShipToLocation",
		'exclude_ship_to_location': "ExcludeShipToLocation",
		'item_id': 'ItemID',
		'ending_reason': "EndingReason",
		'item': 'Item',
		'deleted_field': 'DeletedField',
		'item_specifics': 'ItemSpecifics',
		'name_value_list': 'NameValueList',
		'name': 'Name',
		'value': 'Value',
	}

	def __init__(self, headers=None, token=None):
		'''
		Args:
			headers[dict] A dictionary of ebay headers that should equal
			   "X-EBAY-API-DEV-NAME":  'developer_key'
			   "X-EBAY-API-APP-NAME":  'application_key'
			   "X-EBAY-API-CERT-NAME": 'certificate_key'
			   "X-EBAY-API-SITEID":    'site_id'
			   
			   The CALL-NAME and COMPATIBILITY-LEVEL will be set automatically
			   
			    Alternatively headers can be False (if this is for a bulk request, no headers will be calculated)
			    Or you can not define the headers argument and the GlobalConfiguration will be used

			token[str] The Ebay Auth Token needed for TradingApi Requests
		'''
		if(headers):
			print "Setting Headers"
			self.set_headers(headers)
			self.use_headers = True
		elif(headers == False):
			#explicitly don't use headers( used for bulk requests)
			print "Headers are false, not using headers"
			self.headers = False
		elif(headers is None):
			#Use global configuration
			print "Headers are None, Using GlobalConfiguration"
			self.set_headers(GlobalConfiguration.get_headers(self.environment))
			self.use_headers = True
		else:
			raise ValueError("Invalid value for argument 'headers'")
			
		if(isinstance(token,str)):
			if token in ['production', 'sandbox']:
				self.environment = token
				print "Token is %s, using GlobalConfiguration" % token
				self.set_token(GlobalConfiguration.get_token(self.environment))
				self.use_token = True
			else:
				print "Token is a string, setting it"
				self.set_token(token)
				self.use_token = True
		elif(token is None):
			print "Token is None, using GlobalConfiguration"
			self.set_token(GlobalConfiguration.get_token(self.environment))
			self.use_token = True
		elif(token == False):
			print "Token is False, not using a token"
			#No token xml will be added to the request (used for bulk requests)
			self.token = False
		else:
			raise ValueError("Invalid value for argument 'token'")

		if headers != False:
			self.set_header('X-EBAY-API-CALL-NAME', self.call_name)
			self.set_header('X-EBAY-API-COMPATIBILITY-LEVEL', self.api_version)
			self.set_header( 'X-EBAY-API-SITEID', self.site_id )

		EbayApiRequest.__init__( self )

	def set_token(self, token):
		print "Type: %s" % type( token )
		assert type(token) is str
		self.token = token
	
	def set_header(self, header, value):
		if(header not in self.headers.keys()):
			raise Exception("Uknown Header -> %s" % header)
		self.headers[header] = value
		
	def set_headers(self, headers):
		for key, val in headers.iteritems():
			print key, val
			self.set_header(key, val)
			
	def get_headers(self):
		return self.headers


class UnacceptableKeysError(Exception): pass




