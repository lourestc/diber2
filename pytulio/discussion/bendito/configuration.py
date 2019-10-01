import json

class BenditoConfig:
	
	def __init__(self,configfile):

		#reprs = { "TFIDF_base":"tfidf_basico", "TFIDF_prod":"produto_tfidf", "doc2vec-DM":"doc2vec_dm", "doc2vec-DBOW":"doc2vec_dbow" }

		with json.open(configfile,'r') as f:

			self.reprs = f['reprs']
			self.evals = f['evals']