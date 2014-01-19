import argparse
import random
import select
import socket
import time


class Node:
    def __init__(self, config_file, my_id):
        self.config_file = config_file
        self.id = my_id
        self.host = '127.0.0.1'
        self.local_clock = random.randrange(0, 100)
        print("initial clock value", self.local_clock)

        self.nodes = self.get_nodes()
        self.port = int(self.nodes[self.id][1])
        del self.nodes[self.id]

    def run(self):
        read_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        read_socket.bind(('', self.port))
        read_socket.listen(5)
        print("{} listening to {}".format(self.id, self.port))
        
        time.sleep(5)

        rlist = [read_socket]

        for _ in range(40):
            read_ready, _, _ = select.select(rlist, [], [], 0)

            for sock in read_ready:
                if sock is read_socket:
                    #print(self.id, "receiving")
                    self.receive_message(read_socket)

            random.choice([self.local_event, self.send_message])()

    def get_nodes(self):
        nodes = {}
        with open(self.config_file) as f:
            for line in f:
                node_id, host, port = line.split()
                nodes[node_id] = (host, int(port))
        return nodes

    def adjust_clock(self, timestamp):
        self.local_clock = max(self.local_clock, timestamp)

    def increase_clock(self):
        n = random.randrange(1, 6)
        self.local_clock += n
        return n

    def local_event(self):
        n = self.increase_clock()
        print('l', n)

    def send_message(self):
        #self.increase_clock()

        recv_id = random.choice(list(self.nodes.keys()))
        recv_host, recv_port = self.nodes[recv_id]
        #print("{} sending to {}".format(self.id, recv_port))
        message = bytearray('{} {}'.format(self.id, self.local_clock), "ASCII")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((recv_host, recv_port))
        sock.send(message)
        sock.close()

        print('s', recv_id, self.local_clock)

    def receive_message(self, sock):
        conn, addr = sock.accept()
        data = conn.recv(1024)
        sender, timestamp = data.split()
        self.adjust_clock(int(timestamp))
        #self.increase_clock()
        print('r', int(sender), int(timestamp), self.local_clock)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file')
    parser.add_argument('line')
    args = parser.parse_args()
    node = Node(args.configuration_file, args.line)
    node.run()


if __name__ == '__main__':
    main()
