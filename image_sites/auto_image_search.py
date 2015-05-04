import pynoramio

import os

# set a name for our search
search_name      = "BellingcatRaqqah"

# set our bounding box coordinates here
southwest_corner = "<PASTEYOURCOORDINATESHERE>"
northeast_corner = "<PASTEYOURCOORDINATESHERE>"

# we use the coordinates 
lat_min,long_min = southwest_corner.split(",")
lat_max,long_max = northeast_corner.split(",")


#
# All of our magical search functions here
#
def panaramio_search(fd):
    
    image_searcher = pynoramio.Pynoramio()

    # perform the search
    panaramio_results = image_searcher.get_from_area(float(lat_min), float(long_min), float(lat_max), float(long_max),picture_size="original",map_filter=False)

    # panaramio_results is a dictionary with: count, has_more, map_location, photos
    if panaramio_results['count'] > 0:
        
        print "[*] Retrieved: %d results" % panaramio_results['count']
        
        # now retrieve all photos from this search
        for photo in panaramio_results['photos']:
          
            # write the image out to our HTML page with a link to Google Maps
            fd.write("<a target='_blank' href='http://maps.google.com/?q=%f,%f'><img src='%s' border='0'></a><br/>\r\n" % 
                     (photo['latitude'],photo['longitude'],photo['photo_file_url']))

        return

# create a directory to hold our results
if not os.path.exists("%s" % search_name):
    os.mkdir("%s" % search_name)

# open up our HTML page for writing
fd = open("%s/%s.html" % (search_name,search_name), "wb")

# write out the top of the HTML document
fd.write("<html><head></head><body>")

# now do a paramio search
panaramio_search(fd)

# close the HTML file
fd.write("</body></html>")
fd.close()

print "[*] Finished!"