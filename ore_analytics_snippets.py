"""
Predefined XML snippets for ORE analytics configurations.
These snippets are used by the ORE Agent to add or modify analytics in ore.xml.
"""

npv = """<Parameter name="active">Y</Parameter>
    <Parameter name="baseCurrency">EUR</Parameter>
    <Parameter name="outputFileName">npv.csv</Parameter>
  </Analytic>"""

cashflow = """<Analytic type="cashflow">
    <Parameter name="active">Y</Parameter>
    <Parameter name="outputFileName">flows.csv</Parameter>
  </Analytic>"""

curves = """<Analytic type="curves">
    <Parameter name="active">Y</Parameter>
    <Parameter name="configuration">default</Parameter>
    <Parameter name="grid">240,1M</Parameter>
    <Parameter name="outputFileName">curves.csv</Parameter>
  </Analytic>"""
  
additionalResults = """<Analytic type="additionalResults">
    <Parameter name="active">Y</Parameter>
    <Parameter name="outputFileName">additional_results.csv</Parameter>
  </Analytic>"""
  
todaysMarketCalibration = """<Analytic type="todaysMarketCalibration">
    <Parameter name="active">Y</Parameter>
    <Parameter name="outputFileName">todaysmarketcalibration.csv</Parameter>
  </Analytic>"""
  
simulation = """<Analytic type="simulation">
    <Parameter name="active">Y</Parameter>
    <Parameter name="simulationConfigFile">simulation.xml</Parameter>
    <Parameter name="pricingEnginesFile">pricingengine.xml</Parameter>
    <Parameter name="baseCurrency">EUR</Parameter>
    <Parameter name="storeFlows">Y</Parameter>
    <Parameter name="storeSurvivalProbabilities">Y</Parameter>
    <Parameter name="cubeFile">cube_A.dat</Parameter>
    <Parameter name="nettingSetCubeFile">nettingSetCube_A.dat</Parameter>
    <Parameter name="cptyCubeFile">cptyCube_A.dat</Parameter>
    <Parameter name="aggregationScenarioDataFileName">scenariodata.dat</Parameter>
    <Parameter name="aggregationScenarioDump">scenariodump.csv</Parameter>
  </Analytic>"""
  
xva = """<Analytic type="xva">
    <Parameter name="active">Y</Parameter>
    <Parameter name="csaFile">netting.xml</Parameter>
    <Parameter name="cubeFile">cube.dat</Parameter>
    <Parameter name="hyperCube">Y</Parameter>
    <Parameter name="scenarioFile">scenariodata.dat</Parameter>
    <Parameter name="baseCurrency">EUR</Parameter>
    <Parameter name="exposureProfiles">Y</Parameter>
    <Parameter name="exposureProfilesByTrade">Y</Parameter>
    <Parameter name="quantile">0.95</Parameter>
    <Parameter name="calculationType">Symmetric</Parameter>      
    <Parameter name="allocationMethod">None</Parameter>    
    <Parameter name="marginalAllocationLimit">1.0</Parameter>
    <Parameter name="exerciseNextBreak">N</Parameter>
    <Parameter name="cva">Y</Parameter>
    <Parameter name="dva">N</Parameter>
    <Parameter name="dvaName">BANK</Parameter>
    <Parameter name="fva">N</Parameter>
    <Parameter name="fvaBorrowingCurve">BANK_EUR_BORROW</Parameter>
    <Parameter name="fvaLendingCurve">BANK_EUR_LEND</Parameter>
    <Parameter name="colva">Y</Parameter>
    <Parameter name="collateralFloor">Y</Parameter>
    <Parameter name="dynamicCredit">N</Parameter>
    <Parameter name="kva">Y</Parameter>
    <Parameter name="kvaCapitalDiscountRate">0.10</Parameter>
    <Parameter name="kvaAlpha">1.4</Parameter>
    <Parameter name="kvaRegAdjustment">12.5</Parameter>
    <Parameter name="kvaCapitalHurdle">0.012</Parameter>
    <Parameter name="kvaOurPdFloor">0.03</Parameter>
    <Parameter name="kvaTheirPdFloor">0.03</Parameter>
    <Parameter name="kvaOurCvaRiskWeight">0.005</Parameter>
    <Parameter name="kvaTheirCvaRiskWeight">0.05</Parameter>
    <Parameter name="dim">Y</Parameter>
    <Parameter name="mva">Y</Parameter>
    <Parameter name="dimQuantile">0.99</Parameter>
    <Parameter name="dimHorizonCalendarDays">14</Parameter>
    <Parameter name="dimRegressionOrder">1</Parameter>
    <Parameter name="dimRegressors">EUR-EURIBOR-3M,USD-LIBOR-3M,USD</Parameter>
    <Parameter name="dimLocalRegressionEvaluations">100</Parameter>
    <Parameter name="dimLocalRegressionBandwidth">0.25</Parameter>
    <Parameter name="dimScaling">1.0</Parameter>
    <Parameter name="dimEvolutionFile">dim_evolution.txt</Parameter>
    <Parameter name="dimRegressionFiles">dim_regression.txt</Parameter>
    <Parameter name="dimOutputNettingSet">CPTY_A</Parameter>      
    <Parameter name="dimOutputGridPoints">0</Parameter>
    <Parameter name="rawCubeOutputFile">rawcube.csv</Parameter>
    <Parameter name="netCubeOutputFile">netcube.csv</Parameter>
    <Parameter name="fullInitialCollateralisation">true</Parameter>
    <Parameter name="flipViewXVA">N</Parameter>
    <Parameter name="flipViewBorrowingCurvePostfix">_BORROW</Parameter>
    <Parameter name="flipViewLendingCurvePostfix">_LEND</Parameter>
  </Analytic>"""
  
