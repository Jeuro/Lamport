"""Lamport clock implementation for the DS project course."""
import argparse
import errno
import os
import random
import select
import socket
import time


class Node:
    def __init__(self, config_file, my_id):
        self.config_file = config_file
        self.id = my_id

        self.host = '127.0.0.1'
        self.filename = '{}_{}'.format(self.id, time.strftime("%Y%m%d_%H:%M:%S", time.gmtime()))
        self.log_file = os.path.join('out', self.filename)

        self.local_clock = 0

        self.nodes = self.get_nodes()
        self.port = int(self.nodes[self.id][1])
        del self.nodes[self.id]

    def run(self):
        read_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        read_socket.bind(('', self.port))
        read_socket.listen(5)

        # Sleep to ensure that all nodes are up before running
        time.sleep(10)

        rlist = [read_socket]

        for _ in range(100):
            read_ready, _, _ = select.select(rlist, [], [], 0)

            # Check if messages have been received
            for sock in read_ready:
                if sock is read_socket:
                    self.receive_message(read_socket)

            # Execute a local event or send a message
            random.choice([self.local_event, self.send_message])()

    def get_nodes(self):
        """Read node information from configuration file into a dictionary and return the dictionary."""
        nodes = {}
        with open(self.config_file) as f:
            for line in f:
                node_id, host, port = line.split()
                nodes[node_id] = (host, int(port))
        return nodes

    def adjust_clock(self, timestamp):
        self.local_clock = max(self.local_clock, timestamp)

    def increment_clock(self):
        n = random.randrange(1, 6)
        self.local_clock += n
        return n

    def write_log(self, message):
        with open(self.log_file, 'a') as f:
            f.write(message)
            f.write('\n')

    def local_event(self):
        n = self.increment_clock()
        self.write_log('l {}'.format(n))

    def send_message(self):
        """Send a message to a randomly chosen node."""
        self.increment_clock()
        # Select a random node
        recv_id = random.choice(list(self.nodes.keys()))
        recv_host, recv_port = self.nodes[recv_id]
        message = bytearray('{} {}'.format(self.id, self.local_clock), "ASCII")

        try:
            # Attempt to send the message
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((recv_host, recv_port))
            sock.send(message)
            sock.close()

            self.write_log('s {} {}'.format(recv_id, self.local_clock))
        except socket.error as err:
            # Ignore error if the connection was refused
            if err.errno == errno.ECONNREFUSED:
                return
            raise err

    def receive_message(self, sock):
        """Read a message from the given socket and execute the algorithm."""
        conn, addr = sock.accept()
        data = conn.recv(1024)
        sender, timestamp = data.split()
        self.adjust_clock(int(timestamp))
        self.write_log('r {} {} {}'.format(int(sender), int(timestamp), self.local_clock))        
        self.increment_clock()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file')
    parser.add_argument('line')
    args = parser.parse_args()
    node = Node(args.configuration_file, args.line)
    node.run()


if __name__ == '__main__':
    main()
