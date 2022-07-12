## Installations
The libraries I used in this analysis are pandas, seaborn, and numpy. 

## Motivation
This optional portfolio exercise was included as part of the Udacity Data Scientist Nanodegree.

## File descriptions
This directory contains the data files, a test_results.py script to test the promotion strategy,
and the Jupyter notebook with the analysis.

## Summary of results
In the first iteration of this analysis, the approach I adopted was to compare:
- Purchasers vs. non-purchasers in the control group
- Purchasers vs. non-purchasers in the treatment group

Using boxplots for each variable, V1-V7, I was able to see the difference between characteristics of
purchasers and non-purchasers in the control and treatment group. Then, for the promotion strategy,
the simple approach is to use information obtained from only the second comparison, purchasers vs. 
non-purchasers in the treatment group. By strategically selecting thresholds for each variable, we attempt to minimize promotions sent to the users that would not buy. 

With this method, I was able to obtain an IRR/NIR of 0.0216 / 332.20, which exceeded the test solution of 0.0188 / 189.45.

A possible improvement on this method may be trying to identify out of the purchasers in the treatment group, which ones would have purchased without the treatment. This is a more difficult task, as it requires somehow trying to classify users in the purchase/treatment group into two separate sub-groups: those that would purchase without the promotion, and those that purchased only because of the promotion. If there is too much overlap in the two distributions, such a classification may not be easily obtainable. 

