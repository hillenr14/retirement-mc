def calculate_income_tax(w2_income, qualified_dividends, non_qualified_dividends, interest_income,
                         capital_gains, other_income, filing_status, num_qualifying_children,
                         college_invest_contribution):
  # 2023 standard deduction amounts
  standard_deductions = {
      'single': 13850,
      'married_joint': 27700,
      'married_separate': 13850,
      'head_of_household': 20800
  }

  # 2023 tax brackets
  tax_brackets = {
      'single': [
          (0, 11000, 0.10),
          (11000, 44725, 0.12),
          (44725, 95375, 0.22),
          (95375, 182100, 0.24),
          (182100, 231250, 0.32),
          (231250, 578125, 0.35),
          (578125, float('inf'), 0.37)
      ],
      'married_joint': [
          (0, 22000, 0.10),
          (22000, 89450, 0.12),
          (89450, 190750, 0.22),
          (190750, 364200, 0.24),
          (364200, 462500, 0.32),
          (462500, 693750, 0.35),
          (693750, float('inf'), 0.37)
      ],
      'married_separate': [
          (0, 11000, 0.10),
          (11000, 44725, 0.12),
          (44725, 95375, 0.22),
          (95375, 182100, 0.24),
          (182100, 231250, 0.32),
          (231250, 346875, 0.35),
          (346875, float('inf'), 0.37)
      ],
      'head_of_household': [
          (0, 15700, 0.10),
          (15700, 59850, 0.12),
          (59850, 95350, 0.22),
          (95350, 182100, 0.24),
          (182100, 231250, 0.32),
          (231250, 578100, 0.35),
          (578100, float('inf'), 0.37)
      ]
  }

  # Capital gains tax rates for qualified dividends and long-term capital gains
  capital_gains_brackets = {
      'single': [
          (0, 44725, 0.00),
          (44725, 492300, 0.15),
          (492300, float('inf'), 0.20)
      ],
      'married_joint': [
          (0, 89450, 0.00),
          (89450, 553850, 0.15),
          (553850, float('inf'), 0.20)
      ],
      'married_separate': [
          (0, 44725, 0.00),
          (44725, 276900, 0.15),
          (276900, float('inf'), 0.20)
      ],
      'head_of_household': [
          (0, 59850, 0.00),
          (59850, 523050, 0.15),
          (523050, float('inf'), 0.20)
      ]
  }

  # Child Tax Credit parameters
  ctc_amount = 2000  # per qualifying child
  ctc_refundable_limit = 1600  # maximum refundable portion per child
  phase_out_thresholds = {
      'single': 200000,
      'married_joint': 400000,
      'married_separate': 200000,
      'head_of_household': 200000
  }

  # Colorado state tax rate
  colorado_tax_rate = 0.044  # 4.4%

  # Get the standard deduction for the filing status
  standard_deduction = standard_deductions.get(filing_status.lower())
  phase_out_threshold = phase_out_thresholds.get(filing_status.lower())

  if not standard_deduction or not phase_out_threshold:
    raise ValueError(
      "Invalid filing status. Choose from 'single', 'married_joint', 'married_separate', 'head_of_household'")

  # Calculate gross income
  gross_income = w2_income + non_qualified_dividends + \
      interest_income + other_income + capital_gains + qualified_dividends

  # Subtract the standard deduction to get taxable income
  taxable_income = gross_income - standard_deduction
  # Ensure taxable income doesn't go negative
  taxable_income = max(taxable_income, 0)

  # Calculate the ordinary income tax
  # Ordinary income excludes qualified dividends and long-term capital gains
  ordinary_income = taxable_income - qualified_dividends - capital_gains
  ordinary_tax = 0.0

  for lower, upper, rate in tax_brackets[filing_status.lower()]:
    if ordinary_income > lower:
      taxable_part = min(ordinary_income, upper) - lower
      ordinary_tax += taxable_part * rate
    else:
      break

  # Calculate the tax on qualified dividends and long-term capital gains
  qualified_and_capital_tax = 0.0

  for lower, upper, rate in capital_gains_brackets[filing_status.lower()]:
    # if qualified_dividends + capital_gains > lower:
    if taxable_income > lower:
      # taxable_part = min(qualified_dividends + capital_gains, upper) - lower
      # Determine the portion of qualified dividends + capital gains that falls within this bracket
      if ordinary_income < upper:
        taxable_part = min(taxable_income, upper) - max(lower, ordinary_income)
        qualified_and_capital_tax += taxable_part * rate
        print(lower, upper, taxable_part)
    else:
      break

  # Total federal tax before credits
  total_federal_tax_before_credits = ordinary_tax + qualified_and_capital_tax

  # Calculate Child Tax Credit
  ctc_phase_out_amount = max(
    (gross_income - phase_out_threshold) // 1000 * 50, 0)
  ctc = max(ctc_amount * num_qualifying_children - ctc_phase_out_amount, 0)

  # Refundable portion of the Child Tax Credit
  refundable_ctc = min(ctc, ctc_refundable_limit * num_qualifying_children)

  # Calculate total federal tax after Child Tax Credit
  total_federal_tax = max(total_federal_tax_before_credits - ctc, 0)

  # Adjust Colorado taxable income for CollegeInvest contribution
  colorado_taxable_income = taxable_income - college_invest_contribution
  # Ensure it doesn't go negative
  colorado_taxable_income = max(colorado_taxable_income, 0)

  # Calculate Colorado state income tax
  colorado_state_tax = colorado_taxable_income * colorado_tax_rate

  print("taxable income:            ", '${:,.0f}'.format(taxable_income))
  print("ordinary income:           ", '${:,.0f}'.format(ordinary_income))
  print("ordinary tax:              ", '${:,.0f}'.format(ordinary_tax))
  print("qualified and capital tax: ",
        '${:,.0f}'.format(qualified_and_capital_tax))
  print("total federal tax:         ", '${:,.0f}'.format(total_federal_tax))
  print("Colorado taxable income:   ",
        '${:,.0f}'.format(colorado_taxable_income))

  return total_federal_tax, refundable_ctc, colorado_state_tax


# Example usage:
w2_income = 303857  # Replace with actual W-2 income
qualified_dividends = 964  # Replace with actual qualified dividends
non_qualified_dividends = 3345  # Replace with actual non-qualified dividends
interest_income = 10558  # Replace with actual interest income
capital_gains = 543  # Replace with actual capital gains (long-term)
other_income = 1507  # Replace with any other taxable income
filing_status = 'married_joint'  # Replace with actual filing status
# Replace with the number of qualifying children for Child Tax Credit
num_qualifying_children = 1
# Replace with actual CollegeInvest contribution
college_invest_contribution = 24000

federal_tax, refundable_ctc, colorado_tax = calculate_income_tax(w2_income, qualified_dividends, non_qualified_dividends, interest_income,
                                                                 capital_gains, other_income, filing_status, num_qualifying_children,
                                                                 college_invest_contribution)

print(f"Estimated federal tax for {filing_status} with the following incomes:\n"
      f"- W-2 income: ${w2_income}\n"
      f"- Qualified dividends: ${qualified_dividends}\n"
      f"- Non-qualified dividends: ${non_qualified_dividends}\n"
      f"- Interest income: ${interest_income}\n"
      f"- Capital gains: ${capital_gains}\n"
      f"- Other income: ${other_income}\n"
      f"- Number of qualifying children: {num_qualifying_children}\n"
      f"- CollegeInvest contribution: ${college_invest_contribution}\n"
      f"Total estimated federal tax: ${federal_tax:.2f}\n"
      f"Refundable portion of Child Tax Credit: ${refundable_ctc:.2f}\n"
      f"Estimated Colorado state tax: ${colorado_tax:.2f}")
