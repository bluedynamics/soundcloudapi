flat dict
=========

::

    >>> from soundcloudapi._api import soundcloud_flat_dict
    >>> data = {'foo': 'bar', 'baz': {'bazfoo': 'value', 'bazbar': 'value2'}}
    >>> data = soundcloud_flat_dict(data)
    >>> print ', '.join(['%s: %s' % (_, data[_]) for _ in sorted(data)])
    baz[bazbar]: value2, baz[bazfoo]: value, foo: bar

Prepare
=======

Fetch values from environment::

    >>> import os
    >>> CLIENT_ID = os.environ.get('CLIENT_ID')
    >>> TOKEN = os.environ.get('TOKEN')     

    >>> from soundcloudapi import Soundcloud, AuthInfo
    >>> authinfo = AuthInfo(CLIENT_ID, token=TOKEN)
    >>> sc = Soundcloud(authinfo)
        
Test API
========

Users
-----

::

    >>> user = sc.users(3207)
    >>> user()['permalink']
    u'jwagener'
    
    >>> 'video_url' in user.tracks()[0]
    True
    
    