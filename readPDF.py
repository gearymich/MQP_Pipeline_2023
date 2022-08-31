import PyPDF2
import os

def textPreprocess(text):
	'''
	handles multiple problems with traslating from pdf to text
	involves many hard coding solutions
	'''

	# first concatenate broken sentences
	# type 1: ending with space
	newText1 = []
	index = 0
	while index < len(text):
		tempList = [] # stores sentences to concatenate
		target = text[index]
		tempList.append(target.strip()) # remove spaces
		while target.endswith(' ') and index < len(text) - 1:
			index += 1
			target = text[index]
			tempList.append(target.strip())
		newText1.append(' '.join(tempList))
		index += 1

	# type 2: starting with -
	newText1 = newText1[::-1] # reverse the order
	newText2 = []
	index = 0
	while index < len(newText1):
		tempList = [] # stores sentences to concatenate
		target = newText1[index]
		tempList.append(target.lstrip('-'))
		while target.startswith('-') and index < len(newText1) - 1:
			# print(target)
			index += 1
			target = newText1[index]
			tempList.append(target.lstrip('-'))
		newText2.append(''.join(tempList[::-1]))
		index += 1
	newText2 = newText2[::-1]

	# type 1: ending with -
	newText3 = []
	index = 0
	while index < len(newText2):
		tempList = [] # stores sentences to concatenate
		target = newText2[index]
		tempList.append(target.rstrip('-')) # remove spaces
		while target.endswith('-') and index < len(newText2) - 1:
			index += 1
			target = newText2[index]
			tempList.append(target.rstrip('-'))
		newText3.append(''.join(tempList))
		index += 1

	# now we think of spellcheckers
	# i found textblob not working properly
	# currently only hard coding for traf˜ckers and Cote d™Ivoire
	newText3 = [item.replace('˜', 'fi') for item in newText3]
	newText3 = [item.replace('Œ', '-') for item in newText3]
	newText3 = [item.replace('\"', '') for item in newText3]
	newText3 = [item.replace('\'', '') for item in newText3]
	newText3 = [item.replace('™', '\'') for item in newText3] #moved this below to keep the apostrophe in Cote d'Ivoire which is nescessary for GPE entity recognition
	return newText3

# return list of pages text ["page 1 text", "page 2 text"]
def readPDF(fileName, fileExt):
    with open('{}.{}'.format(fileName, fileExt), 'rb') as f:
        pdfReader = PyPDF2.PdfFileReader(f)
        pages = []
        for pageNum in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(pageNum)
            text = pageObj.extractText()
            pageToken = '| {}'.format(pageNum+1)
            text = text.replace(pageToken, pageToken+'\n')
            text = text.replace('\n-\n', '')                                # IDEA May want to preserve newlines/tabs for identifying new paragraphs
            text = [item for item in text.split('\n') if item != '']
            text = textPreprocess(text)
            pages.append(text)
    text = [" ".join(page) for page in pages]
    return text
