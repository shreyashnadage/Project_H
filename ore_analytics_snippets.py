"""
Predefined XML snippets for ORE analytics configurations.
These snippets are used by the ORE Agent to add or modify analytics in ore.xml.
"""

# Dictionary mapping analytic types to their XML configurations
ore_analytics = {
    "npv": """
    <Analytic type="npv">
      <Parameter name="active">Y</Parameter>
      <Parameter name="baseCurrency">EUR</Parameter>
      <Parameter name="outputFileName">npv.csv</Parameter>
    </Analytic>
    """,
    "cashflow": """
    <Analytic type="cashflow">
      <Parameter name="active">Y</Parameter>
      <Parameter name="outputFileName">flows.csv</Parameter>
    </Analytic>
    """,
    "curves": """
    <Analytic type="curves">
      <Parameter name="active">Y</Parameter>
      <Parameter name="outputFileName">curves.csv</Parameter>
    </Analytic>
    """,
    "simulation": """
    <Analytic type="simulation">
      <Parameter name="active">Y</Parameter>
      <Parameter name="simulationConfigFile">simulation.xml</Parameter>
      <Parameter name="pricingEnginesFile">../../Input/pricingengine.xml</Parameter>
      <Parameter name="baseCurrency">EUR</Parameter>
      <Parameter name="cubeFile">cube_A.csv.gz</Parameter>
    </Analytic>
    """,
    "xva": """
    <Analytic type="xva">
      <Parameter name="active">Y</Parameter>
      <Parameter name="calculationType">NoLag</Parameter>
    </Analytic>
    """,
    "sensitivity": """
    <Analytic type="sensitivity">
      <Parameter name="active">Y</Parameter>
      <Parameter name="marketConfigFile">simulation.xml</Parameter>
      <Parameter name="sensitivityConfigFile">sensitivity.xml</Parameter>
      <Parameter name="pricingEnginesFile">../../Input/pricingengine.xml</Parameter>
      <Parameter name="sensitivityOutputFile">sensitivity.csv</Parameter>
    </Analytic>
    """,
    "stress": """
    <Analytic type="stress">
      <Parameter name="active">Y</Parameter>
      <Parameter name="marketConfigFile">simulation.xml</Parameter>
      <Parameter name="stressConfigFile">stresstest.xml</Parameter>
      <Parameter name="pricingEnginesFile">../../Input/pricingengine.xml</Parameter>
      <Parameter name="scenarioOutputFile">stresstest.csv</Parameter>
    </Analytic>
    """,
    "parametricVar": """
    <Analytic type="parametricVar">
      <Parameter name="active">Y</Parameter>
      <Parameter name="sensitivityInputFile">sensitivity.csv</Parameter>
    </Analytic>
    """,
    "historicalSimulationVar": """
    <Analytic type="historicalSimulationVar">
      <Parameter name="active">Y</Parameter>
      <Parameter name="outputFile">var_historical.csv</Parameter>
    </Analytic>
    """,
    "simm": """
    <Analytic type="simm">
      <Parameter name="active">Y</Parameter>
      <Parameter name="version">2.1</Parameter>
      <Parameter name="crif">crif.csv</Parameter>
      <Parameter name="calculationCurrency">USD</Parameter>
    </Analytic>
    """,
    "imschedule": """
    <Analytic type="imschedule">
      <Parameter name="active">Y</Parameter>
      <Parameter name="crif">schedule_crif.csv</Parameter>
      <Parameter name="calculationCurrency">USD</Parameter>
    </Analytic>
    """,
    "zeroToParSensiConversion": """
    <Analytic type="zeroToParSensiConversion">
      <Parameter name="active">Y</Parameter>
      <Parameter name="marketConfigFile">simulation.xml</Parameter>
      <Parameter name="sensitivityConfigFile">sensitivity.xml</Parameter>
      <Parameter name="pricingEnginesFile">../../Input/pricingengine.xml</Parameter>
    </Analytic>
    """,
    "xva": """
    <Analytic type="xva">
      <Parameter name="active">Y</Parameter>
      <Parameter name="csaFile">netting.xml</Parameter>
      <Parameter name="cubeFile">cube.csv.gz</Parameter>
      <Parameter name="scenarioFile">scenariodata.csv.gz</Parameter>
      <Parameter name="collateralBalancesFile">collateralbalances.xml</Parameter>
      <Parameter name="baseCurrency">EUR</Parameter>
      <Parameter name="exposureProfiles">Y</Parameter>
      <Parameter name="exposureProfilesByTrade">Y</Parameter>
      <Parameter name="quantile">0.95</Parameter>
      <Parameter name="calculationType">NoLag</Parameter>
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
      <Parameter name="dimModel">Regression</Parameter>
      <Parameter name="mva">Y</Parameter>
      <Parameter name="dimQuantile">0.99</Parameter>
      <Parameter name="dimHorizonCalendarDays">14</Parameter>
      <Parameter name="dimRegressionOrder">1</Parameter>
      <Parameter name="dimRegressors">EUR-EURIBOR-3M,USD-LIBOR-3M,USD</Parameter>
    </Analytic>
    """
}