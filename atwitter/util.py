import mimetools
import mimetypes
import hashlib

def ensure_utf8(x):
    return x.encode('utf-8') if isinstance(x, unicode) else x

def content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

_boundary_hasher = hashlib.sha1()

def encode_multipart(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    h = _boundary_hasher.copy()
    h.update(mimetools.choose_boundary())
    boundary = h.hexdigest()

    crlf = '\r\n'

    l = []
    for k, v in fields:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"' % k)
        l.append('')
        l.append(v)
    for (k, f, v) in files:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, f))
        l.append('Content-Type: %s' % content_type(f))
        l.append('')
        l.append(v)
    l.append('--' + boundary + '--')
    l.append('')
    body = crlf.join(l)

    return boundary, body

