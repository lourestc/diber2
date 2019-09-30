from pytulio.discussion.comseq import *
from pytulio.discussion.bendito.representation import *
from pytulio.discussion.bendito.evaluation import *
from pytulio.discussion.bendito.configuration import *

import matplotlib.pyplot as plt

import argparse

#globals
args = None
config = None

def parse_args():
	argparser = argparse.ArgumentParser( description="Run the DiBER2 benchmark" )
	argparser.add_argument( "comseq", help="input comseq filepath", type=str )
	argparser.add_argument( "-o", "--outfile", help="output filepath", type=str )
	argparser.add_argument( "-c", "--configfile", help="json file containing configuration settings", type=str, default="diber2-config.json" )
	argparser.add_argument( "-v", "--verbose", help="increase output verbosity", action="store_true" )
	#argparser.add_argument( "-v", "--verbose", help="increase output verbosity", action="count", default=0 )
	#argparser.add_argument( "-v", "--verbosity", type=int, choices=[0, 1, 2], help="increase output verbosity" )
	args = argparser.parse_args()

def read_data():
	if args.verbose: print("Reading comseq data from file '{}'...".format(args.comseq))
	cseq = Comseq( args.comseq )
	if args.verbose: print(" Subjects:", len(cseq.Subjects), "\n", "Threads:", len(cseq.Threads), "\n", "Comments:", len(cseq.Comments))
	return cseq

def read_configuration():
	if args.verbose: print("Reading configuration settings from file '{}'...".format(args.configfile))
	config = BenditoConfig(args.configfile)
	if args.verbose: print("Done.")

def generates_representations(cseq):

	if args.verbose: print("Generating thread representations...")

	ttext = cseq.threadtext_list()

	#reprs = { "TFIDF_base":tfidf_basico, "TFIDF_prod":produto_tfidf, "doc2vec-DM":doc2vec_dm, "doc2vec-DBOW":doc2vec_dbow }
	#reprs = { "TFIDF_base":"tfidf_basico", "TFIDF_prod":"produto_tfidf", "doc2vec-DM":"doc2vec_dm", "doc2vec-DBOW":"doc2vec_dbow" }
	reprs = { "TFIDF_prod":"produto_tfidf", "doc2vec-DM":"doc2vec_dm", "doc2vec-DBOW":"doc2vec_dbow" }
	thread_reprs = {}

	for kr,repr_generator in reprs.items():
		if args.verbose: print( "Generating", kr, "representation..." )
		#thread_reprs[kr] = repr_generator(ttext)
		thread_reprs[kr] = globals()[repr_generator](ttext)
		if args.verbose: print( " {} shape: {}".format(kr, thread_reprs[kr].shape) )

	return thread_reprs

def evaluate_representations(cseq,thread_reprs):

	if args.verbose: print("Evaluating thread representations...")

	evaluators = {}
	for kr,r in thread_reprs.items():
		evaluators[kr] = Evaluator( kr, r, cseq )

	evaluations = { "cluster by subjects":"eval_clustering", "compare thread order":"eval_order" }

	for ke,ev_func in evaluations.items():
		if args.verbose: print("Running evaluation task: "+ke+"...")
		if args.verbose: print("Results:")
		for ev in evaluators.values():
			getattr(ev,ev_func)()
		plt.legend()
		plt.show()


	# #Clustering
	# if args.verbose: print("Clustering by subjects...")

	# for ev in evaluators.values():
	# 	ev.eval_clustering()

	# if args.verbose: print("Results:")
	# for ev in evaluators.values():
	# 	ev.eval_clustering()
	# plt.legend()
	# plt.show()

	# if args.verbose: print("Results:")
	# plt.hist(ev.rand_clustering(),histtype='step',label="rand")
	# for kr,ev in evaluators.items():
	# 	print( " V-measure ("+kr+"):", ev.vmeasure )
	# 	plt.scatter(ev.vmeasure,1,label=kr)
	# plt.legend()
	# plt.show()

	# #Thread Order
	# if args.verbose: print("Comparing thread order...")

	# for ev in evaluators.values():
	# 	ev.eval_order()

	# if args.verbose: print("Results:")
	# for ev in evaluators.values():
	# 	ev.eval_order()
	# plt.legend()
	# plt.show()

	# if args.verbose: print("Results:")
	# rand_order_correlations = ev.rand_order()
	# y = np.array(range(len(rand_order_correlations)))/float(len(rand_order_correlations))
	# x = np.sort(rand_order_correlations)
	# y = np.concatenate(([0],y))
	# x = np.concatenate(([-1],x))
	# plt.plot(x,y,label="rand",linestyle="--")
	# for kr,ev in evaluators.items():
	# 	print( " KS-stat ("+kr+"):", ss.ks_2samp(ev.order_correlations, rand_order_correlations) )
	# 	y = np.array(range(len(ev.order_correlations)))/float(len(ev.order_correlations))
	# 	x = np.sort(ev.order_correlations)
	# 	y = np.concatenate(([0],y))
	# 	x = np.concatenate(([-1],x))
	# 	plt.plot(x,y,label=kr)
	# plt.xlim(-1,1)
	# plt.legend()
	# plt.show()

	# #Recommendation
	# ...

	if args.verbose: print("Evaluation complete")

if __name__ == '__main__':

	parse_args()
	
	if args.verbose: print("Running '{}'".format(__file__))

	read_configuration()

	cseq = read_data()

	thread_reprs = generates_representations( cseq )

	evaluate_representations( cseq, thread_reprs )

	if args.verbose: print("Benchmark over")