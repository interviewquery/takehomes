# interview
Interview repo for data science

# Prompt

## Introduction
Welcome to Granular's Code Review Technical Challenge! We're excited to see what you find and read your response.

This task involves commenting on a piece of code and its output. You have 24 hours to answer this question, but we expect it to take you at most **2 hours** of work. Your written answer should be **500-1000 words** (entries over 1000 words will be disqualified). To be clear, you will _not_ be writing code, but rather reviewing it.

**Disclaimer:** The code in this exercise is not representative of code quality at Granular. We are presenting code with many errors and something like this would never go into production.

**Happy hunting!**

## Scenario

The file `toy_model_pipeline.py` contains Python code that loads historical data, trains models, and then uses those models to make predictions on a new dataset. `historical.csv` and `new_data.csv` contain train and test sets, respectively. They include simulated land sale data: each row describes a parcel of land. `y` is the sale price. `categorical_mapping.csv` maps the `category` feature to numerical features. `logfile.txt` contains output from running the script. `mse_by_model.png` visualizes the results. The goal is to predict prices as accurately as possible (interpretability is not a concern).

## Your task

Pretend that `toy_model_pipeline.py` is a piece of production code and review it. You should consider **architecture, style, logic, and maintainability** in your commentary. Explain bugs and other errors and give suggestions for improvement. No issue is too big or too small, and nothing is out of scope. Address any `TODO`s you see. When commenting on a specific function, or a specific line of code, please make that clear.  For example, you could structure your feedback like this:

> Lines 77-79: There is a bug related to XYZ. A sentence or two of explanation.

> Lines 82-88: Using parameters ABC for model DEF is a terrible idea. I would use parameter X because Y.

> Lines 203-204: Brittle/copy-pasted code. Needs a function.

> Overall, the code is difficult to maintain because of W. If I were responsible for this code, I'd recommend doing H.

Please send us your review in a text document named `{first_name}_{last_name}_granular_exam.txt`.

## Hints and further guidance
This task is open ended and you should not feel constrained by what follows, but it may be helpful if you are unsure of where to start.

The output of `toy_model_pipeline.py` is puzzling. Look at the plot of model MSEs (mean squared errors) in `mse_by_model.png`: it appears that the models do worse on new data (x=2) than they do on held-out test data (x=1). Is that just a statistical fluke? Also, it looks like the random forest does worse than the linear model. What's going on?

Comment on any other interesting things you see in `mse_by_model.png` (including suggestions for improving the graph), in addition to commenting on the code itself. Your answer may include code snippets if you think that would be useful, but snippets are not required. You are free to run the code yourself as a way of exploring what it does. In case you are unable to run `toy_model_pipeline.py`, we have saved its output for you in `logfile.txt`.
