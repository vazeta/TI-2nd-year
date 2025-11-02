# Author: Marco Simoes
# Adapted from Java's implementation of Rui Pedro Paiva
# Teoria da Informacao, LEI, 2022

import sys
from huffmantree import HuffmanTree
import numpy as np


lenCodes = {257: (0,3), 258: (0, 4), 259: (0, 5), 260: (0, 6), 261: (0, 7), 262: (0,8), 263: (0,9),
            264: (0, 10), 265: (1,11), 266:(1, 13), 267: (1, 15), 268: (1, 17), 269: (2, 19), 270: (2, 23), 271: (2, 27),
            272: (2,31), 273: (3, 35), 274: (3, 43), 275: (3, 51), 276: (3,59), 277: (4,67), 278: (4, 83), 279: (4,99),
            280: (4,115), 281: (5,131), 282: (5,163), 283: (5,195), 284: (5,227), 285: (0, 258)}

distCodes = {0: (0,1), 1: (0,2), 2:(0,3), 3: (0,4), 4:(1,5), 5:(1,7), 6:(2,9), 7:(2,13), 8:(3,17), 9:(3,25),
             10:(4,33), 11:(4,49), 12:(5,65), 13:(5,97), 14:(6,129), 15:(6,193), 16:(7,257), 17:(7,385),
             18:(8,513), 19:(8,769), 20:(9,1025), 21:(9,1537), 22:(10,2049), 23:(10,3073), 24:(11,4097),
             25:(11, 6145), 26:(12,8193), 27:(12,12289), 28:(13,16385), 29:(13,24577)}

class GZIPHeader:
	''' class for reading and storing GZIP header fields '''

	ID1 = ID2 = CM = FLG = XFL = OS = 0
	MTIME = []
	lenMTIME = 4
	mTime = 0

	# bits 0, 1, 2, 3 and 4, respectively (remaining 3 bits: reserved)
	FLG_FTEXT = FLG_FHCRC = FLG_FEXTRA = FLG_FNAME = FLG_FCOMMENT = 0   
	
	# FLG_FTEXT --> ignored (usually 0)
	# if FLG_FEXTRA == 1
	XLEN, extraField = [], []
	lenXLEN = 2
	
	# if FLG_FNAME == 1
	fName = ''  # ends when a byte with value 0 is read
	
	# if FLG_FCOMMENT == 1
	fComment = ''   # ends when a byte with value 0 is read
		
	# if FLG_HCRC == 1
	HCRC = []
		
		
	
	def read(self, f):
		''' reads and processes the Huffman header from file. Returns 0 if no error, -1 otherwise '''

		# ID 1 and 2: fixed values
		self.ID1 = f.read(1)[0]  
		if self.ID1 != 0x1f: return -1 # error in the header
			
		self.ID2 = f.read(1)[0]
		if self.ID2 != 0x8b: return -1 # error in the header
		
		# CM - Compression Method: must be the value 8 for deflate
		self.CM = f.read(1)[0]
		if self.CM != 0x08: return -1 # error in the header
					
		# Flags
		self.FLG = f.read(1)[0]
		
		# MTIME
		self.MTIME = [0]*self.lenMTIME
		self.mTime = 0
		for i in range(self.lenMTIME):
			self.MTIME[i] = f.read(1)[0]
			self.mTime += self.MTIME[i] << (8 * i) 				
						
		# XFL (not processed...)
		self.XFL = f.read(1)[0]
		
		# OS (not processed...)
		self.OS = f.read(1)[0]
		
		# --- Check Flags
		self.FLG_FTEXT = self.FLG & 0x01
		self.FLG_FHCRC = (self.FLG & 0x02) >> 1
		self.FLG_FEXTRA = (self.FLG & 0x04) >> 2
		self.FLG_FNAME = (self.FLG & 0x08) >> 3
		self.FLG_FCOMMENT = (self.FLG & 0x10) >> 4
					
		# FLG_EXTRA
		if self.FLG_FEXTRA == 1:
			# read 2 bytes XLEN + XLEN bytes de extra field
			# 1st byte: LSB, 2nd: MSB
			self.XLEN = [0]*self.lenXLEN
			self.XLEN[0] = f.read(1)[0]
			self.XLEN[1] = f.read(1)[0]
			self.xlen = self.XLEN[1] << 8 + self.XLEN[0]
			
			# read extraField and ignore its values
			self.extraField = f.read(self.xlen)
		
		def read_str_until_0(f):
			s = ''
			while True:
				c = f.read(1)[0]
				if c == 0: 
					return s
				s += chr(c)
		
		# FLG_FNAME
		if self.FLG_FNAME == 1:
			self.fName = read_str_until_0(f)
		
		# FLG_FCOMMENT
		if self.FLG_FCOMMENT == 1:
			self.fComment = read_str_until_0(f)
		
		# FLG_FHCRC (not processed...)
		if self.FLG_FHCRC == 1:
			self.HCRC = f.read(2)
			
		return 0
			



