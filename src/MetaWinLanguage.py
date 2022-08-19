"""
Localization of text
"""
import MetaWinConstants

current_language = "English"


ENGLISH_DICTIONARY = {"error_not_text_file": "{} does not appear to be a text file.",
                      "error_not_newick": "{} does not appear to contain a phylogeny in Newick format.",
                      "{} studies": "{} studies",
                      "{} studies will be included in this analysis": "{} studies will be included in this analysis",
                      "About Localization": "About Localization",
                      "About MetaWin": "About MetaWin",
                      "Additional Options": "Additional Options",
                      "Analysis": "Analysis",
                      "available": "available",
                      "Automatically check for udpates": "Automatically check for udpates",
                      "Axes Titles": "Axes Titles",
                      "Bar Color": "Bar Color",
                      "Basic Meta-Analysis": "Basic Meta-Analysis",
                      "Between": "Between",
                      "Bootstrap Mean Effect Size(s)": "Bootstrap Mean Effect Size(s)",
                      "bootstrap_caption": " Upward-pointing triangles mark the confidence interval from a "
                                           "bootstrap ({:,} iterations) procedure, following {}; downward-pointing "
                                           "triangles mark the bias-corrected bootstrap interval.",
                      "Bootstrap Confidence Limits": "Bootstrap Confidence Limits",
                      "Bias-corrected Bootstrap Confidence Limits": "Bias-corrected Bootstrap Confidence Limits",
                      "Calculate Effect Sizes": "Calculate Effect Sizes",
                      "Cancel": "Cancel",
                      "Categorical Variables": "Categorical Variables",
                      "Categorical Independent Variables(s)": "Categorical Independent Variable(s)",
                      "Check for updates": "Check for updates",
                      "Choose an Analysis": "Choose an Analysis",
                      "Citation": "Citation",
                      "Citations": "Citations",
                      "Clear Data": "Clear Data",
                      "Clear Filters": "Clear Filters",
                      "Color": "Color",
                      "Column": "Column",
                      "Column Delimiters": "Column Delimiters",
                      "Column headers in first row": "Column headers in first row",
                      "Commas": "Commas",
                      "Complex/GLM": "Complex/GLM",
                      "Complex/GLM Meta-Analysis": "Complex/GLM Meta-Analysis",
                      "Compute": "Compute",
                      "Confidence Intervals": "Confidence Intervals",
                      "Continuous Variables": "Continuous Variables",
                      "Continuous Independent Variables(s)": "Continuous Independent Variable(s)",
                      "Control": "Control",
                      "Control Means": "Control Means",
                      "Control No Response Count": "Control No Response Count",
                      "Control Response Count": "Control Response Count",
                      "Control Sample Sizes": "Control Sample Sizes",
                      "Control Standard Deviations": "Control Standard Deviations",
                      "Count": "Count",
                      " Counts were weighted by a sample size associated with each effect size.":
                          " Counts were weighted by a sample size associated with each effect size.",
                      " Counts were weighted by the inverse of the variance of each effect size.":
                          " Counts were weighted by the inverse of the variance of each effect size.",
                      "Correlation Coefficients": "Correlation Coefficients",
                      "Correlation": "Correlation",
                      "Correlations": "Correlations",
                      "Cumulative Meta-Analysis": "Cumulative Meta-Analysis",
                      "Cumulative Order": "Cumulative Order",
                      "Cumulative Results": "Cumulative Results",
                      "Currently running": "Currently running",
                      "Data": "Data",
                      "Data Decimals": "Data Decimals",
                      "Data for X-axis": "Data for X-axis",
                      "Data for Y-axis": "Data for Y-axis",
                      "Data has not been saved": "Data has not been saved",
                      "Data Location": "Data Location",
                      "Data obtained from columns:": "Data obtained from columns:",
                      "Data Options": "Data Options",
                      "Data Type": "Data Type",
                      "Delimiters": "Delimiters",
                      "Decimal Places": "Decimal Places",
                      "Deselect All": "Deselect All",
                      "Drag and drop variables to indicate desired structure":
                          "Drag and drop variables to indicate desired structure",
                      "drag_nesting":
                          "Drag and drop variables to indicate desired nested structure, from top to bottom.",
                      "Draw": "Draw",
                      "Edge Color": "Edge Color",
                      "Edge Style": "Edge Style",
                      "Edge Width": "Edge Width",
                      "Edit Figure": "Edit Figure",
                      "Effect Size": "Effect Size",
                      "Effect Size Polarity": "Effect Size Polarity",
                      "Effect Size Polarity Indicator": "Effect Size Polarity Indicator",
                      "Effect Size Variance": "Effect Size Variance",
                      "Effect Size Variances": "Effect Size Variances",
                      "Effect Sizes": "Effect Sizes",
                      "Error": "Error",
                      "Error reading file {}": "Error reading file {}",
                      "Error writing to file": "Error writing to file",
                      "Estimator of Missing Studies": "Estimator of Missing Studies",
                      "Estimate of pooled variance": "Estimate of pooled variance",
                      "Exit": "Exit",
                      "Export Figure Data": "Export Figure Data",
                      "exit_download": "Exit {} and open website to download newer version?",
                      "Failsafe Tests": "Failsafe Tests",
                      "Fewer than two studies were valid for analysis":
                          "Fewer than two studies were valid for analysis",
                      "Fewer than two valid groups were identified in column {}":
                          "Fewer than two valid groups were identified in column {}",
                      "Fewer than two valid studies were identified for group {} of column {}.":
                          "Fewer than two valid studies were identified for group {} of column {}.",
                      "nest_error_1": "Fewer than two valid studies were identified for group {} of column {}, "
                                      "based on specified nested structure.",
                      "nest_error_2": "Fewer than two valid child groups were identified for group {} of column {}, "
                                      "based on specified nested structure.",
                      "nest_caption": "Forest plot of effect sizes for the mean of all studies as well as nested "
                                      "subgroups. Arrows in front of labels along the y-axis indicate the degree of "
                                      "nesting.",
                      "Figure": "Figure",
                      "File": "File",
                      "Filter within Column": "Filter within Column",
                      "Filtered Row Color": "Filtered Row Color",
                      "Filtered within Column Color": "Filtered within Column Color",
                      "First Column Contains Row Labels": "First Column Contains Row Labels",
                      "First Row Contains Column Headers": "First Row Contains Column Headers",
                      "fixed effects": "fixed effects",
                      "Fixed Effects Model": "Fixed Effects Model",
                      "Font": "Font",
                      "Forest Plot": "Forest Plot",
                      "Forest plot of individual effect sizes for each study.":
                          "Forest plot of individual effect sizes for each study.",
                      "Forest plot of individual effect sizes for each study, as well as the overall mean.":
                          "Forest plot of individual effect sizes for each study, as well as the overall mean.",
                      "forest_plot_common_caption": " Effect size measured as {}. The dotted vertical line "
                                                    "represents no effect, or a mean of zero. Circles represent "
                                                    "mean effect size, with the corresponding line "
                                                    "the {:0.0%} confidence interval.",
                      "forest_plot_median_caption": " X's represent the median.",
                      "group_forest_plot":
                          "Forest plot of effect sizes for the mean of all studies, as well as subgroups of studies "
                          "designated by {}.",
                      "cumulative_forest_plot":
                          "Forest plot of effect sizes from a cumulative meta-analysis, ranging from the fewest "
                          "studies at the top to the most at the bottom, ordered by {}.",
                      "Galbraith (Radial) Plot": "Galbraith (Radial) Plot",
                      "Global": "Global",
                      "Global Results": "Global Results",
                      "Graph": "Graph",
                      "Graph Cumulative Mean Effect (Forest Plot)": "Graph Cumulative Mean Effect (Forest Plot)",
                      "Graph Effect Sizes and Mean (Forest Plot)": "Graph Effect Sizes and Mean (Forest Plot)",
                      "Graph Jackknife Means (Forest Plot)": "Graph Jackknife Means (Forest Plot)",
                      "Graph Mean Effect Sizes (Forest Plot)": "Graph Mean Effect Sizes (Forest Plot)",
                      "Graph Regression": "Graph Regression",
                      "Graph Trim and Fill Funnel Plot": "Graph Trim and Fill Funnel Plot",
                      "Group Results": "Group Results",
                      "Grouped": "Grouped",
                      "Grouped Meta-Analysis": "Grouped Meta-Analysis",
                      "Groups": "Groups",
                      "Help": "Help",
                      "Heterogeneity": "Heterogeneity",
                      "Hide Data Toolbar": "Hide Data Toolbar",
                      "Hide Output Toolbar": "Hide Output Toolbar",
                      "Hide Phylogeny Tab": "Hide Phylogeny Tab",
                      "Histogram of {} from individual studies.": "Histogram of {} from individual studies.",
                      "Horizontal Axis": "Horizontal Axis",
                      "Horizontal Axis Mean Line": "Horizontal Axis Mean Line",
                      "HTML": "HTML",
                      "Import Error": "Import Error",
                      "Import Text Options": "Import Text Options",
                      "Imported phylogeny from {}": "Imported phylogeny from {}",
                      "Imported phylogeny contains {} tips": "Imported phylogeny contains {} tips",
                      "Include Independent Variables": "Include Independent Variables",
                      "Include Random Effects Variance?": "Include Random Effects Variance?",
                      "Independent Variable": "Independent Variable",
                      "Independent Variables": "Independent Variables",
                      "Indicate Polarity": "Indicate Polarity",
                      "Inferred Data": "Inferred Data",
                      "Inferred Mean": "Inferred Mean",
                      "Input/Output Error": "Input/Output Error",
                      "Invalid Choices": "Invalid Choices",
                      "Inverse Variance": "Inverse Variance",
                      "iterations": "iterations",
                      "Intercept": "Intercept",
                      "Jackknife Meta-Analysis": "Jackknife Meta-Analysis",
                      "Jackknife Results": "Jackknife Results",
                      "jackknife_forest_plot": "Forest plot of mean effect sizes from a jackknife meta-analysis, "
                                               "with the summary repeated with each study removed, one by one.",
                      "Language": "Language",
                      "Line of No Effect": "Line of No Effect",
                      "Linear Meta-Regression Analysis": "Linear Meta-Regression Analysis",
                      "Linear Regression": "Linear Regression",
                      "Load Data": "Load Data",
                      "Loaded data from {}": "Loaded data from {}",
                      "Load Phylogeny": "Load Phylogeny",
                      "Log Transformed Measure": "Log Transformed Measure",
                      "Lower Prediction Limit": "Lower Prediction Limit",
                      "Markdown": "Markdown",
                      "Mean": "Mean",
                      "Means": "Means",
                      "Means and Standard Deviations": "Means and Standard Deviations",
                      "Mean Effect Sizes": "Mean Effect Sizes",
                      "Median": "Median",
                      "Medians": "Medians",
                      "Meta-Analysis": "Meta-Analysis",
                      "minimal effect size": "minimal effect size",
                      "Model": "Model",
                      "Model Results": "Model Results",
                      "nest_structure_error": "You must choose at least two variable to indicate nesting structure.",
                      "Nested Group Analysis": "Nested Group Meta-Analysis",
                      "Nested Groups": "Nested Groups",
                      "Nested Variables": "Nested Variables",
                      "Nested Variables (top to bottom)": "Nested Variables (top to bottom)",
                      "Newer Version Available": "Newer Version Available",
                      "No Newer Version Found": "No Newer Version Found",
                      "No data has been loaded.": "No data has been loaded.",
                      "No effect size could be calculated": "No effect size could be calculated",
                      "No fill color": "No fill color",
                      "No phylogney has been loaded": "No phylogney has been loaded",
                      "No Response": "No Response",
                      "No Weighting": "No Weighting",
                      "None": "None",
                      "Normal Quantile": "Normal Quantile",
                      "Normal Quantile Plot": "Normal Quantile Plot",
                      "normal_quantile_caption": "Normal Quantile plot following {}. The "
                                                 "standardized effect size is the efffect size divided by the "
                                                 "square-root of its variance. The solid line represents the "
                                                 "regression and the dashed lines the 95% prediction envelope.",
                      "note_funnel_plot": "Note: A funnel plot is just a scatter plot of a metric (such as a<br/>"
                                          "mean or effect size) vs. it\'s variance or sample size.",
                      "Number of Bins": "Number of Bins",
                      "Number of decimal places": "Number of decimal places",
                      "Number of Decimal Places to Display": "Number of Decimal Places to Display",
                      "Number of Iterations": "Number of Iterations",
                      "Ok": "Ok",
                      "Options": "Options",
                      "Original Data": "Original Data",
                      "Original Mean": "Original Mean",
                      "Other(s)": "Other(s)",
                      "Output": "Output",
                      "Output Decimals": "Output Decimals",
                      "Output Format": "Output Format",
                      "Output has not been saved": "Output has not been saved",
                      "Output Options": "Output Options",
                      "Pairs of Means": "Pairs of Means",
                      "Phylogenetic GLM Meta-Analysis": "Phylogenetic GLM Meta-Analysis",
                      "Phylogeny": "Phylogeny",
                      "Phylogeny contains {} tips": "Phylogeny contains {} tips",
                      "Phylogeny Tip Names": "Phylogeny Tip Names",
                      "phylogeny_ind_error":
                          "You must choose at least one independent variable in either the categorical or continous "
                          "boxes.",
                      "Plain Text": "Plain Text",
                      "Please filter problematic data to continue": "Please filter problematic data to continue",
                      "Point Data": "Point Data",
                      "Precision": "Precision",
                      "Pre-filtered studies excluded from analysis": "Pre-filtered studies excluded from analysis",
                      "Predictor": "Predictor",
                      "Predictors": "Predictors",
                      "Probabilities": "Probabilities",
                      "Probability": "Probability",
                      "prompt_data_save_clear": "Do you want to save the data before clearing it?",
                      "prompt_data_save_quit": "Do you want to save the data before quitting?",
                      "prompt_output_save_quit": "Do you want to save the output before quitting?",
                      "Radial Arc": "Radial Arc",
                      "Radial Arc Labels": "Radial Arc Labels",
                      "Radial_chart_caption": "Radial chart (Galbraith 1988, 1994) of standardized {} vs. precision. "
                                              "A line from the origin through any point intersects the curve at the "
                                              "effect size for that point. The regression line intersects the curve "
                                              "at the mean effect size.",
                      "Random (Mixed) Effects Model": "Random (Mixed) Effects Model",
                      "random effects": "random effects",
                      "Random Effects Model": "Random Effects Model",
                      "randomization": "randomization",
                      "Randomization Test for Model Structure": "Randomization Test for Model Structure",
                      "Randomization Test for Phylogenetic Structure": "Randomization Test for Phylogenetic Structure",
                      "Randomization to test correlation": "Randomization to test correlation",
                      "Rank Correlation Analysis": "Rank Correlation Analysis",
                      "Rank Correlation Method": "Rank Correlation Method",
                      "Rank Correlation Results": "Rank Correlation Results",
                      "Correlate Effect Size with": "Correlate Effect Size with",
                      "References": "References",
                      "Regression Results": "Regression Results",
                      "regression_caption": "Plot of {} vs. {}, with a {} meta-analytic linear regression following "
                                            "the methods of {}.",
                      "Regression Line": "Regression Line",
                      "Resampling Procedures": "Resampling Procedures",
                      "Response": "Response",
                      "rosenberg_fs_error":
                          "Estimate of pooled variance was less than zero. This fail-safe number cannot be calculated.",
                      "rosenberg_fs_rand":
                          "Estimate of pooled variance is less than zero. No random effects fail-safe number can be "
                          "calculated.",
                      "Row": "Row",
                      "Row labels in first column": "Row labels in first column",
                      "Running most current version available": "Running most current version available",
                      "Sample Size": "Sample Size",
                      "Save Data": "Save Data",
                      "Save Output": "Save Output",
                      "Save Figure": "Save Figure",
                      "Scatter plot of {} vs. {}.": "Scatter plot of {} vs. {}.",
                      "Scatter/Funnel Plot": "Scatter/Funnel Plot",
                      "Select All": "Select All",
                      "Select Groups to Include in Analyses": "Select Groups to Include in Analyses",
                      "Shape": "Shape",
                      "Show Data Toolbar": "Show Data Toolbar",
                      "Show Output Toolbar": "Show Output Toolbar",
                      "Show Phylogeny Tab": "Show Phylogeny Tab",
                      "Significance Level": "Significance Level",
                      "sig_alpha_text": "Significance level (alpha) for confidence intervals and similar tests",
                      "Slope": "Slope",
                      "Source": "Source",
                      "Spaces": "Spaces",
                      "Standard Deviation": "Standard Deviation",
                      "Standardized": "Standardized",
                      "Standardized Effect Size": "Standardized Effect Size",
                      "Started at ": "Started at ",
                      "Statistical Calculator": "Statistical Calculator",
                      "Structure": "Structure",
                      "Studies with invalid data": "Studies with invalid data",
                      "Study": "Study",
                      "Style": "Style",
                      "Tabs": "Tabs",
                      "effect_size_ind_error": "The effect size cannot also be designated as an independent variable.",
                      "Toggle Row Filter": "Toggle Row Filter",
                      "Total": "Total",
                      "Treat Consecutive Delimiters as One": "Treat Consecutive Delimiters as One",
                      "Treatment": "Treatment",
                      "Treatment Means": "Treatment Means",
                      "Treatment No Response Count": "Treatment No Response Count",
                      "Treatment Response Count": "Treatment Response Count",
                      "Treatment Sample Sizes": "Treatment Sample Sizes",
                      "Treatment Standard Deviations": "Treatment Standard Deviations",
                      "Trim and Fill Analysis": "Trim and Fill Analysis",
                      "Trim and Fill Mean": "Trim and Fill Mean",
                      "Trim and Fill Analysis estimated {} missing studies.":
                          "Trim and Fill Analysis estimated {} missing studies.",
                      "trim_fill_caption": "Funnel plot of {} vs. precision, showing the results of a Trim and "
                                           "Fill Analysis ({}). Solid black circles represent the original data; "
                                           "open red circles represent inferred \"missing\" data. The dashed line "
                                           "represents the mean effect size of the original data, the dotted line "
                                           "the mean effect size including the inferred data.",
                      "Two x Two Contingency Table": "Two x Two Contingency Table",
                      "Unable to write to ": "Unable to write to ",
                      "Unused": "Unused",
                      "Upper Prediction Limit": "Upper Prediction Limit",
                      "Use bootstrap for confidence intervals around means":
                          "Use bootstrap for confidence intervals around means",
                      "Use randomization to test model structure": "Use randomization to test model structure",
                      "Use randomization to test phylogenentic structure":
                          "Use randomization to test phylogenentic structure",
                      "Value": "Value",
                      "Variance": "Variance",
                      "Version": "Version",
                      "Vertical Axis": "Vertical Axis",
                      "Vertical Axis Mean Line": "Vertical Axis Mean Line",
                      "Vertical Axis Tick Labels": "Vertical Axis Tick Labels",
                      "Vertical Axis Zero Line": "Vertical Axis Zero Line",
                      "Warning": "Warning",
                      "Weighted Count": "Weighted Count",
                      "Weighted Histogram": "Weighted Histogram",
                      "Weighting": "Weighting",
                      "Width": "Width",
                      "Within": "Within",
                      "You are running the most current version available":
                          "You are running the most current version available",
                      }

# TEST_DICTIONARY = {"About Localization": "About Localization",
#                    "About MetaWin": "Dis Here Be MetaWin",
#                    }


LANGUAGE_DICTIONARY = {
    "English": ENGLISH_DICTIONARY,
    # "Test": TEST_DICTIONARY
}

LANGUAGE_FLAGS = {
    "English": MetaWinConstants.english_icon,
    # "Test": MetaWinConstants.spanish_icon
}


def language_list() -> list:
    return sorted(LANGUAGE_DICTIONARY.keys())


def get_text(key: str) -> str:
    try:
        text = LANGUAGE_DICTIONARY[current_language][key]
    except KeyError:
        text = key
        print("(Internal Warning) {} Dictionary Missing Text: {}".format(current_language, key))

    return text
