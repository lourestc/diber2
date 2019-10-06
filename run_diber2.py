from pytulio.discussion.dataformats.comseq import *
from pytulio.discussion.bendito.representation import *
from pytulio.discussion.bendito.evaluation import *
from pytulio.discussion.bendito.configuration import *
from pytulio.discussion.bendito.results import *

import matplotlib.pyplot as plt
import argparse
from pathlib import Path

#globals
args = None
config = None
dataname = None

def parse_args():
	argparser = argparse.ArgumentParser( description="Run the DiBER2 benchmark" )
	argparser.add_argument( "comseq", help="input comseq filepath", type=str )
	argparser.add_argument( "outpath", help="output folder path", type=str )
	argparser.add_argument( "-c", "--configfile", help="json file containing configuration settings", type=str, default="BenDiTO_aux/config.json" )
	argparser.add_argument( "-r", "--regen-reprs", help="re-generate representations even if already existis in previous output", action="store_true" )
	argparser.add_argument( "-s", "--show-plots", help="show plots of results, besides only saving", action="store_true" )
	argparser.add_argument( "-v", "--verbose", help="increase output verbosity", action="store_true" )
	#argparser.add_argument( "-v", "--verbose", help="increase output verbosity", action="count", default=0 )
	#argparser.add_argument( "-v", "--verbosity", type=int, choices=[0, 1, 2], help="increase output verbosity" )

	global args
	args = argparser.parse_args()

def read_data():
	if args.verbose: print("Reading comseq data from file '{}'...".format(args.comseq))
	cseq = Comseq( args.comseq )
	global dataname
	#dataname = '.'.join(args.comseq.split('/')[-1].split('.')[:-1])
	dataname = Path(args.comseq).stem
	if args.verbose: print(" Subjects:", len(cseq.Subjects), "\n", "Threads:", len(cseq.Threads), "\n", "Comments:", len(cseq.Comments))
	return cseq

def read_configuration():
	if args.verbose: print("Reading configuration settings from file '{}'...".format(args.configfile))
	global config
	config = BenditoConfig(args.configfile)
	if args.verbose: print("Done.")

def generates_representations(cseq):

	if args.verbose: print("Generating thread representations...")

	thread_reprs = {}	
	for rmethod in config.reprs:
		thread_reprs[rmethod] = Representator( rmethod, dataname )
		
	ttext = cseq.threadtext_list()

	for kr,repr in thread_reprs.items():
	
		loadfile = args.outpath + "/" + repr.dataname + "/reprs/" + kr
		loadpath = Path(loadfile)
		
		if not args.regen_reprs and repr.check_repr_exists( loadpath ):
			if args.verbose: print( "Loading {} representation from '{}'...".format(kr,loadfile) )
			repr.load( loadpath )
		else:
			if args.verbose: print( "Generating", kr, "representation..." )
			repr.generate( ttext )
			repr.save( loadpath )
			
		if args.verbose: print( " {} shape: {}".format(kr, repr.D.shape) )

	return thread_reprs

def evaluate_representations(cseq,thread_reprs):

	if args.verbose: print("Evaluating thread representations...")

	evaluators = {}
	for ke in config.evals:
		evaluators[ke] = {}
		evaluators[ke]['random'] = Evaluator( ke, 'random', dataname, cseq )
		for kr in thread_reprs.keys():
			evaluators[ke][kr] = Evaluator( ke, kr, dataname, cseq )

	for ke in evaluators.keys():
		if args.verbose: print("Running evaluation task: "+ke+"...")
		
		if not next(iter(evaluators[ke].values())).can_eval():
			if args.verbose: print("Can't evaluate for task:", ke)
			break
		
		for kr in evaluators[ke].keys(): #for kr in thread_reprs.keys():
		
			dn = next(iter(evaluators[ke].values())).dataname
			loadfile = args.outpath + "/" + dn + "/evals/" + kr + "/" + ke
			loadpath = Path(loadfile)
				
			if not args.regen_reprs and evaluators[ke][kr].check_results_exist( loadpath ):
				if args.verbose: print( "Loading {} results from '{}'...".format(ke,loadfile) )
				evaluators[ke][kr].load( loadpath )
			else:
				if kr == 'random':
					evaluators[ke][kr].evaluate( None )
				else:
					evaluators[ke][kr].evaluate( thread_reprs[kr].D )
				evaluators[ke][kr].save( loadpath )

	if args.verbose: print("Evaluation complete")
	return evaluators
	
def display_results( evaluators ):

	for ke in evaluators.keys():
	
		if not next(iter(evaluators[ke].values())).can_eval():
			break
	
		if args.verbose: print("Results for task:", ke)
		
		dn = next(iter(evaluators[ke].values())).dataname
		resultfolder = args.outpath + "/" + dn + "/results/" + ke
		resultpath = Path(resultfolder)
		
		viewer = ResultViewer( dn, resultpath, show_plots=args.show_plots )
		viewer.display( evaluators[ke] )

if __name__ == '__main__':

	parse_args()
	
	if args.verbose: print("Running '{}'".format(__file__))

	read_configuration()

	cseq = read_data()

	thread_reprs = generates_representations( cseq )

	evaluators = evaluate_representations( cseq, thread_reprs )
	
	display_results( evaluators )

	if args.verbose: print("Benchmark over")