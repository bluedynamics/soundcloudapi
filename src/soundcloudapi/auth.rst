Prepare
=======

Fetch values from environment::

    >>> import os
    >>> CLIENT_ID = os.environ.get('CLIENT_ID')
    >>> CLIENT_SECRET = os.environ.get('CLIENT_SECRET')    
    >>> REDIRECT_URI = os.environ.get('REDIRECT_URI')    
    >>> CODE = os.environ.get('CODE') 
    >>> TOKEN = os.environ.get('TOKEN') 

AuthInfo
========

Basic tests with AuthInfo:: 

    >>> from soundcloudapi.auth import AuthInfo
    >>> authinfo = AuthInfo('TESTID', 'TESTSECRET', 'HTTP://REDIRECT.URL')
    >>> authinfo.redirect_url   
    'https://soundcloud.com/connect?client_id%3DTESTID%26client_secret%3DTESTSECRET%26redirect_uri%3DHTTP%3A//REDIRECT.URL%26response_type%3Dcode%26scope%3Dnon-expiring'

    >>> authinfo._step2_body('TESTCODE')
    'client_id=TESTID&client_secret=TESTSECRET&code=TESTCODE&grant_type=authorization_code&redirect_uri=HTTP://REDIRECT.URL'
    
    >>> authinfo.authenticated
    False     
    
    >>> authinfo.token = 'TESTTOKEN'
    >>> authinfo.authenticated 
    True    

FETCH YOUR TOKEN
================

If you already now your token, put it in ``testenv.cfg``. Otherwise follow
procedure below. Yes, I know, this is a PITA.

First you'll need to follow the url output shown as error in your browser.
redirect url should prompt the request, so you'll get the code for step 2, put
CODE in ``testenv.cfg`` (its a one-time code ) and run buildout::    
   
    >>> authinfo = AuthInfo(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    >>> if not CODE and not TOKEN:
    ...     authinfo.redirect_url    
    
    
Run the test again. You'll get the token from the code below::

    >>> if CODE:
    ...     authinfo.token_from_code(CODE)
    

Once you have the token, remove CODE from  ``testenv.cfg`` and add TOKEN there.
Run buildout. You can proceed with the other tests::

    >>> if not TOKEN:
    ...     raise Exception('PROVIDE YOUR TOKEN!')

Test the Filter
===============

Basics::

    >>> authinfo = AuthInfo(CLIENT_ID, CLIENT_SECRET, 
    ...                     redirect_uri=REDIRECT_URI, token=TOKEN)
    
    >>> from soundcloudapi.auth import PublicAuth
    >>> from soundcloudapi.auth import PrivateAuth
    >>> public_filter = PublicAuth(authinfo)
    >>> private_filter = PrivateAuth(authinfo)    

Public Resource::

    >>> import json
    >>> from restkit import Resource 
    >>> resource = Resource('http://api.soundcloud.com/tracks/',
    ...                     filters=[public_filter])  
    >>> resp = resource.get(path='13158665.json')
    >>> result = json.loads(resp.body_string())
    >>> result['id']
    13158665
    
Private Resource::
    
    >>> resource = Resource('https://api.soundcloud.com/me.json',
    ...                     filters=[private_filter])
    >>> resp = resource.get()
    >>> result = json.loads(resp.body_string())
    >>> 'full_name' in result
    True

    