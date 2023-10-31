import json
import logging
import os
from pprint import pprint

# import arrow
from google.cloud import firestore


def get_collection(collection_name):
    try:
        client = firestore.Client()

        doc = client.collection(f"{collection_name}").get()
        logging.info(f"Retrieved collection: {collection_name.lower()}")
        return doc.to_dict()
    except Exception as ex:
        logging.error(f"Error: {ex}")

    return None


def get_document(collection_name, config_env):
    try:
        client = firestore.Client()

        doc = client.collection(f"{collection_name}").document(config_env.lower()).get()
        logging.info(f"Retrieved config: {config_env.lower()}")
        return doc.to_dict()
    except Exception as ex:
        logging.error(f"Error: {ex}")

    return None
