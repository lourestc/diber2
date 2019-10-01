import json

class BenditoConfig:
	
	def __init__(self,configfile):

		#reprs = { "TFIDF_base":"tfidf_basico", "TFIDF_prod":"produto_tfidf", "doc2vec-DM":"doc2vec_dm", "doc2vec-DBOW":"doc2vec_dbow" }

		print(configfile)

		with open(configfile,'r') as f:
			config = json.load(f)

		#print(ascii(jsonstring))

		self.reprs = config['reprs']
		self.evals = config['evals']