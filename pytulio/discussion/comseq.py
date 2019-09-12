import jsonlines

class Comseq:

    def __init__( self, fname, thread_key='tid', comment_key='cid', subject_key='did', subject_id=None ):

        self.Comments = {} #dict of kc:comment
        self.Threads = {} #list of comments
        self.Subjects = {} #list of comments

        self.subject_key = subject_key
        self.thread_key = thread_key
        self.comment_key = comment_key

        self.has_data = {}

        self.dictionary = None
            
        with jsonlines.open(fname,"r") as f:
            for c in f:
                if subject_id==None or c['did']==subject_id:
                    self.Comments[c[comment_key]] = c

        for c in self.Comments.values():
            self.Threads.setdefault( c[thread_key], [] ).append( c )

        for t in self.Threads.values():
            self.Subjects.setdefault( t[0][subject_key], [] ).append( t )

        if 'ts' in next(iter(self.Comments.values())):
            for t in self.Threads.values():
                t.sort( key=lambda c: c['ts'] )

        self._check_data_availability()

    def _check_data_availability( self ):
        
        #Thread number / thread sequence
        for c in self.Comments.values():
            if 'tnumber' not in c:
                self.has_data['tnumber'] = False
                break
        else: #nobreak
            self.has_data['tnumber'] = True

        #Thread subject
        nsubj = len(set([ t[0][self.subject_key] for t in self.Threads.values() ]))
        self.has_data['subjects'] = nsubj>1

        #Subject co-recommendation
        ...

    def threadtext_list( self ):

        return [ ' '.join([c['c'] for c in t]) for t in self.Threads.values() ]

