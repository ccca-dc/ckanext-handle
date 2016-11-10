import os
import logging
import urlparse
import ckan.plugins as p
from pylons import config

from b2handle.handleclient import  EUDATHandleClient
from b2handle.clientcredentials import PIDClientCredentials

log = logging.getLogger(__name__)

class HandleService:
    def __init__(self):
        # Load config parameters for ckanext-handle
        self.handle_server_url = config.get("ckanext.handle.handle_server_url")
        self.private_key = config.get("ckanext.handle.private_key")
        self.certificate_only = config.get("ckanext.handle.certificate_only")
        self.prefix = config.get("ckanext.handle.prefix")
        self.proxy = config.get("ckanext.handle.proxy")
        self.resourcefield = config.get("ckanext.handle.resourcefield")
        self.packagefield = config.get("ckanext.handle.packagefield")

        # Create credentials and client for handle interaction
        #self.cred = PIDClientCredentials(
        #    handle_server_url=self.handle_server_url,
        #    private_key=self.private_key,
        #    certificate_only=self.certificate_only)
        #self.client = EUDATHandleClient.instantiate_with_credentials(cred)


    def create_hdl_url(self, hdl_id):
        """
        Create a unique identifier, using the prefix and the id:
        eg. 20.500.11756/15aa58d5-2405-4e0e-ad1b-ad9776e9733f
        Do not register
        @param hdl_id: A handle suffix
        @return handle: A handle URL
        """
        # Create valid handle pid
        hdl_url = urlparse.urlparse(self.proxy)
        url_path = '/'.join(s.strip('/') for s in [self.prefix,hdl_id])
        hdl_url = hdl_url._replace(path = url_path)
        hdl_url = urlparse.urlunparse(hdl_url)

        return hdl_url

    def register_hdl_url(self, hdl_url, location):
        """
        Register a handle url:
        eg. https://hdl.handle.net/20.500.11756/15aa58d5-2405-4e0e-ad1b-ad9776e9733f
        @param hdl_url: A handle URL
        @return:
        """
        handle = self.client.register_handle(_hdl_url_to_hdl_id(hdl_url))
        log.debug(handle)
        return handle

    def _hdl_url_to_hdl_id(self, hdl_url):
        hdl_url_parsed = urlparse.urlparse(hdl_url)
        hdl_id = hdl_url_parsed.path.stip('/')
        log.debug(hdl_id)

        return hdl_id
