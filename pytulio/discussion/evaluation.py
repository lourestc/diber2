import numpy as np
import scipy.stats as ss

from sklearn.cluster import KMeans
from sklearn import metrics

import matplotlib.pyplot as plt

class Evaluator():

	rand_vmeasure = None #static
	rand_order_correlations = None #static

	def __init__( self, kr, D, cseq ):

		self.name = kr
		self.repr = D
		self.cseq = cseq

		self.vmeasure = None

		self.tdistances = None
		self.tnearest_per_subj = None

		self.order_correlations = None

	def eval_clustering( self ):
		
		if not self.cseq.has_data['subjects']:
			return

		if Evaluator.rand_vmeasure is None:
			self._rand_clustering()

		s_ids = [ t[0][self.cseq.subject_key] for t in self.cseq.Threads.values() ]
		
		ns = len(self.cseq.Subjects)
		kmeans = KMeans( n_clusters=ns, random_state=0 ).fit(self.repr)

		clustering_measures = metrics.homogeneity_completeness_v_measure(s_ids, kmeans.labels_)
		self.vmeasure = clustering_measures[2]

		print( " V-measure ("+self.name+"):", self.vmeasure )
		plt.scatter(self.vmeasure,1,label=self.name)

	#@staticmethod
	def _rand_clustering( self, n_rand_permutations=10000 ):

		if not self.cseq.has_data['subjects']:
			return

		s_ids = [ t[0][self.cseq.subject_key] for t in self.cseq.Threads.values() ]

		Evaluator.rand_vmeasure = []
		for _ in range(n_rand_permutations):
			rand_ids = np.random.choice( np.unique(s_ids), size=len(self.cseq.Threads) )
			clustering_measures = metrics.homogeneity_completeness_v_measure(s_ids, rand_ids)
			Evaluator.rand_vmeasure.append( clustering_measures[2] )

		print( " V-measure (rand):", np.mean(Evaluator.rand_vmeasure), "(mean)" )
		plt.hist( Evaluator.rand_vmeasure, histtype='step', label="rand" )

	def _calc_tdistances( self ):

		if self.tdistances is not None:
			return

		self.tdistances = metrics.pairwise.cosine_distances( self.repr, self.repr )

	def _find_nearest_per_subj( self ):

		if self.tnearest_per_subj is not None:
			return

		self._calc_tdistances()

		tkeys = list(self.cseq.Threads.keys())

		self.tnearest_per_subj = {}
		for ks,s in self.cseq.Subjects.items():

			stkeys = [ t[0][self.cseq.thread_key] for t in s ]
			i_sthreads = np.isin( tkeys, stkeys )

			dist_sthreads = self.tdistances[i_sthreads][:,i_sthreads]
			self.tnearest_per_subj[ks] = np.argsort(dist_sthreads, axis=1)

	def eval_order( self, rand=False ):

		if not self.cseq.has_data['tnumber']:
			return

		if Evaluator.rand_order_correlations is None:
			self._rand_order()

		self._find_nearest_per_subj()

		tkeys = list(self.cseq.Threads.keys())

		self.order_correlations = []

		for ks,s in self.cseq.Subjects.items():

			stkeys = [ t[0][self.cseq.thread_key] for t in s ]

			if len(stkeys)>1:
				stnumbers = [ self.cseq.Threads[kt][0]['tnumber'] for kt in stkeys ]

				stkeys_sorted_by_tnumber = [ x for _,x in sorted(zip(stnumbers,stkeys)) ]
				index_t0 = stkeys.index(stkeys_sorted_by_tnumber[0])
				stkeys_sorted_by_tnearest = [ stkeys[it] for it in self.tnearest_per_subj[ks][index_t0] ]

				self.order_correlations.append( ss.spearmanr(stkeys_sorted_by_tnumber,stkeys_sorted_by_tnearest)[0] )

		print( " KS-stat ("+self.name+"):", ss.ks_2samp(self.order_correlations, self.rand_order_correlations) )
		y = np.array(range(len(self.order_correlations)))/float(len(self.order_correlations))
		x = np.sort(self.order_correlations)
		y = np.concatenate(([0],y))
		x = np.concatenate(([-1],x))
		plt.plot(x,y,label=self.name)
		plt.xlim(-1,1)

	#@staticmethod			
	def _rand_order( self, n_rand_permutations=100 ):

		if not self.cseq.has_data['tnumber']:
			return

		tkeys = list(self.cseq.Threads.keys())

		Evaluator.rand_order_correlations = []

		for ks,s in self.cseq.Subjects.items():

			stkeys = [ t[0][self.cseq.thread_key] for t in s ]

			if len(stkeys)>1:
				stnumbers = [ self.cseq.Threads[kt][0]['tnumber'] for kt in stkeys ]

				stkeys_sorted_by_tnumber = [ x for _,x in sorted(zip(stnumbers,stkeys)) ]

				for _ in range(n_rand_permutations):
					rand_stkeys = np.random.choice( stkeys, size=len(stkeys), replace=False )
					Evaluator.rand_order_correlations.append( ss.spearmanr(stkeys_sorted_by_tnumber,rand_stkeys)[0] )

		y = np.array(range(len(Evaluator.rand_order_correlations)))/float(len(Evaluator.rand_order_correlations))
		x = np.sort(Evaluator.rand_order_correlations)
		y = np.concatenate(([0],y))
		x = np.concatenate(([-1],x))
		plt.plot(x,y,label="rand",linestyle="--")