from lxml import html

import json
import requests
import re
import argparse
import networkx as nx
import urllib

ap = argparse.ArgumentParser()
ap.add_argument("-d","--domain",    required=False,help="The domain to target ie. cnn.com")
ap.add_argument("-f","--file",      required=False,help="File that contains a list of domains to process.")
ap.add_argument("-mp", "--meanpath",required=False,help="Search Meanpath for potential new sites", action='store_true')

args = vars(ap.parse_args())


mashape_api_key = ""

networks = {}

networks['Google Analytics'] = {
    "xpath" : "//script/text()", 
    "regex" : "UA-(.+?)-",   
    "search_prefix" : "UA-"  }

networks['Google AdSense']   = {
    "xpath" : "//script/text()", 
    "regex" : "pub-(.+?)\"", 
    "search_prefix" : "pub-" }

networks['Amazon Affiliate'] = { 
    "xpath" : "//a[contains(@href,\"amazon\")]/@href", 
    "regex" : "tag=(.+?)-20", 
    "search_prefix" : "tag="}

networks['AddThis']          = {
    "xpath" : "//script[contains(@src,\"addthis\")]/@src", 
    "regex" : "#pubid=(.+?)$",
    "search_prefix" : "#pubid="}



network_hits = {}


if args['domain'] is not None:
    site_list = [args['domain']]
elif args['file'] is not None:
    site_list  = open(args['file'], 'r').read().splitlines()
else:
    print "[*] Need to specify -d or -f in order for this to work!"


#
# Search Meanpath for hits to add to our list of targets
#
def search_meanpath(meanpath_query):
     
    # we need to quote for exact matching 
    meanpath_query = "\"%s\"" % meanpath_query
    
    api_url = "https://meanpathfree.p.mashape.com/?q=%s" % urllib.quote(meanpath_query)
    
    headers = {}
    headers['X-Mashape-Key'] = mashape_api_key
    headers['Accept']        = "application/json"
    
    response = requests.get(api_url,headers=headers)
    
    if response.status_code == 200:
        
        results = json.loads(response.content)
    
        return results
    
    return None

#
# Extract all networks from HTML
#
def extract_tracking_code(html_tree,tracking_code=None):    
    
    hit_list     = []
    
    for network in networks:
    
        # extract the HTML elements we want
        html_elements = html_tree.xpath(networks[network]['xpath'])
        
        
        if html_elements:
            
            for element in html_elements:
                
                tracking_codes = re.findall(networks[network]['regex'],element)
                
                if tracking_codes:
                    
                    if tracking_code is not None:
                        
                        if tracking_code in tracking_codes:
                            hit_list.append([network,tracking_codes])
                    else:
                        hit_list.append([network,tracking_codes])
                        
    return hit_list

#
# Analyze a target site
#
def analyze_target(site,tracking_code=None):
    
    if "http://" not in site: 
        
        site = "http://" + site        
    
        if site.endswith ("/") != True:
            site = site + "/"
    
    print "[*] Trying %s..." % site,

    # retrieve the website content
    try:
        page = requests.get(site) # Get the HTML
        print "Success! Parsing HTML"
    except:
        print "Failed: Site Unreachable."           
        return None

    if page.status_code == 200:

        # attempt to parse the HTML tree
        try:
            html_tree = html.fromstring(page.text)
        except:
            print "[!] Failed to parse HTML."    
            return None
    else:
        return None
    
    hit_list = extract_tracking_code(html_tree,tracking_code)    


    return hit_list


number_of_sites = len(site_list)
new_sites       = []
site_graph      = nx.Graph()
full_hit_list   = []

for site in site_list:
    
    # if this is a site picked up by Meanpath we will validate
    # against original tracking code
    if type(site) is list:
        hit_list = analyze_target(site[0],site[1])
        site     = site[0]
        
        if hit_list:
            new_sites.append(site)
            
    else:
        hit_list = analyze_target(site)
        
    if hit_list:
        
        # add the site to the graph
        site_graph.add_node(site,EntityType="Website",URL=site)
        
        
        for hit in hit_list:
            
            for tracking_code in set(hit[1]):

                if tracking_code not in full_hit_list:
                    full_hit_list.append(tracking_code)
                
                # connect the tracking code to the site
                site_graph.add_node(tracking_code,EntityType=hit[0])
                site_graph.add_edge(site,tracking_code)
                
                # search for additional hits in Meanpath
                if args['meanpath'] == True and mashape_api_key is not "":
                    
                    # Build Meanpath search string              
                    meanpath_query = networks[hit[0]]['search_prefix'] + tracking_code
                    
                    results = search_meanpath(meanpath_query)

                else:
                    results = None
    
                if results is not None:
                    
                    for result in results['hits']['hits']:
                        
                        # do we already have this domain
                        if result['_id'] not in site_list and [result['_id'],tracking_code] not in site_list:
                            
                            # add it to the list of sites to process
                            print "[*] Discovered potential new target: %s" % result['_id']
                            site_list.append([result['_id'],tracking_code])
                            
                            
        
print "[*] Discovered %d unique tracking codes." % len(full_hit_list)
print "[*] Discovered %d new websites:" % len(new_sites)

for site in new_sites:
    print "[+] %s" % site
    

nx.write_gexf(site_graph,"Site_Network.gexf")

print "[*] Complete. Graph output to Site_Network.gexf."