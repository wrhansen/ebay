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

'''
The superclass that all Ebay Api's will inherit from.
So this class will contain data and functions that are generic
to all of Ebay's API's
'''

__author__ = ["Ben DeMott", "Wesley Hansen"]

import httplib
from lxml import etree
import sys
import os.path
import uuid
import traceback
import simplejson

class EbayApiRequest():
	'''
	Holds some information global to all Ebay Requests
	'''
	xml_header = '''<?xml version="1.0" encoding="UTF-8"?>'''
	validated = False #<---True if data has been updated and validated, False otherwise
	error_language = 'en_US' #xml request info(en_US by default)
	warning_level = 'High' #xml request info(High by default)
	site_id = 100 #Site ID for the eBay site you're using the EbayApiRequest for(default is 100[eBayMotors])

	tree = None #<--- The root etree._Element created from _build()
	data = {} #<---This is the container for all of the fields that will go into building the <Item> container

	def __init__(self):
		'''
		Initialize data structures, and set variable defaults
		'''
		self.tree = None
		self.data = {}
		self.validated = False
		self.error_language = 'en_US'
		self.warning_level = 'High'
		self.site_id = 100
		
		
	def get_element(self):
		'''
		Retrieve the XML node of the assembled request
		In order to retrieve an element, data must be updated and validated
		'''
		if not self.validated:
			raise DataNotValidatedError( "Data Not Validated: Validate the data by calling update()" )
			
		#Build the xml request from the given data
		self._build( self.data )
		
		#Return the xml node (etree._Element)
		return self.tree

	def get_data(self):
		'''
		Returns the underlying data structure
		'''
		return self.data
	def generate_message_id(self):
		return 
		
	def get_message_id(self):
		return self.message_id
	
	def set_message_id( self, message):
		'''
		Set the MessageID field of the TradingAPI request
		By default, requests do not include a MessageID.
		
		Args:
			message[str]: The message you'd like the attach to the request within the MessageID field
		'''
		self.message_id = message
	
	def set_error_language( self, language ):
		'''
		Set the ErrorLanguage field of the TradingAPI request
		By default, ErrorLanguage is set to 'en_US'
		Reference: http://developer.ebay.com/DevZone/xml/docs/WebHelp/wwhelp/wwhimpl/js/html/wwhelp.htm?href=InvokingWebServices-.html
		
		Args:
			language[str]: language Identification tag as specified by eBay's documentation
		'''
		self.error_language = language
		
	def set_warning_level( self, level ):
		'''
		Set the WarningLevel field of the TradingAPI request
		By default, WarningLevel is set to 'High'
		
		Args:
			level[str]: What level you want to set Warning Level to
		'''
		self.warning_level = level
		
	def update(self, update):
		'''
		Set request data - This is how you set data to form the request!
		
		The keys that you can set are indicated by calling the help() method
		of this class
		'''
		if isinstance( update, dict ):
			#Update a dictionary into data
		
			#Resolve the dotted keys, dropping the dots and adding levels to the dictionary
			#update = self._manage_dot_keys(update)
			update = self._resolve_dottedkeys( update )
			
			#Update the dictionary, overwriting values if the keys exist
			for key,value in update.iteritems():
				self.data.update( {key:value} )

			exceptions = []
			exception_keys = []
			for key, val in update.iteritems():
				try:
					self._validate(key, val)
				except Exception as e:
					#traceback.print_exc()
					exceptions.append(e)
					exception_keys.append(key)
			
			if(exceptions):
				if(len(exceptions) == 1):
					self._validate(exception_keys[0], update[exception_keys[0]]) # <-- There is only one exception, so have it raise itself inline (is this the best way to do this???)	
				else:
					raise MultipleUpdateErrors(exception_keys,exceptions)
			
	
			# Support updating keys either way:
			# ----------------------------------------------
			#   data['PrimaryCategory']['CategoryID'] = 377
			#   data['PrimaryCategory.CategoryID'] = 377
			
			self.validated = True #Successfully Validated `data`
		
		else:
			raise UpdateDataError( "Incorrect update parameters, must pass a dictionary")
			
	def _resolve_dottedkeys(self, data):
		"""
		Resolves dotted keys within a dictionary.
	
		Arguments:
		- data (`dict`)
		  - The data.

		Returns:
		- The data (`dict`) with the dotted keys resolved.
		"""

		# Find dotted keys.
		dotted = dict((key, value) for key, value in data.iteritems() if '.' in key)
	
		# Remove dotted keys.
		data = dict((key, value) for key, value in data.iteritems() if '.' not in key)
	
		# Resolve dotted keys.
		for key, value in dotted.iteritems():
			parts = key.split('.')
			end = len(parts) - 1
			sub = data
			for i, part in enumerate(parts):
				if i == end:
					if part not in sub:
						print "part not in sub"
						sub[part] = value
					elif isinstance(sub[part], list):
						print "it's a list, appending"
						sub[part].append(value)
					else:
						print "creating list"
						sub[part] = [sub[part], value]
				elif part in sub:
					if isinstance(sub[part], dict):
						sub = sub[part]
					else:
						raise ValueError("Cannot nest %r at %r because %r is %r." % (value, key, '.'.join(parts[:i+1]), sub[part]))
				else:
					sub[part] = {}
					sub = sub[part]
	
		return data

	def _validate_request(self, data=None):
		'''
		Validate the overall request before it's generated / sent
		Check that all toplevel keys are acceptable
		Check that data contains all required keys at least
		'''
		#Validate self.data or validate data passed to this function
		if not data:
			data = self.data
		
		#Handle 'OR'd' keys i.e.: "postal_code|location"
		#Split them into separate keys, and add to accepted_keys
		#		ALSO
		#Add keys to required, including the split keys
		#separate keys into a list of or_pair sets for subset testing
		accepted_keys = set() #A set of all acceptable keys
		required = set() #A set of all required keys( or-pairs are split off
		or_pairs = []#A list of all or-pair key sets
		
		#Populate accepted_keys, required, and or_pairs
		for key in self.required_keys:
			if "|" in key:
				split_list = key.split( "|" )
				or_pairs.append( set( split_list) )
				for split_key in split_list:
					accepted_keys.add(split_key)
					required.add( split_key)			
			else:
				accepted_keys.add(key)
				required.add( key )
		
		accepted_keys |= set(self.other_keys)
		#Ensure that all keys used are acceptable
		unacceptable = set( data.keys()) - set( accepted_keys)
		if len( unacceptable):
			raise InvalidRequest( "These keys are not acceptable %s" % list( unacceptable ) )

		#Ensure all required keys are present
		missing = required - set(data.keys())
		key_pairs = []#<--A list of or-pair keys to add to missing
		remove_pairs = []#<-- A list of keys to remove from missing
		for pair in or_pairs:
			if pair.issubset( missing ):
				#Pair was not in self.data, add to missing
				or_string = ""
				for element in pair:
					or_string += element + "|"
				key_pairs.append( or_string.strip('|') )
			
			#Always remove the un-or'd elements from missing
			for element in pair:
				remove_pairs.append( element )

		#Add or-pairs to missing that weren't included in data
		for pair in key_pairs:
			missing.add( pair )
		#Remove or-pair keys from missing that were included in data
		for key in remove_pairs:
			missing.discard(key)
			
		if(len(missing)):
			raise InvalidRequest("These required keys have not been set - %s" % list(missing))
		
	def _validate(self, key, val):
		'''
		Validate the data structure of a top-level key
		
		This validates the structure by each top-level key.
		'''
		
		accepted_keys = set(self.other_keys) | set(self.required_keys)
		if key in accepted_keys:
			fn = getattr(self, '_validate_'+key, None)
			if(not fn):
				return
		
			return fn(val)
		
		
	def _build(self, data):
		'''
		take request data structure and turn it into a DOM object
		
		Args:
			data[dict]: A dictionary containing the information for the <Item>
			container of the xml request. At this point it will be validated and
			corrected, so this function will simply build the request.
		'''
		
		self._validate_request( data )
		#Create the root of the request with the given namespace
		root = etree.Element( "{%s}%s" % (self.namespace, self.request_name ), nsmap={None: self.namespace} )
		
		#Build other additional things:
		#ErrorLanguage
		if self.error_language:
			error = etree.SubElement( root, "ErrorLanguage")
			error.text = self.error_language
		else:
			#ErrorLanguage is required, so raise exception
			raise InvalidTopLevelRequest( "InvalidTopLevelRequest: Must include an Error Language" )
		
		#WarningLevel
		if self.warning_level:
			warning = etree.SubElement( root, "WarningLevel" )
			warning.text = self.warning_level
		else:
			#WarningLevel is required so raise exception
			raise InvalidTopLevelRequest( "InvalidTopLevelRequest: Must include a Warning Level" )

		#MessageID
		if self.message_id:
			message = etree.SubElement( root, "MessageID" )
			message.text = self.message_id
		
		#Version
		if self.api_version:
			version = etree.SubElement( root, "Version" )
			version.text = str(self.api_version)
		else:
			#Version is required so raise an exception
			raise InvalidTopLevelRequest( "InvalidTopLevelRequest: Must include a Version" )

		#RequestCredentials
		if self.token:
			requester_credentials = etree.SubElement( root, "RequesterCredentials" )
			ebay_token = etree.SubElement( requester_credentials, "eBayAuthToken")
			ebay_token.text = self.token

		#Build Item element
		if isinstance( data, dict ):
			if self.call_name in self.has_item_container:
				item = etree.SubElement( root, "Item" )
				self._build_item_container( item, data )
			else:
				self._build_item_container( root, data )
		else:
			#Must have an item to build, raise exception
			raise InvalidRequestData( "InvalidRequestData: Data must be a dict, not a: %r" % data )
			
		#print etree.tostring( root, pretty_print = True )
		#Set the tree to root--This will be returned by a call to get_element()
		self.tree = root
			
	def _build_item_container( self, element, data, key=None):
		'''
		Parses the given data, creating an element out of each key:value
		pair it finds and appends it to element.
		If a value of data is a list, it creates an element for each value in the list, recursively calling
		this function for each value in the list that is either another list or a dictionary.
		If a value of data is a dictionary, a recursive call to this function is called
		with element being the element created with that key, and data being that dictionary found
		at value
		
			Ex: Where <Item/> is element:
				1) data = {'a': 'b'}  ---> 	<Item>
												<a>b</a>
											</Item>
											
				2) data = {'a': ['b','c']} --> 	<Item>
													<a>b</a>
													<a>c</a>
												</Item>
												
				3) data = {'a': { 'b': 'c'}} --->	<Item>
														<a>
															<b>c</b>
														</a>
													</Item>
		Args:
			element[etree._Element]: The root element to append the new elements to
			data[dict]: Elements are created such that key is an xml tag, and value is the text field
		'''
		if not isinstance( element, etree._Element ):
			raise InvalidElementError( "InvalidElementError: element must be a valid etree._Element, instead element is %r" % element )

		if isinstance( data, dict ):
			for key, value in data.iteritems():
				if isinstance( value, basestring ) or isinstance( value, int ) or isinstance( value, float ):
					#Create element, append to base element
					key_string = self.key_map[key]#<---Grab the key-map string to create a properly formatted eBay field
					new_elem = etree.SubElement( element, key_string )
					new_elem.text = str(value)
				elif isinstance( value, list ):
					#Create a list of elements, appending them each to the base element
					self._build_item_container( element, (key,value))

				elif isinstance( value, dict ):
					#Create an element of `key` appending to base 'element'
					#Recursively call _build_item_container with 'key', as element, and value as data
					key_string = self.key_map[key]
					new_elem = etree.SubElement( element,key_string)
					self._build_item_container( new_elem, value )
			
				else:
					raise InvalidDataType( "InvalidDataType: a value can be a string, a float, an int, a list, or a dict...not a %r" % value )
		elif isinstance( data, tuple ):
			key, value = data
			for item in value:
				if isinstance( item, basestring ) or isinstance( item, int ) or isinstance( item, float ):
					#Create element, append to base element
					key_string = self.key_map[key]#<---Grab the key-map string to create a properly formatted eBay field
					new_elem = etree.SubElement( element, key_string )
					new_elem.text = str(item)

				elif isinstance( item, list ):
					#Create a list of elements, appending them each to the base element
					self._build_item_container( element, (key,item))

				elif isinstance( item, dict ):
					#Create an element of `key` appending to base 'element'
					#Recursively call _build_item_container with 'key', as element, and value as data
					key_string = self.key_map[key]
					new_elem = etree.SubElement( element,key_string)
					self._build_item_container( new_elem, item )
			
				else:
					raise InvalidDataType( "InvalidDataType: a value can be a string, a float, an int, a list, or a dict...not a %r" % value )
		else:
			raise InvalidDataType( "InvalidDataType: a value can be a string, a float, an int, a list, or a dict...not a %r" % value )

	def prettyprint(self):
		'''
		Call get_element() and pretty print it - all child classes must implement a get_element() method
		'''
		if self.tree is None:
			print ''
		else:
			print etree.tostring( self.tree, pretty_print=True )

	def help(self):
		'''
		Returns information about the expected structure and possible keys that
		can be set.
		
		Each sub class must override the self.help_string with
		information regarding their 
		'''
		return self.help_string
		
	def __repr__(self):
		'''
		Returns a representation of the data... which will be information about
		the call as well as the xml.
		'''
		return str( self )#XXX
		
	def __str__(self):
		'''
		Returns the string XML for this specific call
		
	<?xml version="1.0" encoding="utf-8"?>
	<AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
	  <!-- Standard Input Fields -->
	  <ErrorHandling> ErrorHandlingCodeType </ErrorHandling>
	  <ErrorLanguage> string </ErrorLanguage>
	  <MessageID> string </MessageID>
	  <Version> string </Version>
	  <WarningLevel> WarningLevelCodeType </WarningLevel>
	  <!-- Call-specific Input Fields -->
	  <Item> ItemType
		'''
		if self.tree is None:
			return ''
		else:
			return etree.tostring( self.tree, pretty_print=False )


