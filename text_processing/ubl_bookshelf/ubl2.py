import requests
import pyPdf
import glob
import json
import time
import os

from collections import Counter
from alchemyapi import AlchemyAPI

alchemyapi = AlchemyAPI()
file_list  = glob.glob("pdfs/*.pdf")
entities   = {}
concepts   = {}
categories = {}


for pdf_file in file_list:

    # read in the PDF
    print "[*] Parsing %s" % pdf_file
    
    pdf_obj = pyPdf.PdfFileReader(open(pdf_file,"rb"))

    full_text = ""
    
    # extract all of the text from each page
    for page in pdf_obj.pages:
        
        full_text += page.extractText()

    # let the Alchemy API extract entities
    print "[*] Sending %d bytes to the Alchemy API" % len(full_text)
    
    
    response = alchemyapi.entities('text', full_text, {'sentiment': 0})
    
    
    # get the list of entities
    if response['status'] == 'OK':
        
        # loop through the list of entities
        for entity in response['entities']:
            
            # add each entity to our master list
            if entities.has_key(entity['text']):
                entities[entity['text']] += int(entity['count'])
            else:
                entities[entity['text']] = int(entity['count'])
                
        print "[*] Retrieved %d entities from %s" % (len(entities),pdf_file)    
        
    else:
        print "[!] Error receiving Alchemy response: %s" % response['statusInfo']
        
    
    # get the category
    response = alchemyapi.category('text',full_text)
    
    if response['status'] == 'OK':
        
        if categories.has_key(response['category']):
            categories[response['category']] += 1
        else:
            categories[response['category']]  = 1
    
        print "[*] Categorized %s as %s" % (pdf_file,response['category'])
        
        
    # grab the concepts
    response = alchemyapi.concepts('text',full_text)
    
    if response['status'] == 'OK':
    
        # loop through the list of entities
        for concept in response['concepts']:
    
            # add each entity to our master list
            if concepts.has_key(concept['text']):
                concepts[concept['text']] += 1
            else:
                concepts[concept['text']]  = 1
    
        print "[*] Retrieved %d concepts from %s" % (len(response['concepts']),pdf_file)    
    
    else:
        print "[!] Error receiving Alchemy response: %s" % response['statusInfo']    

    
    time.sleep(1)

    
# now accumulate our most common terms and print them out
entity_counter = Counter(entities)

top_entities   = entity_counter.most_common()

print "Top 10 Entities"
print "-" * 25

# let's take the top 10 entities UBL mentions
for top_entity in top_entities[0:10]:
    
    # most_common returns a tuple (entity,count)
    output = "%s => %d" % (top_entity[0],top_entity[1])
    

# grab the top 10 concepts
concept_counter = Counter(concepts)

top_concepts    = concept_counter.most_common()

print
print "Top 10 Concepts"
print "-" * 25

for top_concept in top_concepts[0:10]:
    
    print "%s => %d" % (top_concept[0],top_concept[1])
    
# grab the top 10 categories
category_counter = Counter(categories)

top_categories     = category_counter.most_common()

print
print "Top 10 Categories"
print "-" * 25

for  top_category in top_categories[0:10]:
    
    print "%s => %d" % (top_category[0],top_category[1])
    