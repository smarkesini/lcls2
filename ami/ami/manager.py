import re
import sys
import zmq
import argparse
import threading
from mpi4py import MPI
from ami.comm import Collector
from ami.data import MsgTypes


class Manager(Collector):
    """
    An AMI graph Manager is the control point for an
    active "tree" of workers. It is the final collection
    point for all results, broadcasts those results to 
    clients (e.g. plots/GUIs), and handles requests for
    configuration changes to the graph.
    """

    def __init__(self, gui_port):
        """
        protocol right now only tells you how to communicate with workers
        """
        super(__class__, self).__init__()
        self.feature_store = {}
        self.feature_req = re.compile("feature:(?P<name>.*)")
        self.graph = {}

        # ZMQ setup
        self.ctx = zmq.Context()
        self.comm = self.ctx.socket(zmq.REP)
        print("port", gui_port)
        self.comm.bind("tcp://*:%d" % gui_port)

        self.client_listener_thread = threading.Thread(target=self.client_listener)
        #self.client_listener_thread.daemon = True
        self.client_listener_thread.start()

    def process_msg(self, msg):
        if msg.mtype == MsgTypes.Datagram:
            self.feature_store[msg.payload.name] = msg.payload
            #print(msg.payload)
            #sys.stdout.flush()
        return

    @property
    def features(self):
        dets = {}
        for key, value in self.feature_store.items():
            dets[key] = value.dtype
        return dets

    def feature_request(self, request):
        matched = self.feature_req.match(request)
        if matched:
            print("in feature_request", matched.group('name'))            
            
            reqs = []
            ########## 
            for rank in range(1, MPI.COMM_WORLD.Get_size()):
                reqs.append(MPI.COMM_WORLD.isend([matched.group('name'), 2], tag=2, dest=rank))
            for req in reqs:
                req.wait()
            reqs.clear() 

            # answer from workers on how many images they have
            for i in range(1, MPI.COMM_WORLD.Get_size()):
                answer = MPI.COMM_WORLD.recv(tag=2, source=MPI.ANY_SOURCE)
            
            for rank in range(1, MPI.COMM_WORLD.Get_size()):
                if rank == 1:
                    num = 2
                else:
                    num = 0
                reqs.append(MPI.COMM_WORLD.isend(num, tag=2, dest=rank))
            for req in reqs:
                req.wait()
        
            ###########
            
            if matched.group('name') in self.feature_store:
                self.comm.send_string('ok', zmq.SNDMORE)
                self.comm.send_pyobj(self.feature_store[matched.group('name')].data)
            else:
                self.comm.send_string('error')
            return True
        else:
            return False

    def client_listener(self):
        print('*** started client listen thread')
        sys.stdout.flush()
        while True:
            request = self.comm.recv_string()
            
            # check if it is a feature request
            if not self.feature_request(request):
                if request == 'get_features':
                    self.comm.send_pyobj(self.features)
                elif request == 'get_graph':
                    self.comm.send_pyobj(self.graph)
                elif request == 'set_graph':
                    self.graph = self.recv_graph()
                    sys.stdout.flush()
                    if self.apply_graph():
                        self.comm.send_string('ok')
                    else:
                        self.comm.send_string('error')
                else:
                    self.comm.send_string('error')

    def recv_graph(self):
        return self.comm.recv_pyobj() # zmq for now, could be EPICS in future?

    def apply_graph(self):
        reqs = []
        print("manager: sending requested graph...")
        sys.stdout.flush()
        try:
            for rank in range(1, MPI.COMM_WORLD.Get_size()):
                reqs.append(MPI.COMM_WORLD.isend(self.graph, tag=1, dest=rank))
            for req in reqs:
                req.wait()
        except Exception as exp:
            print("manager: failed to send graph -", exp)
            sys.stdout.flush() 
            return False
        print("manager: sending of graph completed")
        sys.stdout.flush()
        return True


# TJL note to self:
# we do not need this any more

#def main():
#    parser = argparse.ArgumentParser(description='AMII Manager App')
#
#    parser.add_argument(
#        '-H',
#        '--host',
#        default='*',
#        help='interface the AMII manager listens on (default: all)'
#    )
#
#    parser.add_argument(
#        '-p',
#        '--port',
#        type=int,
#        default=5557,
#        help='port for GUI-Manager communication'
#    )
#
#    args = parser.parse_args()
#
#    try:
#        manager = Manager(args.port)
#        return manager.run()
#    except KeyboardInterrupt:
#        print("Manager killed by user...")
#        return 0
#
#
#if __name__ == '__main__':
#    sys.exit(main())


