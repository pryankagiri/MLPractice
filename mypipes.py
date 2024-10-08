import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin

## Note you don't need VarSelector this if you are using make_column_transformer and make_pipeline (version 1.3.1 later)
## You can totally comment the VarSelector part and it will still work however I am keeping as is, as there can be a case where somone is using old version of sklearn
## The modified code of mypipes.py work also on older version of sklearn along with newer version
## Older code of "Python Pipeline Building.ipynb" does work with untill 1.2.2 with one change of get_feature_names_out() so use that code if you are using lower version than 1.3.1
## Calling .get_feature_names_out() wouldn't work in newer version of sklearn
## Note the changes made is due to that the interface no longer supports get_feature_names in multiple methods
## The way out is to use make_pipeline and make_column_transformer
## this significantly reduces the need of varselector as a class
## you need to implement get_feature_names_out instead of get_feature_names
## although the second parameter is dummy but is required as internally it requries to have a 2 parameter method
## Also added one fix during one hot encoding

class VarSelector(BaseEstimator, TransformerMixin):

    def __init__(self,feature_names):

        self.feature_names=feature_names


    def fit(self,x,y=None):

        return self

    def transform(self,X):

        return X[self.feature_names]

    def get_feature_names(self):

        return self.feature_names
    
    def get_feature_names_out(self, feature_names_out):

        return self.feature_names



class custom_fico(BaseEstimator,TransformerMixin):

    def __init__(self):

        self.feature_names=['fico']

    def fit(self,x,y=None):

        return self

    def transform(self,X):

        k=X['FICO.Range'].str.split('-',expand=True).astype(float)
        
        fico=0.5*(k[0]+k[1])
        return pd.DataFrame({'fico':fico})

    def get_feature_names(self):

        return self.feature_names
    
    def get_feature_names_out(self, feature_names_out):

        return self.feature_names



class string_clean(BaseEstimator, TransformerMixin):

    def __init__(self,replace_it='',replace_with=''):

        self.replace_it=replace_it
        self.replace_with=replace_with
        self.feature_names=[]

    def fit(self,x,y=None):

        self.feature_names=x.columns
        return self

    def transform(self,X):

        for col in X.columns:
            X[col]=X[col].str.replace(self.replace_it,self.replace_with)
        return X

    def get_feature_names(self):

        return self.feature_names
    
    def get_feature_names_out(self, feature_names_out):

        return self.feature_names



class convert_to_numeric(BaseEstimator, TransformerMixin):

    def __init__(self):

        self.feature_names=[]

    def fit(self,x,y=None):

        self.feature_names=x.columns
        return self

    def transform(self,X):

        for col in X.columns:
            X[col]=pd.to_numeric(X[col],errors='coerce')
        return X

    def get_feature_names(self):
        return self.feature_names
    
    def get_feature_names_out(self, feature_names_out):

        return self.feature_names




class get_dummies_Pipe(BaseEstimator, TransformerMixin):

    def __init__(self,freq_cutoff=0):

        self.freq_cutoff=freq_cutoff
        self.var_cat_dict={}
        self.feature_names=[]

    def fit(self,x,y=None):

        data_cols=x.columns

        for col in data_cols:

            k=x[col].value_counts()

            if (k<=self.freq_cutoff).sum()==0:
                cats=k.index[:-1]

            else:
                cats=k.index[k>self.freq_cutoff]

            self.var_cat_dict[col]=cats

        for col in self.var_cat_dict.keys():
            for cat in self.var_cat_dict[col]:
                ## Added a fix here due to duplicate columns generated
                if col+'_'+ cat not in self.feature_names:
                    self.feature_names.append(col+'_'+cat)

        return self

    def transform(self,x,y=None):
        dummy_data=x.copy()

        for col in self.var_cat_dict.keys():
            for cat in self.var_cat_dict[col]:
                name=col+'_'+cat
                dummy_data[name]=(dummy_data[col]==cat).astype(int)

            del dummy_data[col]

        return dummy_data

    def get_feature_names(self):

        return self.feature_names
    
    def get_feature_names_out(self, feature_names_out):

        return self.feature_names

class DataFrameImputer(BaseEstimator,TransformerMixin):

    def __init__(self):

        self.impute_dict={}
        self.feature_names=[]

    def fit(self, X, y=None):

        self.feature_names=X.columns

        for col in X.columns:
            if X[col].dtype=='O':
                self.impute_dict[col]='missing'
            else:
                self.impute_dict[col]=X[col].median()
        return self

    def transform(self, X, y=None):
        return X.fillna(self.impute_dict)

    def get_feature_names(self):

        return self.feature_names
    
    def get_feature_names_out(self, feature_names_out):

        return self.feature_names

class pdPipeline(Pipeline):

    def get_feature_names(self):

        last_step = self.steps[-1][-1]

        return last_step.get_feature_names()
