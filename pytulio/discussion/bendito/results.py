import numpy as np
import scipy.stats as ss

import matplotlib.pyplot as plt

class ResultViewer():
	
	def __init__( self, dataname, resultpath, show_plots=False ):
		
		self.dataname = dataname
		self.resultpath = resultpath
		self.show_plots = show_plots
		
	def display( self, evaluators ):
	
		self.resultpath.parent.mkdir( parents=True, exist_ok=True )
		
		etask = next(iter(evaluators.values())).etask
		
		if etask == "cluster_by_subjects":
			self._display_clustering(evaluators)
		elif etask == "compare_thread_order":
			self._display_order(evaluators)
		else:
			eprint("Evaluation task '{}' is invalid.".format(self.etask))
			sys.exit(1)
			
	def _display_clustering( self, evaluators ):
	
		for kr,ev in evaluators.items():
		
			if kr == "random":
				print( " V-measure (rand):", np.mean(ev.results["vmeasure"]), "(mean)" )
				plt.hist( ev.results["vmeasure"], histtype='step', label=ev.rmethod )
			else:
				print( " V-measure ("+ev.rmethod+"):", ev.results["vmeasure"] )
				plt.scatter( ev.results["vmeasure"], 1, label=ev.rmethod )
			
		plt.legend()
		
		if self.show_plots:
			plt.show()
			
		plt.savefig( self.resultpath.with_name("cluster_vmeasures.png") )
		plt.clf()
		
	def _display_order( self, evaluators ):
	
		for kr,ev in evaluators.items():
		
			if kr == "random":
				ls = '--'
			else:
				ls='-'
				ksstat = ss.ks_2samp(ev.results["order_correlations"], evaluators['random'].results["order_correlations"])
				print( " KS-stat ("+ev.rmethod+"):", ksstat )
				
			ncorrs = len(ev.results["order_correlations"])
			y = np.array(range(ncorrs)) / float(ncorrs)
			x = np.sort( ev.results["order_correlations"] )
			y = np.concatenate(([0],y))
			x = np.concatenate(([-1],x))
			
			plt.plot( x, y, label=ev.rmethod, linestyle=ls )
		
		plt.xlim(-1,1)
		plt.legend()
		
		if self.show_plots:
			plt.show()
			
		plt.savefig( self.resultpath.with_name("order_ksstats.png") )
		plt.clf()