Prepare
=======

::
    >>> import os
    >>> CLIENT_ID = os.environ.get('CLIENT_ID')
    >>> CLIENT_SECRET = os.environ.get('CLIENT_SECRET')    
    >>> REDIRECT_URI = os.environ.get('REDIRECT_URI')    
    >>> CODE = os.environ.get('CODE') 
    >>> TOKEN = os.environ.get('TOKEN') 
    >>> interact(locals())

AuthInfo
========
:: 

    >>> from soundcloudapi.auth import AuthInfo
    >>> authinfo = AuthInfo('TESTID', 'TESTSECRET', 'HTTP://REDIRECT.URL')
    >>> authinfo.redirect_url    
    'https://soundcloud.com/connect?client_id=TESTID&client_secret=TESTSECRET&redirect_uri=HTTP://REDIRECT.URL&response_type=code&scope=non-expiring'

    >>> authinfo._step2_body('TESTCODE')
    'client_id=TESTID&client_secret=TESTSECRET&code=TESTCODE&grant_type=authorization_code&redirect_uri=HTTP://REDIRECT.URL'
    
    >>> authinfo.authenticated
    False     
    
    >>> authinfo.token = 'TESTTOKEN'
    >>> authinfo.authenticated 
    True    

With Real Values
================

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
Run buildout. You can proceed with the other tests