class EbayAPIConnection():
	'''
	Creates a connection to an eBay API and has the ability to send a request, and
	retrieve a response
	'''
	headers = None
	url = None
	location = None
	connection = None
	filename = "/home/wes/it/Development/projects/python/ebay/api_tests/LMS_API/bulk_api_layout/api_credentials.json"#TODO: THIS MUST BE CONFIGURED ON INSTALL
	token = None#Auth token: ONLY USED WITH GLOBAL CONFIGURATION
	
	api_map = {
		"TradingApiRequest": "trading_api",
	}#Maps the request class name to the name found in the credentials structure
	
	request_object = None#True if connection was created with an EbayApiRequest object, False otherwise
	
	def __init__( self, headers=None, api=None, environment=None, request=None ):
		'''
		Creates an APIConnection object with the given headers, api, and environment
		by reading the api_credentials.json structure to get all of the necessary
		information to where to connect and how
		
		Args:
			headers[dict]: all the necessary headers generated from the EbayApiRequest object
			api[string]: the name of the eBay API being connected to
			environment[string]: Which environment the API is connecting to:
			request
			Either "sandbox" or "production"
			request[EbayApiRequest]: Use the information it holds to determine the headers, api, and
			environment
		'''
		if request:
			if not isinstance(request, EbayApiRequest ):
				raise InvalidRequestError( "request must be a valid EbayApiRequest object" )
			self.request_object = request.get_element()
			environment = request.environment
			api = None
			for key in self.api_map:
				if key in str(request.__class__.__bases__):
					api = self.api_map[key]
			if not api:
				raise InvalidRequestError( "request is not correctly mapped to credentials" )
				
			#Read api_credentials.json structure
			#And attempt to get the correct information
			self.headers = request.headers
			self._get_credentials( api, environment )
		

			#Determine if the connection is http or https and create the connection
			split_url = self.url.strip().partition( "://" )
			connection_protocol = split_url[0]
			url = split_url[2]
			#print connection_protocol
			if connection_protocol == 'http':
				self.connection = httplib.HTTPConnection( url )
			elif connection_protocol == 'https':
				self.connection = httplib.HTTPSConnection( url )
			else:
				raise InvalidConnectionProtocolError( "Invalid Connection Protocol: accepted protocols are: HTTP and HTTPS" )
			
			
		elif not headers and not api and environment:
			fp = open( self.filename, mode='r' )
			credentials = simplejson.load( fp )
			fp.close()
			self.token = credentials['_keys'][environment]['auth_token']
			
			
		else:
			#Set headers
			if headers:
				self.headers = headers
			else:
				self.headers = {}
				#raise ImproperHeadersError( "Must supply valid Headers, they cannot be NoneType!" )
		
			#Check environment is correct
			if environment.lower() in ['production', 'sandbox']:
				self.environment = environment.lower()
			else:
				raise IncorrectEnvironmentError( "Incorrect environment, acceptable environments are 'production' or 'sandbox'" )
			
			#Read api_credentials.json structure
			#And attempt to get the correct information
			self._get_credentials( api, self.environment )
		

			#Determine if the connection is http or https and create the connection
			split_url = self.url.strip().partition( "://" )
			connection_protocol = split_url[0]
			url = split_url[2]
			#print connection_protocol
			if connection_protocol == 'http':
				self.connection = httplib.HTTPConnection( url, timeout=30 )
			elif connection_protocol == 'https':
				self.connection = httplib.HTTPSConnection( url, timeout=30 )
			else:
				raise InvalidConnectionProtocolError( "Invalid Connection Protocol: accepted protocols are: HTTP and HTTPS" )
			

	def _get_credentials( self, api, environment ):
		'''
		Read the api_credendtials.json structure and grab the required information
		to create the connection for the given api in the given environment
		Also sets any extra headers that may be needed for the given api
		Args:
			api[string]: the name of the eBay API being connected to
			environment[string]: Which environment the API is connecting to
		'''
		fp = open( self.filename, mode='r' )
		credentials = simplejson.load( fp )
		fp.close()
		#Check that api is valid
		if api not in credentials.keys():
			raise InvalidAPIError( "Invalid API specified\nAcceptable APIs are: %s" % [key for key in credentials.keys() if key is not '_keys'])
		else:
			#Grab the url and location from credentials struct		
			self.url = credentials[api].get(environment, {}).get("url", None )
			self.location = credentials[api].get(environment, {}).get('location', None )
			
			if not self.url:
				raise InvalidCredentialsError( "InvalidCredentialsError: URL invalid")
			if not self.location:
				raise InvalidCredentialsError( "InvalidCredentialsError: Location invalid" )
			
			#Grab the correct header information
			keys = credentials.get( '_keys', None )
			if not keys:
				raise InvalidCredentialsError( "InvalidCredentialsError: '_keys' is missing" )
			
			headers = credentials[api].get('_extra_headers', None )
			if not headers:
				raise InvalidCredentialsError( "InvalidCredentialsError: _extra_headers is missing")
			#Add the extra headers to self.headers
			for key,value in headers.iteritems():
				self.headers[key] = keys[environment][value]
				
	def send_request( self, request=None ):
		'''
		Sends the request over the connection that was created to the appropriate eBay
		server
		
		Args:
			request[string]: The xml string request that the eBay server is expecting
			for the given api call
			Note: This object is not responsible for validating that the request is
			properly built. That is done in the EbayApiRequest object for the specific
			call.
		'''
		assert self.connection
		if isinstance( request, basestring ):
			request = request
		elif isinstance( request, EbayApiRequest ):
			request = etree.tostring(request.get_element(), pretty_print=False, xml_declaration=True, encoding='UTF-8')
		else:
			if self.request_object is not None:
				request = etree.tostring( self.request_object, pretty_print=False, xml_declaration=True, encoding='UTF-8' )
			else:
				raise InvalidRequestError( "Request type is invalid\nAcceptable request types are: %s" % list( basestring,EbayApiRequest) )
		
		self.connection.request( "POST", self.location, request, self.headers )
		
	
	def get_response( self ):
		'''
		Returns the response recieved from the eBay server after accepting a request
		'''
		assert self.connection
		self.response = self.connection.getresponse()
		if self.response.status != 200:
			raise ConnectionError( "Error sending request: %s" % self.response.reason )
		else:
			return self.response
			
	def close_connection( self ):
		'''
		Closes the connection, Should only call this if connection is open
		'''
		assert self.connection
		self.connection.close()

class InvalidRequest(Exception):
	pass

class InvalidElementError( Exception ):
	pass

class MultipleUpdateErrors( Exception ):

	def __init__(self,keys,exceptions):
	
		print '#'*30
		print '# Key Errors:'
		for idx,exception in enumerate(exceptions):
			print "#  Key: %s, Error: %r" %(keys[idx],exception)
		print '#' * 30


class InvalidApiKey( Exception ):
	pass

class DataNotValidatedError( Exception ):
	pass

class UpdateDataError( Exception ):
	pass

class InvalidTopLevelRequest( Exception ):
	pass

class InvalidDataType( Exception ):
	pass

class ImproperHeadersError( Exception ):
	pass

class IncorrectEnvironmentError( Exception ):
	pass
	
class InvalidConnectionProtocolError( Exception ):
	pass

class InvalidAPIError( Exception ):
	pass
	
class InvalidCredentialsError( Exception ):
	pass

class InvalidRequestError( Exception ):
	pass

class ConnectionError( Exception ):
	pass


