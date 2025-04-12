#!/usr/bin/env python
from ORE import *
import sys
sys.path.append('../')
from ore_examples_helper import OreExample

params = Parameters()
params.fromFile("Input/ore.xml")
ore = OREApp(params, False)
ore.run()
errors = ore.getErrors()
# oreex = OreExample(sys.argv[1] if len(sys.argv)>1 else False)

# oreex.print_headline("Run ORE for Sensitivity, Stress and Parametric VaR Analysis")
# oreex.run("Input/ore.xml")
# oreex.get_times("Output/log.txt")

# oreex.print_headline("Run ORE for Parametric VaR Analysis")
# oreex.run("Input/ore_var.xml")
# oreex.get_times("Output/log_var.txt")

test = 0


