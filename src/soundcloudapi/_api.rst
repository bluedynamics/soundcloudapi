
flat dict
=========

We need to flatten the dict according to soundclouds very special and partly
insane needs. Limitations are strong with dicts in lists, so i hope its never
needed for POST or PUT. Limitations are documented with this test too::

    >>> from soundcloudapi._api import soundcloud_flat_dict
    >>> data = {'foo': 'bar', 
    ...         'baz': {'bazfoo': 'value', 'bazbar': 'value2'},
    ...         'buz': [1, 2, 3],
    ...         'biz': [{'x': 'y', 'a': 'b'}, {'x': 'z', 'a': 'c'}]}
    >>> data = soundcloud_flat_dict(data, 'test')
    >>> print ',\n'.join(['%s: %s' % (k, v) for k, v in sorted(data.items())])
    test[baz][bazbar]: value2,
    test[baz][bazfoo]: value,
    test[biz][][a]: b,
    test[biz][][a]: c,
    test[biz][][x]: y,
    test[biz][][x]: z,
    test[buz][]: 1,
    test[buz][]: 2,
    test[buz][]: 3,
    test[foo]: bar
    
preparation of form
===================

::

    >>> from soundcloudapi._api import prepare_payload
    >>> payload, headers = prepare_payload(data, 'test')
    
    >> payload.boundaries
    
    XXX TODO

        
Test API
========

Prepare
-------

Fetch values from environment::

    >>> import os
    >>> CLIENT_ID = os.environ.get('CLIENT_ID')
    >>> TOKEN = os.environ.get('TOKEN')     

    >>> from soundcloudapi import Soundcloud, AuthInfo
    >>> authinfo = AuthInfo(CLIENT_ID, token=TOKEN)
    >>> sc = Soundcloud(authinfo)

Users Public API
----------------

::

    >>> user = sc.users(3207)
    >>> user()['permalink']
    u'jwagener'
    
    >>> 'video_url' in user.tracks()[0]
    True
    
    >>> 'title' in user.playlists()[0]
    True    
    
    >>> 'city' in user.followers()[0]
    True

    >>> 'permalink' in user.followings()[0]
    True
    
    >>> 'body' in user.comments()[0]
    True

    >>> 'attachments_uri' in user.favorites()[0]
    True

    >>> 'permalink' in user.groups()[0]
    True

    >>> lid = 22647936
    >>> luh = sc.tracks(22647936)
    >>> me = sc.me()

    >>> interact(locals())
    
    
    
    