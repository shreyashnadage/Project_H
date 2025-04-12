import os
from ORE import *
import sys

f_path_in = 'D:\\Project_H\\Examples\\Example_1\\Inputnew'
f_path_out = 'D:\\Project_H\\Examples\\Example_1\\Output'

# print(os.getcwd())

os.chdir(os.path.dirname(f_path_in))

params = Parameters()
params.fromFile(os.path.join(f_path_in, 'ore.xml'))
ore = OREApp(params, True)
ore.run()