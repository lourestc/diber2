from pytulio.discussion.dataformats.comseq import *
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
	argparser.add_argument( "-o", "--outpath", help="output folder path", type=str )
	argparser.add_argument( "-c", "--configfile", help="json file containing configuration settings", type=str, default="BenDiTO_aux/config.json" )
	argparser.add_argument( "-v", "--verbose", help="increase output verbosity", action="store_true" )
	#argparser.add_argument( "-v", "--verbose", help="increase output verbosity", action="count", default=0 )
	#argparser.add_argument( "-v", "--verbosity", type=int, choices=[0, 1, 2], help="increase output verbosity" )

	global args
	args = argparser.parse_args()

def read_data():
	if args.verbose: print("Reading comseq data from file '{}'...".format(args.comseq))
	cseq = Comseq( args.comseq )
	if args.verbose: print(" Subjects:", len(cseq.Subjects), "\n", "Threads:", len(cseq.Threads), "\n", "Comments:", len(cseq.Comments))
	return cseq

def read_configuration():
	if args.verbose: print("Reading configuration settings from file '{}'...".format(args.configfile))
	global config
	config = BenditoConfig(args.configfile)
	if args.verbose: print("Done.")

def generates_representations(cseq):

	if args.verbose: print("Generating thread representations...")

	ttext = cseq.threadtext_list()

	thread_reprs = {}

	for kr,repr_generator in config.reprs.items():
		if args.verbose: print( "Generating", kr, "representation..." )
		thread_reprs[kr] = globals()[repr_generator](ttext)
		if args.verbose: print( " {} shape: {}".format(kr, thread_reprs[kr].shape) )

	return thread_reprs

def evaluate_representations(cseq,thread_reprs):

	if args.verbose: print("Evaluating thread representations...")

	evaluators = {}
	for kr,r in thread_reprs.items():
		evaluators[kr] = Evaluator( kr, r, cseq )

	for ke,ev_func in config.evals.items():
		if args.verbose: print("Running evaluation task: "+ke+"...")
		if args.verbose: print("Results:")
		for ev in evaluators.values():
			getattr(ev,ev_func)()
		plt.legend()
		plt.show()

	#Recommendation
	...

	if args.verbose: print("Evaluation complete")

if __name__ == '__main__':

	parse_args()
	
	if args.verbose: print("Running '{}'".format(__file__))

	read_configuration()

	cseq = read_data()

	thread_reprs = generates_representations( cseq )

	evaluate_representations( cseq, thread_reprs )

	if args.verbose: print("Benchmark over")