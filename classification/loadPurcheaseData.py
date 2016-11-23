# coding: utf-8

# ------ IMPORTS -----
import cPickle as pickle
import warnings

import boto3

from tfidf_classification import Classification
from utilNormalizer import Normalizer

print "INTO load purchease"

client = boto3.client('s3', region_name="eu-west-1")
tfidfp = client.get_object(Bucket='smartticket-analytics', Key='dumpTfIdf.pkl')
tf_idf_load_from_pickle = pickle.loads(tfidfp['Body'].read())
rfp = client.get_object(Bucket='smartticket-analytics', Key='dumpRf.pkl')
rf_load_from_pickle = pickle.loads(rfp['Body'].read())


warnings.filterwarnings("ignore")

# input = json.load(open("../data/smart-tickets-payload-example.json", "rb"))
# print input

u = Normalizer()

# Load TF-IDF
# tf_idf_load_from_pickle = pickle.load(open("../models/dumpTfIdf.pkl", "rb"))
# Load Random Forest
# rf_load_from_pickle = pickle.load(open("../models/dumpRf.pkl", "rb"))


class LoadPurchease:
    def __init__(self, input_json):
        self.input_json = input_json

    def extract_description(self, input_json):
        """
        Extraction of the description of the products.
        If ocr processed is not empty then it is a key else we use ocr raw
        :param input: json input from pruchease
        :return: dictionary with key equals to production description
        """
        ### TEST ###
        print "TEST"
        print type(input_json['store_address'])
        print input_json['store_address']['street_number']

        dict_description = {}
        for line in input_json['lines']:
            if line['ocr_processed_description'] != "":
                dict_description[line['ocr_processed_description']] = line['category_name']
            else:
                dict_description[line['ocr_raw_description']] = line['category_name']
        return dict_description

    def classification_homemade(self, input_json):
        """
        Classify the products description into a dictionary
        :return: dictionary key: description value : rmw category
        """
        dict_prod = self.extract_description(input_json)
        list_prod = u.from_dict_to_list(dict_prod)
        t = Classification()
        result = t.tfidf_rf_classif_apply(tf_idf_load_from_pickle, rf_load_from_pickle, list_prod)
        return u.from_two_lists_to_dict(list_prod, result)

    def fill_input_with_classif(self, input_json):
        dict_class = self.classification_homemade(input_json)
        output = {}
        output['analytics_result'] = 'FAILURE'
        output['smartticket'] = input_json
        for line in input_json['lines']:
            if line['ocr_processed_description'] != "":
                if dict_class[line['ocr_processed_description']] <> line['category_name']:
                    output['analytics_result'] = 'SUCCESS'
                    line['category_name'] = dict_class[line['ocr_processed_description']].upper()
                    # TODO : change category_image_url too
            else:
                if dict_class[line['ocr_raw_description']] <> line['category_name']:
                    output['analytics_result'] = 'SUCCESS'
                    line['category_name'] = dict_class[line['ocr_raw_description']].upper()
                    # TODO : change category_image_url too
        return output

        # l = LoadPurchease(input)
        # print l.fill_input_with_classif()
