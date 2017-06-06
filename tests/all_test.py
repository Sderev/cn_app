#!/usr/bin/env python3

"""
This file launches all the tests.

Source used :
    http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
"""

import os
from threading import Thread

os.system('python parsergift_test.py')
os.system('python model_test.py')
os.system('python edx_test.py')
os.system('python ims_test.py')

# class RunTest(Thread):
#
#     def __init__(self, chiffre):
#         Thread.__init__(self)
#         self.chiffre = chiffre
#
#     def run(self):
#         if self.chiffre == 0:
#             execfile('parsergift_test.py')
#         if self.chiffre == 1:
#             execfile('model_test.py')
#         if self.chiffre == 2:
#             execfile('edx_test.py')
#         if self.chiffre == 3:
#             execfile('ims_test.py')
#         else :
#             return
#
# thread_1 = RunTest(0)
# thread_2 = RunTest(1)
#
#     # Lancement des threads
# thread_1.start()
# thread_2.start()
#
#     # Attend que les threads se terminent
# thread_1.join()
# thread_2.join()
