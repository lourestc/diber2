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
	
		with self.resultpath.with_name(self.dataname+"cluster_vmeasures.csv").open('w') as f:
			f.write("Representation,V-measure")
			
		plt.figure()
		
		for ev in evaluators.values():
			
			if ev.rmethod == "random":
				vmeasure = np.mean(ev.results["vmeasure"])
				plt.hist( ev.results["vmeasure"], histtype='step', label=ev.rmethod )
			else:
				vmeasure = ev.results["vmeasure"]
				plt.scatter( ev.results["vmeasure"], 1, label=ev.rmethod, alpha=0.5 )
				
			print( " V-measure ("+ev.rmethod+"):", vmeasure )
			with self.resultpath.with_name(self.dataname+"cluster_vmeasures.csv").open('a') as f:
				f.write("\n"+ev.rmethod+","+str(vmeasure))
			
		plt.xlim(0,1)
		plt.legend()
		
		if self.show_plots:
			plt.show()
			
		plt.savefig( self.resultpath.with_name(self.dataname+"cluster_vmeasures.png") )
		plt.clf()
	
	def _colors_from_labels( self, labels ):
    
		color_code_unique = list(set(labels))
		color_codes = []
		for x in labels:
			color_codes.append( float(color_code_unique.index(x)) )

		cmap = plt.get_cmap('jet')
		colors = cmap([ c/max(color_codes) for c in color_codes ])

		# legend = []
		# for x in color_code_unique:
			# c = cmap( color_code_unique.index(x)/max(color_codes) )
			# legend.append( Line2D([0], [0], marker='o', color=c, lw=4, label=d) )
        
		return colors#, legend
	
	def scatter_tsne( self, cseq, tsne ):

		x,y = zip(*tsne)
		
		s_ids = [ t[0][cseq.subject_key] for t in cseq.Threads.values() ]
		colors = self._colors_from_labels(s_ids)
		
		plt.figure()
		plt.scatter(x, y, c=colors, alpha=0.5)
		
		if self.show_plots:
			plt.show()
			
		#plt.axis('off')
		plt.gca().axes.get_yaxis().set_visible(False)
		plt.gca().axes.get_xaxis().set_visible(False)
		plt.savefig( "t1.png" )
		plt.clf()
	
	def _display_order( self, evaluators ):
	
		with self.resultpath.with_name(self.dataname+"order_ksstats.csv").open('w') as f:
			f.write("Representation,KS-stat")
		
		for kr,ev in evaluators.items():
		
			if kr == "random":
				ls = '--'
			else:
				ls='-'
				ksstat = ss.ks_2samp(ev.results["order_correlations"], evaluators['random'].results["order_correlations"])
				print( " KS-stat ("+ev.rmethod+"):", ksstat )
				with self.resultpath.with_name(self.dataname+"order_ksstats.csv").open('a') as f:
					f.write("\n"+ev.rmethod+","+str(ksstat))
				
			ncorrs = len(ev.results["order_correlations"])
			y = np.array(range(ncorrs)) / float(ncorrs)
			x = np.sort( ev.results["order_correlations"] )
			y = np.concatenate(([0],y))
			x = np.concatenate(([-1],x))
			
			plt.plot( x, y, label=ev.rmethod, linestyle=ls )
		
		plt.xlim(-1,1)
		plt.ylim(0,1)
		plt.legend()
		
		if self.show_plots:
			plt.show()
			
		plt.savefig( self.resultpath.with_name(self.dataname+"order_ksstats.png") )
		plt.clf()