from pytulio.util.error import *

from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
import numpy as np

import sys

class Representator:
	
	def __init__( self, method ):
	
		self.method = method
		self.D = None
		
	def generate( self, text_list ):
	
		if self.method == "TFIDF_base":
			self.tfidf_base(text_list)
		elif self.method == "TFIDF_prod":
			self.tfidf_product(text_list)
		elif self.method == "doc2vec-DM":
			self.doc2vec_dm(text_list)
		elif self.method == "doc2vec-DBOW":
			self.doc2vec_dbow(text_list)
		else:
			eprint("Representation method '{}' is invalid.".format(self.method))
			sys.exit(1)

	def build_tfidf(self, text_list):

		#ORIGINAL: vectorizer = TfidfVectorizer( min_df=2, stop_words = 'english', strip_accents = 'unicode', lowercase=True, ngram_range=(1,2), norm='l2', smooth_idf=True, sublinear_tf=False, use_idf=True )
		vectorizer = TfidfVectorizer( min_df=1, stop_words = 'english', strip_accents = 'unicode', lowercase=True, ngram_range=(1,1), norm='l2', smooth_idf=True, sublinear_tf=False, use_idf=True )
		X = vectorizer.fit_transform(text_list)
		
		return X
		
	def tfidf_base(self, text_list):
		
		self.D = self.build_tfidf(text_list).toarray()

	def tfidf_product(self, text_list):
		
		D = self.build_tfidf(text_list)
		self.D = -(D @ D.T).toarray() # Distance matrix: dot product between tfidf vectors

	def doc2vec( self, text_list, dm=1, repr_size=300, training=40 ):

		#doc_ids = [ t[0][cseq.thread_key] for t in cseq.Threads.values() ]

		#taggeddocs = [ TaggedDocument(com.split(),[str(icom)]) for icom,com in enumerate(text_list) ]

		taggeddocs = [ TaggedDocument(simple_preprocess(doc), [str(idoc)]) for idoc,doc in enumerate(text_list) ]
		
		d2v = Doc2Vec(vector_size=repr_size, min_count=2, epochs=training) #, iter=55)
		d2v.build_vocab(taggeddocs)
		d2v.train(taggeddocs, total_examples=d2v.corpus_count, epochs=d2v.epochs) #, epochs=d2v_model.iter)
		
		#doc_ids = d2v.docvecs.doctags.keys()
		#D = np.array([ d2v.docvecs[did] for did in doc_ids ])

		return d2v.docvecs.doctag_syn0

	def doc2vec_dm( self, text_list, repr_size=300, training=40 ):
		self.D = self.doc2vec( text_list, 1, repr_size, training )

	def doc2vec_dbow( self, text_list, repr_size=300, training=40 ):
		self.D = self.doc2vec( text_list, 0, repr_size, training )