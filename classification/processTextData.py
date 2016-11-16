# coding: utf-8

# ------ IMPORTS -----
import pandas as pd
from loadAndCleanData import LoadCleanData
from utilNormalizer import Normalizer
import warnings
warnings.filterwarnings("ignore")


class ProcessText:

    def __init__(self):
        self.data = []

    @staticmethod
    # ------ PROCESS DATA -----
    def clean_text_data(df):
        """ Uniformize a column in a DataFrame """
        n = Normalizer()
        df['merge_col'] = df['merge_col'].map(lambda x: x.encode('utf-8') if x != '' else x)
        df['merge_cols_simpl'] = df['merge_col'].map(lambda x: n.end_to_end_normalize(x))
        # Suppress double words and keep order
        df['merge_cols_simpl'] = df['merge_cols_simpl'].map(lambda x: n.clean_duplicate_string(x))
        # Create columns with first letters
        df['merge_col_3'] = df['merge_cols_simpl'].map(lambda x: n.keep_first_letters(x, 3))
        df['merge_col_4'] = df['merge_cols_simpl'].map(lambda x: n.keep_first_letters(x, 4))
        df['merge_col_5'] = df['merge_cols_simpl'].map(lambda x: n.keep_first_letters(x, 5))
        # Merge columns without duplicates
        df['merge_final'] = df['merge_cols_simpl'] + ' ' + df['merge_col_3'] + ' ' + df['merge_col_4'] + ' ' + df['merge_col_5']

        return df


p = ProcessText()
df_open_ff = p.clean_text_data(LoadCleanData().load_and_concat())

print df_open_ff.merge_final[0]
