import pandas as pd
from typing import List, Tuple, Dict
from backtesting_utils import calculate_budget, initialize_data, allocate_monthly_addition

class ETFPortfolioSimulator:
    def __init__(self, path: str, portfolios: List[Tuple[List[str], List[float], List[str]]], initial_budget: float, monthly_increase: float):
        self.path = path
        self.portfolios = portfolios
        self.initial_budget = initial_budget
        self.monthly_increase = monthly_increase
        self.portfolio_data = []
        self.investment_values = []
        self.total_investments = []
        self.percentage_increase = []

    def load_and_initialize_data(self, start_date: str = '2017-03-01', end_date: str = None):
        """Load and initialize portfolio data using the initialize_data function."""
        self.portfolio_data = initialize_data(self.path, self.portfolios, start_date, end_date)

    def calculate_investment_values_with_additions(self):
        dates = self.portfolio_data[0][0].index[:-1]

        for n, (_, allocations, etf_names) in enumerate(self.portfolios):
            current_budget = self.initial_budget
            quota_invested = [current_budget * allocation for allocation in allocations]
            current_investments = quota_invested.copy()
            investment_values_over_time = {name: [] for name in etf_names}
            total_investment_over_time = []

            for month_idx, date in enumerate(dates):
                current_budget = calculate_budget(self.initial_budget, self.monthly_increase, month_idx)
                
                # Call allocate_monthly_addition from backtesting_utils
                allocate_monthly_addition(self.portfolio_data, current_investments, etf_names, date, n, self.monthly_increase)

                for i, df in enumerate(self.portfolio_data[n]):
                    percentage_increase = (df.loc[date].values[0] / df.iloc[0].values[0]) - 1
                    current_investments[i] = quota_invested[i] * (1 + percentage_increase)
                    investment_values_over_time[etf_names[i]].append(current_investments[i])

                total_investment_over_time.append(sum(current_investments))

            self.investment_values.append({name: pd.Series(data=investment_values_over_time[name], index=dates) for name in etf_names})
            self.total_investments.append(pd.Series(data=total_investment_over_time, index=dates))

    def get_attributes(self) -> Dict:
        return self.__dict__
