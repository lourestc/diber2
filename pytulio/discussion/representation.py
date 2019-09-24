from sklearn.feature_extraction.text import TfidfVectorizer

def monta_tfidf(lista_textos):

	#ORIGINAL: vectorizer = TfidfVectorizer( min_df=2, stop_words = 'english', strip_accents = 'unicode', lowercase=True, ngram_range=(1,2), norm='l2', smooth_idf=True, sublinear_tf=False, use_idf=True )
	vectorizer = TfidfVectorizer( min_df=1, stop_words = 'english', strip_accents = 'unicode', lowercase=True, ngram_range=(1,1), norm='l2', smooth_idf=True, sublinear_tf=False, use_idf=True )
	X = vectorizer.fit_transform(lista_textos)
	
	return X
	
def tfidf_basico(lista_textos):
	
	D = monta_tfidf(lista_textos).toarray()
	return D

def produto_tfidf(lista_textos):
	
	D = monta_tfidf(lista_textos)
	D = -(D @ D.T).toarray() # Distance matrix: dot product between tfidf vectors
	return D

#####################

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
import numpy as np

def doc2vec( lista_textos, dm=1, repr_size=300, training=40 ):

	#doc_ids = [ t[0][cseq.thread_key] for t in cseq.Threads.values() ]

	#taggeddocs = [ TaggedDocument(com.split(),[str(icom)]) for icom,com in enumerate(lista_textos) ]

	taggeddocs = [ TaggedDocument(simple_preprocess(doc), [str(idoc)]) for idoc,doc in enumerate(lista_textos) ]
	
	d2v = Doc2Vec(vector_size=repr_size, min_count=2, epochs=training) #, iter=55)
	d2v.build_vocab(taggeddocs)
	d2v.train(taggeddocs, total_examples=d2v.corpus_count, epochs=d2v.epochs) #, epochs=d2v_model.iter)
	
	#doc_ids = d2v.docvecs.doctags.keys()
	#D = np.array([ d2v.docvecs[did] for did in doc_ids ])

	D = d2v.docvecs.doctag_syn0

	return D

def doc2vec_dm( lista_textos, repr_size=300, training=40 ):
	return doc2vec( lista_textos, 1, repr_size, training )

def doc2vec_dbow( lista_textos, repr_size=300, training=40 ):
	return doc2vec( lista_textos, 0, repr_size, training )