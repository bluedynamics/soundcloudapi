#! /usr/bin/env python
# tested using python 2.7 with ssl
import httplib
import pprint

# CONFIGURATION START ########## 

# PLEASE INSERT YOUR TOKEN HERE (example token is invalid)
APITOKEN = '1-11207-73814e2-f825d91d5b94b72a'

# CONFIGURATION END ##########

headers = dict() 
headers['Content-Type'] = "multipart/form-data; boundary=---xxThIs_Is_tHe_bouNdaRY_f0r_ThE_s0uNdC10uDxx--"

def post_data(filename):
    postfile = open(filename, 'rb')
    postdata = postfile.read()
    postfile.close()
    postdata = postdata.replace('APITOKEN', APITOKEN)    
    con = httplib.HTTPSConnection('api.soundcloud.com')
    headers['Content-Length'] = len(postdata)
    con.request('POST', '/tracks', postdata, headers)
    response = con.getresponse()
    con.close()
    return response.status, response.reason

print "Response of working post data: ",
print post_data('post_ok.data')

print "Response of not working post data: ", 
print post_data('post_bug.data')