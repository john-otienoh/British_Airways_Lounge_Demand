# Modeling lounge eligibility at Heathrow Terminal 3

## TASK ONE

How using airline data and modeling helps British Airways forecast lounge demand and plan for future capacity planning.

## What you'll do
- Review lounge eligibility criteria and explore how customer groupings can inform lounge demand assumptions.
- Create a reusable lookup table and written justification that British Airways can apply to future flying schedules.

## Background Information
Lounge access is a key part of the premium travel experience, and understanding lounge demand is crucial for British Airways (BA) to maintain high standards while optimizing space and resources. As the airline plans for future operations at Heathrow Terminal 3, it’s important to anticipate demand across different types of lounge access, each associated with varying levels of customer loyalty and travel class.
As BA plans for the future, especially with changes in flying schedules and fleet strategy, it's important to forecast how many passengers will be eligible to use each lounge on a typical day. However, future schedules can be unpredictable, which means we need a modeling approach that is both flexible and scalable.
That’s where you come in. Your job is to create a lookup table that BA can use to estimate lounge eligibility percentages across different flight groupings. This will allow the business to anticipate lounge demand without needing exact flight or aircraft details.
To do this well, you’ll need to think critically about how to group flights in a meaningful way—by time of day, route type, or regional destination, for example, and apply logical assumptions to estimate how many travelers fall into each lounge tier. These estimates will help the Airport Planning team better understand where lounge investments may be needed as operations evolve.
In short, your table and justification will help translate data into decisions—and ensure BA continues to deliver a seamless experience for its most valued customers.

## Understanding lounge eligibility
To begin modeling lounge demand, it’s important to understand who is typically eligible for lounge access. Lounge eligibility is generally based on customer loyalty status and travel class, with different access tiers offering varying levels of amenities.
![alt text](https://cdn.theforage.com/vinternships/companyassets/tMjbs76F526fF5v3G/L3MQ8f6cYSkfoukmz/1747756205049/BA-Lounge%20eligibility.png)
Each tier supports a different group of travelers, and lounge capacity planning depends on forecasting how many eligible passengers fall into each of these categories.
In the next section, you’ll begin thinking about how to estimate the proportion of passengers eligible for each lounge tier, using broad categories that can apply future schedules.

## Creating eligibility assumptions
Now that you understand the lounge tiers, it’s time to think about how you’ll estimate the percentage of customers eligible for each tier across a flight schedule. Since BA is planning far into the future, your model needs to be flexible and based on high-level groupings—not specific flight numbers or aircraft types. 

Your goal is to create a lookup table that estimates lounge eligibility using clear, scalable categories. To do this, you’ll need to decide how to group flights and make logical assumptions.

Common groups include: 

- Time of day: Early morning, mid-day, evening departures.
- Type of route: Short-haul vs. long-haul
- Region or destination group: Europe, North America, Asia, etc.
 
You’ll estimate what proportion of passengers in each group are likely to be eligible for:

- Tier 1: Concorde Room
- Tier 2: First Lounge
- Tier 3: Club Lounge

There is no single correct approach—what matters most is that your assumptions are logical, justifiable, and easy to apply to future schedules.

## Applying assumptions to a flight schedule

You’ve explored lounge eligibility and made thoughtful assumptions—now it’s time to bring it all together. In this part of the task, you’ll apply your model to a real-world scenario using a sample flight schedule.

Instructions: 

1. Download and review the flight schedule provided below.
2. Assign each flight to one of your defined categories (e.g., by time of day, route type, or destination region).
3. Apply your estimated eligibility percentages to each category to calculate the number of passengers likely to use each lounge.

**Note**: The dataset contains a large number of flights. You do not need to analyze all of them. Instead, select a representative sample (e.g., flights within a specific time window or set of destinations) that allows you to test your groupings and apply your assumptions meaningfully.

You can complete this step using a simplified table format. Here’s an example structure to guide you:
![alt text](https://cdn.theforage.com/vinternships/companyassets/tMjbs76F526fF5v3G/L3MQ8f6cYSkfoukmz/1747756528496/_British%20Airways%20-%20Task%201%20table%202%20(1).png)

**Important Note**: While there is currently no Concorde Room at Terminal 3, your Tier 1 estimate may reflect passengers who would qualify for that level of service. This could help to inform whether a Tier 1 Lounge might be needed in the future. Make sure your modeling treats this is a hypothetical or potential space, not a confirmed development.

Focus on applying your assumptions per category—not per individual flight. Your output should be a reusable, generalized lookup table that can be applied to future schedules.

## Submit your work
You're almost there! Now that you've applied your assumptions to the flight schedule and built your lounge eligibility lookup table, it's time to finalize your work and submit it.

Your submission will help BA understand how many passengers are likely to use each of its lounges at Terminal 3. This is your chance to demonstrate how data modeling can support strategic decision-making.

What to submit:

Lounge Eligibility Lookup Table + Justification (Excel): Download and complete the provided Excel template available below. Fill in your estimated percentages for Tier 1, Tier 2, and Tier 3 eligibility by group. 

Then, open the second sheet in the same file titled "Justification." You’ll find four short questions designed to help you reflect on your approach. Use this table to explain:

How you chose to group the flights
Why your groupings make sense for this type of modeling
The assumptions you made and their reasoning
How your model can scale to future or unknown schedules
 
You can write brief but thoughtful responses directly into the table.

```bash
lounge-demand-forecast/
│
├── README.md
├── requirements.txt
├── LICENSE
│
├── data/
│   ├── raw/
│   │   └── BA_Summer_Schedule.xlsx
│   ├── processed/
│   │   ├── flights_clean.csv
│   │   ├── lounge_lookup.csv
│   │   └── eligibility_results.csv
│   └── assumptions/
│       └── eligibility_assumptions.xlsx
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_create_lookup_table.ipynb
│   ├── 03_apply_lookup_to_schedule.ipynb
│   └── 04_capacity_forecast.ipynb
│
├── sql/
│   ├── schema.sql
│   ├── etl.sql
│   └── kpi_queries.sql
│
├── models/
│   ├── grouping_logic.py
│   ├── eligibility_model.py
│   └── forecast_model.py
│
├── dashboards/
│   ├── Lounge_Demand.pbix
│   └── screenshots/
│
├── reports/
│   ├── lounge_lookup_table.xlsx
│   ├── methodology.pdf
│   └── presentation.pptx
│
└── docs/
    ├── data_dictionary.md
    ├── assumptions.md
    └── project_plan.md
```