class GZIP:
        ''' class for GZIP decompressing file (if compressed with deflate) '''

        gzh = None
        gzFile = ''
        fileSize = origFileSize = -1
        numBlocks = 0
        f = None
        

        bits_buffer = 0
        available_bits = 0		

        
        def __init__(self, filename):
            self.gzFile = filename
            self.f = open(filename, 'rb')
            self.f.seek(0,2)
            self.fileSize = self.f.tell()
            self.f.seek(0)
            self.decompFile = open(self.gzFile.replace('.gz',''),'wb')
        
        def decompress(self):
            ''' main function for decompressing the gzip file with deflate algorithm '''
                
            numBlocks = 0
    
            # get original file size: size of file before compression
            origFileSize = self.getOrigFileSize()
            print(origFileSize)
            
            # read GZIP header
            error = self.getHeader()
            if error != 0:
                print('Formato invalido!')
                return
            
            # show filename read from GZIP header
            print(self.gzh.fName)
            
            
            # MAIN LOOP - decode block by block
            BFINAL = 0	
            while BFINAL != 1:	
                
                BFINAL = self.readBits(1)
                                
                BTYPE = self.readBits(2)					
                if BTYPE != 2:
                    print('Error: Block %d not coded with Huffman Dynamic coding' % (numBlocks+1))
                    return
                
                HLIT, HDIST, HCLEN = self.BlockReader()#ponto1
                numLLCodes = HLIT + 257
                numDistCodes = HDIST + 1
                numCLCodes = HCLEN + 4
                
                alphaCodeLen =  self.hclenParaCodeComp(numCLCodes)#ponto 2 
                huffCode = self.alphaParaHuffman(alphaCodeLen) #ponto 3
                LLCodes, DISTCodes = self.litDistToHuffman(huffCode, numLLCodes, numDistCodes)#ponto 4,5,6
                self.decodeHuffman(LLCodes, DISTCodes) #ex7,8
    
                                                                                                                                                                    
                #update number of blocks read
                numBlocks += 1
        
                # close file			
            self.f.close()
            self.decompFile.close()
            print("HLIT:",HLIT)
            print("HDIST:",HDIST)
            print("HCLEN:",HCLEN)
            print("--------------------------")
            print("Array os comprimentos dos códigos do “alfabeto de comprimentos de códigos”, com base em HCLEN: ")
            print(alphaCodeLen)
            print("------------------")
            print("Códigos de Huffman: ")
            print(huffCode)
            print("-------------------------------") 
            print(LLCodes)
            print("-------------------------------")
            print(DISTCodes)
            print("------------------")
            print("End: %d block(s) analyzed." % numBlocks)
                
        
        #Ponto 1
        def BlockReader(self):
            return self.readBits(5), self.readBits(5), self.readBits(4)
        
        #Ponto 2
        def hclenParaCodeComp(self, numCLCodes):
            ordem = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
            alphaCodeLen = list(np.zeros(len(ordem),dtype=int))
            for i in range(numCLCodes):
                alphaCodeLen[ordem[i]] = self.readBits(3)
                
            return alphaCodeLen
        
        #ponto 3
        def alphaParaHuffman(self, alphaCodeLen):
            lenCounts = [0 for _ in range(max(alphaCodeLen)+1)]
            for length in alphaCodeLen:
                lenCounts[length] += 1
            code = 0
            lenCounts[0] = 0
            nxtCode = [0 for _ in range(max(alphaCodeLen)+1)]
            for bits in range(1, max(alphaCodeLen)+1):
                code = (code + lenCounts[bits-1]) << 1
                nxtCode[bits] = code
            
            codeTable = [(0,0) for _ in range(len(alphaCodeLen))]
            for i in range(len(alphaCodeLen)):
                length = alphaCodeLen[i]
                if length != 0:
                    codeTable[i] = (length, nxtCode[length])
                    nxtCode[length] += 1
            
            return codeTable
        
        def litDistToHuffman(self, codeTable, numLLCodes, numDistCodes):
            
            codeLengthsTreeRoot = HuffmanTree()
    
            for i in range(len(codeTable)):
                numBits, codeBits = codeTable[i]
                if numBits == 0:
                    continue
                code = ""
                for j in range(numBits):
                    code += str((codeBits>>(numBits-j-1)&1))
                codeLengthsTreeRoot.addNode(code, i)
    
            #Search Huffman tree for symbols
            LLCodeLen = [0] * 288
            DistCodeLen = [0] * 32
    
            tree = codeLengthsTreeRoot
            codesRead = 0
            lastIndex = -1
            while codesRead < numLLCodes + numDistCodes:
                tree.nextNode(str(self.readBits(1)))
                if tree.curNode.index == -1:
                    continue
                index = tree.curNode.index
                tree.resetCurNode()
    
                assert(0 <= index < 19) 
    
                if index <= 15:
                    if codesRead >= numLLCodes:
                        DistCodeLen[codesRead-numLLCodes] = index
                    else:
                        LLCodeLen[codesRead] = index
                    codesRead += 1
                    lastIndex = index
    
                elif index == 16:
                    repeatCount = 3 + self.readBits(2)
                    for i in range(repeatCount):
                        if codesRead >= numLLCodes:
                            DistCodeLen[codesRead-numLLCodes] = lastIndex
                        else:
                            LLCodeLen[codesRead] = lastIndex
                        codesRead += 1
    
                elif index == 17:
                    repeatCount = 3 + self.readBits(3)
                    for i in range(repeatCount):
                        if codesRead >= numLLCodes:
                            DistCodeLen[codesRead-numLLCodes] = 0
                        else:
                            LLCodeLen[codesRead] = 0
                        codesRead += 1
                    lastIndex = 0
    
                else:
                    repeatCount = 11 + self.readBits(7)
                    for i in range(repeatCount):
                        if codesRead >= numLLCodes:
                            DistCodeLen[codesRead - numLLCodes] = 0
                        else:
                            LLCodeLen[codesRead] = 0
                        codesRead += 1
                    lastIndex = 0
                    
            #ponto 6
            #Usando a funcao do ponto 3
            LLCodes = self.alphaParaHuffman(LLCodeLen)
            DISTCodes = self.alphaParaHuffman(DistCodeLen)
    
            return LLCodes, DISTCodes
        
        def decodeHuffman(self, LLCodes, DISTCodes):
            arvoreLL = HuffmanTree()
            for i in range(len(LLCodes)):
                numBits, codeBits = LLCodes[i]
                if numBits == 0:
                    continue
                code = ""
                for j in range(numBits):
                    code += str((codeBits >> (numBits - j - 1) & 1))
                arvoreLL.addNode(code, i,True)
        
            arvoreDIST = HuffmanTree()
            for i in range(len(DISTCodes)):
                numBits, codeBits = DISTCodes[i]
                if numBits == 0:
                    continue
                code = ""
                for j in range(numBits):
                    code += str((codeBits >> (numBits - j - 1) & 1))
                arvoreDIST.addNode(code, i,True)
        
            hist = []
            histSize = 32768
        
            while True:
                arvoreLL.nextNode(str(self.readBits(1)))
                if arvoreLL.curNode.index == -1:
                    continue
                index = arvoreLL.curNode.index
                arvoreLL.resetCurNode()
        
                if index == 256:
                    break
                if index > 256:
                    numExtraBits, tam = lenCodes[index]
                    lenOffset = self.readBits(numExtraBits) if numExtraBits > 0 else 0
                    length = lenOffset + tam
        
                    while arvoreDIST.curNode.index == -1:
                        arvoreDIST.nextNode(str(self.readBits(1)))
                    distIndex = arvoreDIST.curNode.index
                    arvoreDIST.resetCurNode()
        
                    numExtraBits, tam = distCodes[distIndex]
                    distOffset = self.readBits(numExtraBits) if numExtraBits > 0 else 0
                    distance = distOffset + tam
        
                    for i in range(length):
                        if len(hist) - distance >= 0:
                            tmpIndex = hist[len(hist) - distance]
                            hist.append(tmpIndex)
                            while len(hist) > histSize:
                                del hist[0]
        
                else:
                    hist.append(index)
                    while len(hist) > histSize:
                        del hist[0]
        
            self.decompFile.write(bytearray(hist))
            
                    
        
            
        def getOrigFileSize(self):
            ''' reads file size of original file (before compression) - ISIZE '''
            
            # saves current position of file pointer
            fp = self.f.tell()
            
            # jumps to end-4 position
            self.f.seek(self.fileSize-4)
            
            # reads the last 4 bytes (LITTLE ENDIAN)
            sz = 0
            for i in range(4): 
                sz += self.f.read(1)[0] << (8*i)
            
            # restores file pointer to its original position
            self.f.seek(fp)
            
            return sz		
            
            
        def getHeader(self):  
            ''' reads GZIP header'''
    
            self.gzh = GZIPHeader()
            header_error = self.gzh.read(self.f)
            return header_error
        
        def readBits(self, n, keep=False):
            ''' reads n bits from bits_buffer. if keep = True, leaves bits in the buffer for future accesses '''
    
            while n > self.available_bits:
                self.bits_buffer = self.f.read(1)[0] << self.available_bits | self.bits_buffer
                self.available_bits += 8
            
            mask = (2**n)-1
            value = self.bits_buffer & mask
    
            if not keep:
                self.bits_buffer >>= n
                self.available_bits -= n
    
            return value


if __name__ == '__main__':
    # gets filename from command line if provided
    fileName = "FAQ.txt.gz"
    if len(sys.argv) > 1:
        fileName = sys.argv[1]			

    # decompress file
    gz = GZIP(fileName)
    gz.decompress()