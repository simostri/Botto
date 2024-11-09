import os
import pandas as pd
from typing import List, Tuple, Dict
from plot_utils import (
    plot_total_investment,
    plot_individual_investments,
    plot_selected_etfs_percentage_increase
)

class ETFPortfolioSimulator:
    def __init__(self, path: str, portfolios: List[Tuple[List[str], List[float], List[str]]], initial_budget: float):
        self.path = path
        self.portfolios = portfolios
        self.initial_budget = initial_budget
        self.monthly_increase = monthly_increase  # Amount added to the budget each month
        self.portfolio_data = []
        self.investment_values = []
        self.investment_values_no_rebalance = []
        self.total_investments = []
        self.total_investments_no_rebalance = []
        self.percentage_increase_no_rebalance = []
        self.rebalance_dates = []

    def load_data(self, start_date: str = '2017-03-01', end_date: str = None):
        """Load and prepare ETF data for each portfolio."""
        for portfolio_files, _, etf_names in self.portfolios:
            portfolio_df_list = []
            for file, etf_name in zip(portfolio_files, etf_names):
                full_path = os.path.join(self.path, file)
                df = pd.read_csv(full_path, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
                df = df.loc[start_date:end_date] if end_date else df.loc[start_date:]
                df.rename(columns={'Close': etf_name}, inplace=True)
                df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0]) - 1
                portfolio_df_list.append(df)
            self.portfolio_data.append(portfolio_df_list)

    def calculate_investment_values(self, rebalance: bool = True):
        """Calculate investment values over time with optional rebalancing."""
        dates = self.portfolio_data[0][0].index[:-1]
        if rebalance:
            self.rebalance_dates = dates[dates.month % 6 == dates[0].month % 6]

        for n, (_, allocations, etf_names) in enumerate(self.portfolios):
            investment_over_time = self._calculate_portfolio_growth(n, dates, allocations, etf_names, rebalance)
            if rebalance:
                self.investment_values.append(investment_over_time['individual'])
                self.total_investments.append(investment_over_time['total'])
            else:
                self.investment_values_no_rebalance.append(investment_over_time['individual'])
                self.total_investments_no_rebalance.append(investment_over_time['total'])

    def _calculate_portfolio_growth(self, n, dates, allocations, etf_names, rebalance):
        quota_invested = [self.initial_budget * allocation for allocation in allocations]
        current_investments = quota_invested.copy()
        investment_values_over_time = {name: [] for name in etf_names}
        total_investment_over_time = []

        for date in dates:
            if rebalance and date in self.rebalance_dates:
                period_date_zero = date
                total_value = sum(current_investments)
                quota_invested = [total_value * allocation for allocation in allocations]
                
            for i, df in enumerate(self.portfolio_data[n]):
                period_date_zero = period_date_zero if rebalance else dates[0]
                pct_increase = df.loc[date].values[0] / df.loc[period_date_zero].values[0]
                current_investments[i] = quota_invested[i] * pct_increase
                investment_values_over_time[etf_names[i]].append(current_investments[i])
                
            total_investment_over_time.append(sum(current_investments))
        
        return {
            'individual': {name: pd.Series(data=investment_values_over_time[name], index=dates) for name in etf_names},
            'total': pd.Series(data=total_investment_over_time, index=dates)
        }

    def calculate_percentage_increase_no_rebalance(self):
        dates = self.portfolio_data[0][0].index[:-1]
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            percentage_increase_no_rebalance = {name: [] for name in etf_names}
            
            for date in dates:
                for i, df in enumerate(self.portfolio_data[n]):
                    percentage_increase = (df.loc[date].values[0] / df.loc[dates[0]].values[0])
                    percentage_increase_no_rebalance[etf_names[i]].append(percentage_increase)
            
            self.percentage_increase_no_rebalance.append({name: pd.Series(data=percentage_increase_no_rebalance[name], index=dates) for name in etf_names})

    def get_attributes(self) -> Dict:
        return self.__dict__

# Define portfolios and initialize the simulator
path = "/home/simone/Finance/Botto/csvperetf/"
portfolios = [
    (['ITPS.SW.csv', 'IBGX.AS.csv', 'US10.PA.csv', 'IBCI.AS.csv', 'IBGL.AS.csv', 'SGLD.MI.csv','ICOM.L.csv', 'SPPW.DE.csv'], [0.1, 0.15, 0.1, 0.1, 0.1, 0.075, 0.075, 0.3], [
        'iShares $ TIPS UCITS ETF USD',
        'iShares Euro Government Bond 3-5 Year UCITS',
        'Lyxor US Treasury 10+Y (DR) UCITS',
        'IShares Euro Inflation Linked Government Bond UCITS',
        'iShares Euro Government Bond 15-30yr UCITS',
        'Invesco Physical Gold A',
        'Lyxor Commodities Refinitiv/CoreCommodity CRB TR UCITS',
        'SPDR MSCI World UCITS ETF'
    ]),
    (['SGLD.MI.csv','SPPW.DE.csv'], [0.4,0.6], [
        'Invesco Physical Gold A',
        'SPDR MSCI World UCITS ETF'
    ]),
    (['VBK.csv', 'VBR.csv', 'VUG.csv', 'VTV.csv', 'SGLD.MI.csv'], [0.05, 0.1, 0.7, 0.1, 0.05], [
        'Vanguard Small-Cap Growth Index Fund',
        'Vanguard Small-Cap Value Index Fund',
        'Vanguard Growth Index Fund',
        'Vanguard Value Index Fund',
        'Invesco Physical Gold'
    ]),
    (['VOO.csv'], [1], [
        'Vanguard S&P 500'
    ])
]
initial_budget = 10000

# Initialize simulator
simulator = ETFPortfolioSimulator(path, portfolios, initial_budget)
simulator.load_data(start_date='2020-01-01', end_date='2024-05-20')
simulator.calculate_investment_values(rebalance=True)
simulator.calculate_investment_values(rebalance=False)
simulator.calculate_percentage_increase_no_rebalance()  # Ensure this is called

# Plotting calls using plot_utils functions
plot_total_investment(simulator.total_investments, rebalance=True)
plot_total_investment(simulator.total_investments_no_rebalance, rebalance=False)
plot_individual_investments(simulator.investment_values, portfolios)
plot_selected_etfs_percentage_increase(simulator.percentage_increase_no_rebalance,
                                       etf_names=['Invesco Physical Gold A',
                                                  'SPDR MSCI World UCITS ETF'])
