
import base64
import logging
logger = logging.getLogger(__name__)

import requests

from ..utils import s2a
from .xml import RemoteXMLDatabase
from . import SyncError

class RemoteRESTDatabase(RemoteXMLDatabase):

    def requestStatus(self, allowHTTP=False):
        logger.debug("Skipping status request")
        return True

    def sync(self, dongle, trackerId, megadump):

        url = "https://android-cdn-client.fitbit.com/1/devices/client/tracker/data/sync.json"

        headers = {
            "Content-Type": "text/plain",
            "Accept-Language": "en-us",
            "Accept-Encoding": "gzip, deflate",
            "Device-Data-Encoding": "base64",
            "X-App-Version": "2.0.1.6809",
            "Fitbit-Code-Version": "0.4.42",
            "Fitbit-Transport-Info": dongle.info(),
        }

        user = "228TQ5"
        authpass = "6e4b857924734e159418ccc0009ef274"
        auth = base64.b64encode(("%s:%s" % (user, authpass)).encode('utf-8'))
        headers['Authorization'] = "Basic "  + auth.decode()

        r = requests.post(url, data=megadump.toBase64(), headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as he:
            status_code = 500
            if getattr(he, 'response', None) is not None:
                status_code = he.response.status_code
            msg = he.args[0]
            raise SyncError("HTTPError: %s (%d)" % (msg, status_code))

        return s2a(base64.b64decode(r.text))
