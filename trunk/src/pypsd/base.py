import unittest
import logging
import io
import os.path

module_logger = logging.getLogger("pypsd.base")

def bytesToInt(bytes):
	shift = 0
	value = 0
	bb = reversed(bytes)
	for b in bb:
		value += (b << shift)
		shift += 8

	module_logger.debug("bytesToInt method. In: %s, out: %s" % (bytes, value))
	return value

def int2Binary(n):
	'''convert denary integer n to binary string bStr'''

	bStr = ''
	if n < 0: raise ValueError ("must be a positive integer")
	if n == 0: return '0'
	while n > 0:
		bStr = str(n % 2) + bStr
		n = n >> 1

	return bStr

class PSDParserBase():
	
	def __init__(self, stream = None):
		self.logger = logging.getLogger("pypsd.base.PSDParserBase")

		self.debugMethodInOut("__init__", {"stream":stream})

		if stream is None or not isinstance(stream, io.BufferedReader):
			raise BaseException("File object should be specified.")
		
		self.stream = stream
		
		'''
		Constants.
		'''
		self.SIGNATURE = "8BPS"
		self.SIGNATIRE_8BIM = "8BIM"
		self.VERSION = 1
		self.CHANNELS_RANGE = [1, 56]
		self.SIZE_RANGE = [1, 30000]
		self.DEPTH_LIST = [1,8,16]
		self.OPACITY_RANGE = [0, 255]
		
		'''
		Start parse Method of the child.
		'''
		self.parse()

	def parse(self):
		raise NotImplementedError()
	
	def skip(self, size):
		self.stream.seek(size, whence=1)
		self.debugMethodInOut("skip", {"size":size})
	
	def skipIntSize(self):
		size = self.readInt()
		self.skip(size)
		self.debugMethodInOut("skipIntSize",result="skipped=%s" % size)
		
	def readCustomInt(self, size):
		value = bytesToInt(self.stream.read(size))
		
		self.debugMethodInOut("readCustomInt", {"size":size}, result=value)
		return value

	def readShortInt(self):
		ch1 = self.readCustomInt(1)
		ch2 = self.readCustomInt(1)
		if ch1 > 0:
			bytes = -(256 - ch1)
		else:
			bytes = ch2
		
		self.debugMethodInOut("readShortInt", result=bytes)
		return bytes
	
	def readTinyInt(self):
		tinyInt = self.readCustomInt(1)
		
		self.debugMethodInOut("readTinyInt", result=tinyInt)
		return tinyInt

	def readInt(self):
		value = self.readCustomInt(4)
		
		self.debugMethodInOut("readInt", result=value)
		return value

	def readBits(self, size):
		barray = bytearray(size)
		self.stream.readinto(barray)
		result = list(barray)
		
		self.debugMethodInOut("readBits", {"size":size}, result)
		return result

	def readString(self, size):
		value = str(self.stream.read(size), "UTF-8")
		self.debugMethodInOut("readString", {"size":size}, value)
		
		return value

	def getSize(self):
		return os.path.getsize(self.stream.name)
	
	def getRectangle(self):
		top = self.readInt()
		left = self.readInt()
		bottom = self.readInt()
		right  = self.readInt()
		width  = right-left
		height = bottom-top
		
		return {"top":top, "left":left, "bottom":bottom, "right":right, 
			    "width":width, "height":height}
	
	def getCodeLabelPair(self, code, map):		
		return {"code":code, "label":map[code]}
	
	def debugMethodInOut(self, label, invars={}, result=None):
		message = "%s method." % label
		
		if invars:
			invars = ["%s=%s" % (name, vars[name]) for name in vars]
			message += "In: %s" % ", ".join(invars)
			
		if result:
			message += "Out: %s" % result
			
		self.logger.debug(message)


#class CodeMapObject(object):
#	def __init__(self, code=None, map={}, *args, **kwargs):
#		self.logger = logging.getLogger("pypsd.base.CodeMapObject")
#		self.logger.debug(
#				"__int__ method. In: code=%s, map=%s, args=%s, kwargs=%s" %
#				(code, map, args, kwargs))
#		super(CodeMapObject, self).__init__(*args, **kwargs)
#		self.map = map
#		self.code = code
#		self.name = None
#		self.updatename()
#
#	def updatename(self):
#		if self.code is not None:
#			if self.code not in self.map:
#				raise BaseException("Code should be from the list.")
#			else:
#				self.name = self.map[self.code]
#
#		self.logger.debug("updatename method. In: code=%s, Out: name=%s" %
#						(self.code, self.name))
#
#	def __str__(self):
#		return "%s (%s)" % (self.name, self.code)


class PSDBaseTest(unittest.TestCase):
	def testBytesToInt(self):
		value1 = bytesToInt(b'\x00\x01\x02\x03')
		self.failUnlessEqual(0x10203, value1)
		value2 = bytesToInt(b'\xff\x14\x2a\x10')
		self.failUnlessEqual(0xff142a10, value2)


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()