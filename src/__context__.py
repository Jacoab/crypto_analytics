""" This file lets us import the stock_analytics module in this directory """
import os
import sys

parent_path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(parent_path))

import stock_analytics
