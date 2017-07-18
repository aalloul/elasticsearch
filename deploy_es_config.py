#!/usr/bin/env python

from elasticsearch import Elasticsearch, RequestsHttpConnection, client
from json import load
from requests_aws4auth import AWS4Auth
import logging
import argparse

##########
# Cluster settings

ip = "https://search-shippy-es-f5eynamiumiunz5mrdxxmodksu.eu-west-1.es.amazonaws.com"
theport = 80
ACCESS_KEY = "AKIAIAOZRRLDX37HKW4Q"
SECRET_KEY = "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"
REGION = "eu-west-1"
host = 'search-shippy-es-f5eynamiumiunz5mrdxxmodksu.eu-west-1.es.amazonaws.com'
awsauth = AWS4Auth(ACCESS_KEY, SECRET_KEY, REGION, 'es')


#########

class ElasticsearchConfigSink:
    """
    This class is intended as a wrapper to ES.
        It initializes all required variables to allow for a direct
        connection to ES.
        It allows to deploy a new version of a given template
    """

    def __init__(self, template_file_path):
        # Logging
        self.loglevel = logging.INFO
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(self.loglevel)

        self.logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.logger.info("ElasticsearchConfigSink - v0.1")

        # Template information
        self.template_content = self.__get_template_content(template_file_path)
        self.template_name = self.__set_template_name(template_file_path)

        self.logger.debug("  Template file {} found".format(template_file_path))
        self.logger.debug("  Assuming template name is {}".format(self.template_name))

        # Connection information
        self.theport = 80
        self.ACCESS_KEY = "AKIAIAOZRRLDX37HKW4Q"
        self.SECRET_KEY = "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"
        self.REGION = "eu-west-1"
        self.host = 'search-shippy-es-f5eynamiumiunz5mrdxxmodksu.eu-west-1.es.amazonaws.com'
        self.awsauth = AWS4Auth(self.ACCESS_KEY, self.SECRET_KEY, self.REGION, 'es')
        self.es, self.index_client = self.__set_es()

    def __set_template_name(self, filepath):
        """
        This method assumes that the filepath is simply the filename with
        the extension.
        The template name is then extracted from the filename by dropping the extension
        :param filepath: String representing the file name
        :return: The template name.
        """
        return filepath.split(".")[0]

    def __check_es_status(self, es):
        if es.info():
            self.logger.debug("  ES is reachable")
            return True
        else:
            return False

    def __set_es(self):
        es = Elasticsearch(
            hosts=[{'host': self.host, 'port': self.theport}],
            http_auth=self.awsauth,
            connection_class=RequestsHttpConnection
        )
        if self.__check_es_status(es):
            return es, client.IndicesClient(es)
        else:
            raise Exception("Elasticsearch is not reachable")

    def __check_and_clean_template(self):
        if self.index_client.exists_template(self.template_name):
            self.logger.debug("  Template found in ES - Deleting it")
            self.index_client.delete_template(self.template_name)

    def __get_template_content(self, file_path):
        with open(file_path) as f:
            return load(f)

    def __put_template(self):
        return self.index_client.put_template(self.template_name, self.template_content)

    def update_template(self):
        self.logger.debug("Template update")
        self.__check_and_clean_template()
        if self.__put_template()['acknowledged']:
            self.logger.info("  Template deployment finished")
            self.logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            return True


# Allow for filename to be passed as an argument. In which case,
# we will only push that file to ES. Otherwise, both the logging
# and offers templates will be updated.
parser = argparse.ArgumentParser(description='ES configuration deployment argument parser')
parser.add_argument('filename', nargs="?", help="This is the filename where the template can be found.")
args = parser.parse_args()

if args.filename:
    es_sink = ElasticsearchConfigSink(args.filename)
else:
    es_sink_logging = ElasticsearchConfigSink("template_logging_v0.1.json")
    es_sink_logging.update_template()

    # es_sink_offer = ElasticsearchConfigSink("template_offer_v0.json")
    # es_sink_offer.update_template()
