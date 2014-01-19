import argparse
import random


class Node:
    def __init__(self, my_id):
        self.id = my_id
        self.local_clock = 0

    def local_event(self):
        n = random.randrange(1, 6)
        self.local_clock += n
        print("l", n)

    def send_message(self):
        pass

    def receive_message(self):
        pass
