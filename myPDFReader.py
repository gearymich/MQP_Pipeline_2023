import PyPDF2
#import fitz
import io
from PIL import Image
import json
import pandas as pd
# from textblob import TextBlob

def HandleText(fileName, fileExt):
	'''
	extract text info and save them
	'''
	f = open('{}.{}'.format(fileName, fileExt), 'rb')
	pdfReader = PyPDF2.PdfFileReader(f)

	textList = []
	pageList = []
	for pageNum in range(pdfReader.numPages):
		pageObj = pdfReader.getPage(pageNum)
		text = pageObj.extractText()
		pageToken = '| {}'.format(pageNum+1)
		text = text.replace(pageToken, pageToken+'\n')
		text = text.replace('\n-\n', '')
		text = [item for item in text.split('\n') if item != '']
		text = textPreprocess(text)
		textList += text
		pageList += [pageNum+1] * len(text)
	f.close()

	df = pd.DataFrame({'text':textList,'page':pageList})
	df.to_csv('{}.csv'.format(fileName), index=False)
	# with open('{}.json'.format(fileName), 'w') as f:
	# 	json.dump(textList, f)
	return

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

def HandleImage(fileName, fileExt):
	'''
	extract image info and save them
	'''
	pdf_file = fitz.open('{}.{}'.format(fileName, fileExt))

	for page_index in range(len(pdf_file)):
	    page = pdf_file[page_index]
	    image_list = page.getImageList()

	    for image_index, img in enumerate(page.getImageList(), start=1):
	    	# extract image info
	        xref = img[0]
	        base_image = pdf_file.extractImage(xref)
	        image_bytes = base_image["image"]
	        image_ext = base_image["ext"]

	        # now save them in original formats
	        image = Image.open(io.BytesIO(image_bytes))
	        # change your style of naming if you wish
	        image.save('{}_page{}_img{}.{}'.format(fileName, page_index, image_index, image_ext))
	        image.close()
	pdf_file.close()
	return

def main(file):
	fileName, fileExt = file.split('.') # do not use extra dots plz
	HandleText(fileName, fileExt)
	#HandleImage(fileName, fileExt)
	return

if __name__ == '__main__':
	main("eagle-briefing-july-public.pdf")