sensitivity = """<Analytic type="sensitivity">
   <Parameter name="active">Y</Parameter>
   <Parameter name="marketConfigFile">simulation.xml</Parameter>
   <Parameter name="sensitivityConfigFile">sensitivity.xml</Parameter>
   <Parameter name="pricingEnginesFile">pricingengine.xml</Parameter>
   <Parameter name="scenarioOutputFile">scenario.csv</Parameter>
   <Parameter name="sensitivityOutputFile">sensitivity.csv</Parameter>
   <Parameter name="crossGammaOutputFile">crossgamma.csv</Parameter>
   <Parameter name="outputSensitivityThreshold">0.000001</Parameter>
   <Parameter name="recalibrateModels">Y</Parameter>
 </Analytic>"""
 
stress = """<Analytic type="stress">
   <Parameter name="active">Y</Parameter>
   <Parameter name="marketConfigFile">simulation.xml</Parameter>
   <Parameter name="stressConfigFile">stresstest.xml</Parameter>
   <Parameter name="pricingEnginesFile">pricingengine.xml</Parameter>
   <Parameter name="scenarioOutputFile">stresstest.csv</Parameter>
   <Parameter name="outputThreshold">0.000001</Parameter>
 </Analytic>"""
 
parametricVar = """<Analytic type="parametricVar"> 
      <Parameter name="active">Y</Parameter> 
      <Parameter name="portfolioFilter">PF1|PF2</Parameter>
      <Parameter name="sensitivityInputFile">
         ../Output/sensitivity.csv,../Output/crossgamma.csv
      </Parameter> 
      <Parameter name="covarianceInputFile">covariance.csv</Parameter> 
      <Parameter name="salvageCovarianceMatrix">N</Parameter>
      <Parameter name="quantiles">0.01,0.05,0.95,0.99</Parameter> 
      <Parameter name="breakdown">Y</Parameter> 
      <!-- Delta, DeltaGammaNormal, MonteCarlo --> 
      <Parameter name="method">DeltaGammaNormal</Parameter> 
      <Parameter name="mcSamples">100000</Parameter> 
      <Parameter name="mcSeed">42</Parameter> 
      <Parameter name="outputFile">var.csv</Parameter> 
    </Analytic>"""
	
scenarioStatistics = """<Analytic type="scenarioStatistics">
	<Parameter name="active">Y</Parameter>
	<Parameter name="simulationConfigFile">simulation.xml</Parameter>
	<Parameter name="distributionBuckets">20</Parameter>
	<Parameter name="outputZeroRate">Y</Parameter>
	<Parameter name="scenariodump">scenariodump.csv</Parameter>
  </Analytic>"""

imschedule = """<Analytic type="imschedule">
 <Parameter name="active">Y</Parameter>
 <Parameter name="crif">schedule_crif.csv</Parameter>
 <Parameter name="calculationCurrency">USD</Parameter>
 </Analytic>"""

initialMargin = """<Analytic type="initialMargin">
      <Parameter name="active">N</Parameter>
      <Parameter name="method" />
    </Analytic>"""

ore_analytics = {
  "npv": npv,
  "cashflow": cashflow,
  "curves": curves,
  "additionalResults": additionalResults,
  "todaysMarketCalibration": todaysMarketCalibration,
  "simulation": simulation,
  "xva": xva,
  "sensitivity": sensitivity,
  "stress": stress,
  "parametricVar": parametricVar,
  "scenarioStatistics": scenarioStatistics,
  "imschedule": imschedule,
  "initialMargin": initialMargin,
  "exposure": xva
}