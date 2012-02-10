from restkit.forms import (
    BoundaryItem,
    CRLF,
)

"""
Soundcloud API has a bug. This is documented at
http://groups.google.com/group/soundcloudapi/browse_frm/thread/35498de89906c5c1?hl=en

Because of this we need to monkey patch restkit.
"""

restkit_encode_hdr = BoundaryItem.encode_hdr

def sc_encode_hdr(self, boundary):
    """Returns the header of the encoding of this parameter.
    
    Patched for soundcloudapi
    """
    if not self._encoded_hdr or self._encoded_bdr != boundary:
        boundary = self.quote(boundary)
        self._encoded_bdr = boundary
        headers = ["--%s" % boundary]
        if self.fname:
            disposition = 'form-data; name="%s"; filename="%s"' % (self.name,
                    self.fname)
        else:
            disposition = 'form-data; name="%s"' % self.name
        headers.append("Content-Disposition: %s" % disposition)
        if self.filetype:
            filetype = self.filetype
        else:
            pass
            #filetype = "text/plain; charset=utf-8"
        #headers.append("Content-Type: %s" % filetype)
        #headers.append("Content-Length: %i" % self.size)
        headers.append("")
        headers.append("")
        self._encoded_hdr = CRLF.join(headers)
    return self._encoded_hdr

BoundaryItem.encode_hdr = sc_encode_hdr