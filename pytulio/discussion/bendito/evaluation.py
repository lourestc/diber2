import numpy as np
import scipy.stats as ss

from sklearn.cluster import KMeans
from sklearn import metrics

from pathlib import Path
import sys
import json

class Evaluator():

	rand_vmeasure = None #static
	rand_order_correlations = None #static

	def __init__( self, etask, rmethod, dataname, cseq ):

		self.etask = etask
		self.rmethod = rmethod
		self.dataname = dataname
		self.cseq = cseq
		
		self.results = {}
		
		#####################################

		#self.vmeasure = None

		self.tdistances = None
		self.tnearest_per_subj = None

		#self.order_correlations = None

	def evaluate( self, repr ):
	
		if self.etask == "cluster_by_subjects":
			if self.rmethod == "random":
				self._rand_clustering()
			else:
				self.eval_clustering(repr)
		elif self.etask == "compare_thread_order":
			if self.rmethod == "random":
				self._rand_order()
			else:
				self.eval_order(repr)
		else:
			eprint("Evaluation task '{}' is invalid.".format(self.etask))
			sys.exit(1)
			
	def check_results_exist( self, dir ):
	
		loadfile = dir + "/evals/" + self.dataname + "-" + self.rmethod + "-" + self.etask
		loadpath = Path(loadfile)
	
		return loadpath.with_suffix('.json').exists()
	
	def load( self, dir ):
	
		loadfile = dir + "/evals/" + self.dataname + "-" + self.rmethod + "-" + self.etask
		loadpath = Path(loadfile)
		
		with loadpath.with_suffix('.json').open('r') as f:
			self.results = json.load(f)
		
	def save( self, dir ):
	
		savefile = dir + "/evals/" + self.dataname + "-" + self.rmethod + "-" + self.etask
		savepath = Path(savefile)
		
		savepath.parent.mkdir( parents=True, exist_ok=True )
		with savepath.with_suffix('.json').open('w') as f:
			json.dump(self.results,f)

	def can_eval( self ):
		
		if self.etask == "cluster_by_subjects":
			return self.cseq.has_data['subjects']
		elif self.etask == "compare_thread_order":
			return self.cseq.has_data['tnumber']
		else:
			eprint("Evaluation task '{}' is invalid.".format(self.etask))
			sys.exit(1)
	
	def eval_clustering( self, repr ):
		
		if not self.cseq.has_data['subjects']:
			return

		if Evaluator.rand_vmeasure is None:
			self._rand_clustering()

		s_ids = [ t[0][self.cseq.subject_key] for t in self.cseq.Threads.values() ]
		
		ns = len(self.cseq.Subjects)
		kmeans = KMeans( n_clusters=ns, random_state=0, n_jobs=-1 ).fit(repr)

		clustering_measures = metrics.homogeneity_completeness_v_measure(s_ids, kmeans.labels_)
		self.results["vmeasure"] = clustering_measures[2]
		self.results["kmeans_labels"] = [ x.item() for x in kmeans.labels_]

	def _rand_clustering( self, n_rand_permutations=10000 ):

		if not self.cseq.has_data['subjects']:
			return

		s_ids = [ t[0][self.cseq.subject_key] for t in self.cseq.Threads.values() ]

		self.results["vmeasure"] = []
		for _ in range(n_rand_permutations):
			rand_ids = np.random.choice( np.unique(s_ids), size=len(self.cseq.Threads) )
			clustering_measures = metrics.homogeneity_completeness_v_measure(s_ids, rand_ids)
			self.results["vmeasure"].append( clustering_measures[2] )

	def _calc_tdistances( self, repr ):

		if self.tdistances is not None:
			return

		self.tdistances = metrics.pairwise.cosine_distances( repr, repr )

	def _find_nearest_per_subj( self, repr ):

		if self.tnearest_per_subj is not None:
			return

		self._calc_tdistances(repr)

		tkeys = list(self.cseq.Threads.keys())

		self.tnearest_per_subj = {}
		for ks,s in self.cseq.Subjects.items():

			stkeys = [ t[0][self.cseq.thread_key] for t in s ]
			i_sthreads = np.isin( tkeys, stkeys )

			dist_sthreads = self.tdistances[i_sthreads][:,i_sthreads]
			self.tnearest_per_subj[ks] = np.argsort(dist_sthreads, axis=1)

	def eval_order( self, repr ):

		if not self.cseq.has_data['tnumber']:
			return

		if Evaluator.rand_order_correlations is None:
			self._rand_order()

		self._find_nearest_per_subj(repr)

		tkeys = list(self.cseq.Threads.keys())

		self.results["order_correlations"] = []

		for ks,s in self.cseq.Subjects.items():

			stkeys = [ t[0][self.cseq.thread_key] for t in s ]

			if len(stkeys)>1:
				stnumbers = [ self.cseq.Threads[kt][0]['tnumber'] for kt in stkeys ]

				stkeys_sorted_by_tnumber = [ x for _,x in sorted(zip(stnumbers,stkeys)) ]
				index_t0 = stkeys.index(stkeys_sorted_by_tnumber[0])
				stkeys_sorted_by_tnearest = [ stkeys[it] for it in self.tnearest_per_subj[ks][index_t0] ]

				self.results["order_correlations"].append( ss.spearmanr(stkeys_sorted_by_tnumber,stkeys_sorted_by_tnearest)[0] )
		
	def _rand_order( self, n_rand_permutations=100 ):

		if not self.cseq.has_data['tnumber']:
			return

		tkeys = list(self.cseq.Threads.keys())

		self.results["order_correlations"] = []

		for ks,s in self.cseq.Subjects.items():

			stkeys = [ t[0][self.cseq.thread_key] for t in s ]

			if len(stkeys)>1:
				stnumbers = [ self.cseq.Threads[kt][0]['tnumber'] for kt in stkeys ]

				stkeys_sorted_by_tnumber = [ x for _,x in sorted(zip(stnumbers,stkeys)) ]

				for _ in range(n_rand_permutations):
					rand_stkeys = np.random.choice( stkeys, size=len(stkeys), replace=False )
					self.results["order_correlations"].append( ss.spearmanr(stkeys_sorted_by_tnumber,rand_stkeys)[0] )