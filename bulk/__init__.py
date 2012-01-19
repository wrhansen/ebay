from lxml import etree
import os.path
import zlib
import sys
from ebay import EbayApiRequest


class BulkDataFile(EbayApiRequest):
	'''
	Manages Bulk Data File Creation - the Data portion of the BulkDataExchange
	request his managed here.  You don't *HAVE* to use this class in order to
	use the BulkDataExchange Python API - however it is suggested!
	
	This file can also wrap a Bulk Data File that has been downloaded to provide
	ease of access
	
	Does not manage compression	
	'''
	
	api_version = None #Must be same as the version of the calls inside
	request_name = 'BulkDataExchangeRequests'
	container_request_type = None  # Holds the name of the request type being created for this - we will determine this based on the first element appended
	namespace = '{urn:ebay:apis:eBLBaseComponents}'
	write_mode = False#True if file is open in a 'write' mode, False otherwise(default)
	first_write = None#True if file needs to be truncated and overwritten, False otherwise
	bytes_written = 0
	missing_foot = False #True if container foot was removed( on an append )
	mode = 'r'#Save the file pointer mode( default is r )
	REQUEST = 'Request'
	RESPONSE = 'Response'
	fp = None
	max_file_size = 1024 * 1024 * 15 #Maximum BulkDataFile size is 15MB
	
	trading_api_calls = ('AddItem', 'AddFixedPriceItem', 'EndFixedPriceItem', 'EndItem',
						  'RelistFixedPriceItem', 'RelistItem',
						  'ReviseFixedPriceItem','ReviseItem', 'ReviseInventoryStatus',
						  'UploadSiteHostedPictures', 'VerifyAddFixedPriceItem', 'VerifyAddItem') # <-- Use this to validate the different api calls
	merchant_data_api_calls = ( 'SetShipmentTrackingInfo', 'ActiveInventoryReport', 'FeeSettlementReport', 'OrderAck', 'SoldReport' )#<--Non-Trading API calls
	def __init__(self, call_type, file_type='Response', api_version=None, site_id=None):
		'''
		Create a BulkDataFile object with the given call_type, file_type and optional
		api_version and site_id. If the api_version and site_id are not supplied,
		then the file cannot be opened in read/write mode( Generally only do this
		if you're creating a BulkDataFile to read a Response file.)
		
		Args:
			call_type[str]: A string representing what calls will be added to the BulkDataFile.
			The accepted call_types are stored in trading_api_calls and 
			merchant_data_api_calls.
			file_type[str]: Either 'Requests', or 'Responses'--Tells the BulkDataFile whether
			you're reading responses, or reading/writing requests.
			(Optional)api_version[str]: The version of the API call, must be the 
			same version throughout the entire BulkDataFile. Must supply this if creating
			a BulkDataFile in 'Request' mode
			(Optional)site_id[str]: The eBay site ID you're connecting to. Must supply
			the site_id if creating a BulkDataFile in 'Request' mode
		'''
		
		if self._valid_call_type( call_type ):
			if file_type in [self.REQUEST, self.RESPONSE]:
				self.fp = None
				self.site_id = site_id
				self.api_version = api_version
				self.container_request_type = call_type
				self.file_type = file_type
			else:
				raise ValueError( "Incorrect file type! File Type must be one of: [%s, %s]" % (self.REQUEST, self.RESPONSE ) )
		
		else:
			raise ValueError( "Call Type is not supported! Supported Trading API calls:%s\nSupported Merchant Data API calls:%s" % (self.trading_api_calls, self.merchant_data_api_calls ) )
			
	def _valid_file_type( self, file_type, mode ):
		'''
		Check if file type is acceptable with the given mode
		'''
		if file_type == 'Request':
			if self.container_request_type in self.trading_api_calls:
				return True
			return False
		elif file_type == 'Response':
			if mode is not 'r':
				return False
		return True
			

	def _valid_call_type( self, call_type ):
		'''
		Check if call type is accepted. Returns True if it is, False otherwise
		'''
		if call_type in self.trading_api_calls or call_type in self.merchant_data_api_calls:
			return True
		return False
		
	def _get_container_head(self):
		args = {
			'xml_header': self.xml_header, #Inherited from EbayApiRequest
			'request_name': self.request_name,
			'site_id': self.site_id,
			'version': self.api_version
		}
		return '''{xml_header}
					<{request_name}>
					<Header>
						<SiteID>{site_id}</SiteID>
						<Version>{version}</Version>
					</Header>
		'''.format(**args).replace('\t', '')
		
	def _get_container_foot(self):
		return '''</%s>''' % self.request_name
		
	def _init_file(self):
		'''
		adds header information to the file
		Overwriting the contents of the file( and truncating the rest)
		'''
		self.fp.seek(0)
		head = "%s\n" % self._get_container_head()
		self.fp.write(head)
		self.bytes_written = len(head)
		self.fp.truncate( self.fp.tell() )#Truncate the file
		self.write_pos = self.fp.tell()
		self.missing_foot = True
		
	def _parse_request_type(self, string):
		'''
		Parse the request type out of a string
		<ReviseInventoryStatusRequest> ... etc
		'''
		valid = list(self.trading_api_calls)
		valid.extend(self.merchant_data_api_calls)
		for rtype in valid:
			if("%sRequest" % rtype in string):
				return rtype
		raise ValueError("Your Api Request does not contain a supported Merchant Data or Trading API Call\n  Supported Trading API Calls: %s\n  Supported Merchant Data API Calls: %s" % (self.trading_api_calls, self.merchant_data_api_calls))

	def close(self):
		if self.fp:
			if self.missing_foot:
				foot = self._get_container_foot()
				self.fp.write(foot)
				self.bytes_written += len(foot)
				self.missing_foot = False
			self.write_pos = self.fp.tell()
			self.fp.close()

	def open(self, path, mode='r'):
		'''
		Open a BulkDataFile for writing or reading
		
		Args:
			path[str] The Path where we should save the file.
			mode[str] 'r' for ReadOnly or 'w'/'r+' for Read and Write
		'''
		
		# WES - HERE ARE SOME TODO'S FOR THIS SECTION OF LOGIC...
		# LOGIC BELOW NEEDS TO BE FIXED.
		# WE ALWAYS OPEN IN READ/WRITE MODE EVEN IF WRITE MODE IS REQUESTED
		# IF WRITE MODE / READ+WRITE IS REQUESTED AND THE FILE ALREADY EXISTS
		# And you aren't opening in READ-ONLY or APPEND modes we need to 
		# truncate the file after opening it. 
		# TO OPEN IN READ/WRITE (r+) The file must already exist
		# .......
		# Now For implementing the APPEND modes, we need to make sure we don't
		# truncate the file, and we delete the last line, and set the write_pos
		# correctly!
		#
		# For READ-ONLY mode, we just need to make sure we open the file and
		# don't WRITE to it at all
		
		truncate = False
		exists = False
		#APPEND MODE
		if('a' in mode ):
			self.mode = 'a'
			if os.path.isfile( path ):
				exists = True
	
		#If a write mode is chosen, always open in r+ mode
		elif(mode in ('w', 'r+')):
			if(not os.path.isfile(path)):
				open( path, 'w').close()#Create the file since it doesn't exist
			else:
				exists = True

			self.mode = 'r+'#If write mode is chosen, always be in read-and-write mode
			self.write_pos = 0

		#If read is chosen, do not allow any writing at all
		elif('r' in mode):
			self.mode = 'r'
			self.write_pos = None#Do not write at all
			exists = True

		else:
			raise IOError("Unsupported mode %s - The modes (r, w, r+, a) are supported" % mode)
		
		#Check that selected mode is acceptable for the file-mode
		#Requests must be a certain type( Trading API calls)
		#Responses can be any call in trading_api_calls and merchant_data_api_calls
		if not self._valid_file_type( self.file_type, self.mode ):
			raise IOError( "File Type %s cannot be used in %s mode\nAccepted calls are: %s"%(self.file_type, self.mode, self.trading_api_calls))
	
		#Open the file at 'path' in the given 'mode'
		self.fp = open(path, self.mode)
		self.filepath = path
		
		#File exists, so get the size and set bytes_written
		if exists:
			self._get_file_size()
			
		#Initialize the file with new headers
		if('r+' == self.mode):
			self.write_mode = True
			self.first_write = True
			#CHANGED: self._init_file() should be called just before the first write
			#To allow for the file to read first if needed
			#self._init_file()
		elif( 'a' == self.mode ):
			#Set the write position to the end of the file
			#Shouldn't HAVE to do this, but it's OS dependent
			self.fp.seek( 0, os.SEEK_END )
			self.write_mode = True
			self.first_write = True
			self.write_pos = self.fp.tell()


	def _get_file_size( self ):
		'''
		When the file is first opened, and the file already exists, this function
		reads in the file, a chunk at a time, and records the file size
		'''
		assert self.fp #Must be a valid file pointer
		size = 0
		seek_pos = self.fp.tell()
		self.fp.seek(0)
		fp = open( self.filepath, 'r' )
		fp.seek(0)
		while True:
			line = fp.readline()
			if len( line ) == 0:
				break
			size += len( line )
		fp.close()
		self.bytes_written = size
		#print "Bytes: %s" % self.bytes_written
		self.fp.seek( seek_pos )

	def _delete_container_foot(self, filepath):
		'''
		Remove the container's foot from given filepath. The foot in this file is
		</BulkDataExchangeRequests>
		This method also will remove any extra lines or garbage at the end of the file and
		will raise an error if this field doesn't exist in file.
		This function is used when a file is opened in append mode
		
		Args:
			filepath[string]: the path of the file to be opened
		'''
		found_it = False
		fp = open( filepath, 'r+' )#Cannot truncate in read-only mode
		find_string = '</%s>' % self.request_name#<--String to search for
		iteration = -1#The number of bytes to search( negative for reading from end of file)
		size = 1#Check each byte
		while not found_it:
			try:
				fp.seek( size*iteration, os.SEEK_END )#Seek from the end, 'size' bytes at a time
				offset = fp.tell()
				line = fp.readline()
				#If not found, keep parsing
				if find_string not in line:
					iteration -=1
				#Found the foot, calculate the position to truncate
				else:
					lineoffset = line.find( find_string )
					found_it = True
					fp.truncate( offset + lineoffset )#Truncate the file at the foot
					self.missing_foot = True
			except:
				raise IOError( "Incorrect Formatting: This file doesn't contain proper ending" )
		fp.close()

	def write(self, data):
		'''
		Writes string data directly to file
		'''
		#Overwrite the contents of the file first with the header info, then truncate the rest
		if self.first_write == True:
			if self.mode == 'r+':
				self._init_file()
				self.missing_foot = True
				self.first_write = False
			elif self.mode == 'a':
				print "Missing foot: %s" % self.missing_foot
				if self.missing_foot == False:
					self._delete_container_foot( self.filepath )
				
		if('BulkDataExchangeRequests' in data):
			raise ValueError("You do not need to define container elements for this file, this is done for you!")
			
		if(self.write_pos is not None):
			self.fp.seek(self.write_pos)
		else:
			raise IOError("File mode does not support writing, or open() has not been called!")
		
		#Don't write to file if the size will be greater than the max_file_size
		projected_file_size = self.bytes_written + len( '</BulkDataExchangeRequests>' ) + len( data )
		if projected_file_size <= self.max_file_size:
			self.fp.write(data)
			self.write_pos = self.fp.tell()
			self.bytes_written += len(data)
		else:
			raise ApiFileSizeLimitError( "FileSizeError:Projected File Size <%s> is greater than the limit <%s> , Failed Write" % (projected_file_size, self.max_file_size ) )
	
	def seek(self, pos):
		self.fp.seek(pos)
	
	def append(self, xml):
		'''
		xml can be a TradingApiCall, A String, or a XML Dom Object, or a File-Like Object
		'''
		#If we've received a string verify it has an <xml> header on the first line
		#and then verify a SomethingSomethingRequest element immediately follows
		#The request name that is found is stored in self.container_request_type
		#and all subsequent calls to this method MUST contain the same request name
		#The exception raised should be RequestTypeMixed
		if(isinstance(xml, basestring)):
			xmlstr = xml
		elif(isinstance(xml, etree._Element)):
			xmlstr = etree.tostring(xml, pretty_print=False)
		elif(isinstance(xml, TradingApiRequest)):
			xmlstr = etree.tostring(xml.get_element(), pretty_print=True)
		else:
			raise ValueError("xml is not a supported argument type, expected one of (basestring, lxml.etree.Element, ebay.trading.TradingApiRequest")
			
		request_type = self._parse_request_type(xmlstr) # Error gets raised here if it can't determine or improper request type...
		#Now make sure the detected request type is the same request type they told us they were going to be doing.
		if(self.container_request_type  != request_type):
			raise ValueError("CallType must equal the call type passed to init - '%s' - You may not mix-and-match call-types for bulk api requests - they all must be of the same type!" % self.container_request_type)
		self.write(xmlstr+"\n")
			
		
	def __iter__(self):
		'''
		Returns file <request></request> by <request></request> (strings)
		'''
		for element in self.iterparse():
			yield etree.tostring(element, pretty_print=True).strip()
			
	def iterparse(self):
		'''
		Calls lxml.etree.iterparse() - returns each call element one by one
		'''
		#Make sure fp is a file-like object that is open
		assert not self.fp.closed
		#If file is in an incomplete state, finalize it first
		if self.missing_foot:
			foot = self._get_container_foot()
			self.fp.write(foot)
			self.bytes_written += len(foot)
			self.write_pos = self.fp.tell()
			self.first_write = True
			self.missing_foot = False
			
		last_pos = self.fp.tell()
		tag_name = self.namespace + self.container_request_type + self.file_type
		parse_fp = open( self.filepath, 'r' )#etree.iterparse closes file pointer after parsing, so must create a separate file pointer to parse
		#Iterparse the file object and yield the element with tag of container_request_type
		for event, element in etree.iterparse( parse_fp, events=['start','end'], tag=tag_name ):
			fp_pos = self.fp.tell()
			in_tree = False #Determine what state of the tree you're in
			if(fp_pos < last_pos):
				raise IOError("File-Pointer Seek during iteration!  The internal file-pointer was moved during iteration - this is not allowed! Please ensure you are not writing, or reading during this iteration")
			#Detect start event
			if event ==  'start':
				yield element
				in_tree = True
			#Detect end event
			if event == 'end':
				in_tree = False
			#Detect in-between state
			if not in_tree and event not in ['start','end']:
				element.clear()#Free the memory of this element
				#Clean up preceding siblings to free up even more memory
				while element.getprevious() is not None:
					del element.getparent()[0]
			last_pos = fp_pos
		
	
	def __hash__(self):
		'''
		Return an Adler32 hash of this file - use this hash to compare file
		for changes.
		'''
		hash_string = 0
		assert self.fp
		seek_pos = self.fp.tell()
		self.fp.seek( 0 )
		fp = open( self.filepath, 'r' )
		while True:
			line = fp.readline()
			if len( line ) == 0:
				break
			baby_hash = zlib.adler32( line )
			hash_string += baby_hash
		fp.close()
		self.fp.seek( seek_pos )
		return hash_string
	
	def __len__(self):
		'''
		Returns the number of request elements in this file
		'''
		return len([True for item in self.iterparse()])
		
	def bytes(self):
		'''
		Returns the size of the file
		Max File Size is 15MB ( stored in self.max_file_size)
		'''
		return self.bytes_written

	def __repr__(self):
		'''
		String representation of BulkDataFile that looks like this:
			<BulkDataFile size:hash:elements request_type>
		Where:
			size		: size of file in bytes,
			hash		: adler32 hash of file
			elements	: number of requests in file
			request_type: name of the api call in the file
		'''
		reprs = {
			'size' : self.bytes_written,
			'hash' : hash( self ),
			'elements' : len( self ),
			'request_type' : self.container_request_type
		}
		
		repr_string = '<BulkDataFile {size}:{hash}:{elements} {request_type}>'
		return repr_string.format( **reprs )
		
	def __del__(self):
		if self.fp:
			if( not self.fp.closed ):
				self.close()
				
				
class ApiFileSizeLimitError( Exception ):
	'''
	Exception raised by BulkDataFile when appending to the file has reached its
	maximum file size
	'''
	def __init__( self, message):
		print "%s: %s" % (self.__class__.__name__, message)

