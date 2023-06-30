"""
Module with a number of fixed values used throughout program
"""

import sys
import os
from collections import namedtuple


mean_data_tuple = namedtuple("mean_data_tuple", ["name", "order", "n", "mean", "median", "variance", "avg_var",
                                                 "lower_ci", "upper_ci", "lower_bs_ci", "upper_bs_ci", "lower_bias_ci",
                                                 "upper_bias_ci"])

MAJOR_VERSION = 3
MINOR_VERSION = 0
PATCH_VERSION = 13

# validity check when fetching value from data matrix
VALUE_NUMBER = 0
VALUE_STRING = 1
VALUE_ANY = 2

# options for saving the output text
SAVE_TEXT = 0
SAVE_HTML = 1
SAVE_MD = 2


def resource_path(relative_path: str, inc_file: bool = False) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS,
        # and places our data files in a folder relative to that temp
        # folder named as specified in the datas tuple in the spec file
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.join(os.path.dirname(__file__), "..")
    if inc_file:
        return "file://" + os.path.join(base_path, relative_path)
    return os.path.join(base_path, relative_path)


mw3_citation = "Rosenberg, M.S. (2022) <em>MetaWin</em>, Version 3..."
website = "https://www.metawinsoft.com"
download_website = "https://www.metawinsoft.com"

# images and icons
icon_path = os.path.join("resources", "images", "")

exit_icon = resource_path(icon_path + "exit@256px.png")
help_icon = resource_path(icon_path + "button-help-3@256px.png")
ok_icon = resource_path(icon_path + "button-ok-3@256px.png")
save_data_icon = resource_path(icon_path + "save-filled-table@256px.png")
save_output_icon = resource_path(icon_path + "save-filled-text-box@256px.png")
decimal_icon = resource_path(icon_path + "format-decimal@256px.png")
calculator_icon = resource_path(icon_path + "tool-calculator-filled@256px.png")
cancel_icon = resource_path(icon_path + "button-cancel-3@256px.png")
open_icon = resource_path(icon_path + "folder-action-open-filled@256px.png")
clear_icon = resource_path(icon_path + "table-eraser@256px.png")
measure_icon = resource_path(icon_path + "tool-ruler-filled@256px.png")
analysis_icon = resource_path(icon_path + "sum-work-filled@256px.png")
output_icon = resource_path(icon_path + "document-text@256px.png")
data_icon = resource_path(icon_path + "table@256px.png")
graph_icon = resource_path(icon_path + "charts-line-color@256px.png")
tree_icon = resource_path(icon_path + "phylogeny@256px.png")
scatter_icon = resource_path(icon_path + "draw-points@256px.png")
histogram_icon = resource_path(icon_path + "charts-filled@256px.png")
radial_plot_icon = resource_path(icon_path + "draw-radial-plot@256px.png")
forest_plot_icon = resource_path(icon_path + "chart-forest-plot@256px.png")
normal_quantile_icon = resource_path(icon_path + "letter-z-2@256px.png")
norm_dist_icon = resource_path(icon_path + "letter-z-2@256px.png")
t_dist_icon = resource_path(icon_path + "letter-t@256px.png")
gear_icon = resource_path(icon_path + "gear-filled@256px.png")
clear_filter_icon = resource_path(icon_path + "filter-filled-eraser@256px.png")
font_icon = resource_path(icon_path + "text-fonts@256px.png")
row_filter_color_icon = resource_path(icon_path + "table-row-color-wheel@256px.png")
col_filter_color_icon = resource_path(icon_path + "table-column-color-wheel@256px.png")
update_icon = resource_path(icon_path + "cloud-filled-download-filled@256px.png")
save_graph_icon = resource_path(icon_path + "save-filled-picture-filled@256px.png")
edit_graph_icon = resource_path(icon_path + "picture-edit-filled@256px.png")
export_graph_data_icon = resource_path(icon_path + "data-export@256px.png")
analysis_options_icon = resource_path(icon_path + "sum-gear-filled@256px.png")
language_icon = resource_path(icon_path + "translation@256px.png")
alpha_icon = resource_path(icon_path + "letter-alpha@256px.png")
show_toolbar_icon = resource_path(icon_path + "toolbar-position-left-add-filled@256px.png")
hide_toolbar_icon = resource_path(icon_path + "toolbar-position-left-cancel-filled@256px.png")
english_icon = resource_path(icon_path + "flag-united-states@256px.png")
spanish_icon = resource_path(icon_path + "flag-spain@256px.png")
color_swatch_icon = resource_path(icon_path + "color-swatches@256px.png")
pub_bias_icon = resource_path(icon_path + "waste-bin-full-filled-browse@256px.png")

metawin_icon = resource_path(icon_path + "metawin3toolbar_icon.png")
metawin_splash = resource_path(icon_path + "metawin3splash_square.png")

# documentation
# doc_path = os.path.join("..", "resources", "")

doc_path = os.path.join("resources", "")

help_index = {
    "analyses": resource_path(doc_path + "metawin_help.html#analyses", True),
    "basic_analysis": resource_path(doc_path + "metawin_help.html#basic_analysis", True),
    "cumulative_analysis": resource_path(doc_path + "metawin_help.html#cumulative_analysis", True),
    "effect_sizes": resource_path(doc_path + "metawin_help.html#effect_sizes", True),
    "egger_regression": resource_path(doc_path + "metawin_help.html#egger_regression", True),
    "filtering_data": resource_path(doc_path + "metawin_help.html#filtering_data", True),
    "forest_plot": resource_path(doc_path + "metawin_help.html#forest_plot", True),
    "funnel_plot": resource_path(doc_path + "metawin_help.html#funnel_plot", True),
    "galbraith_plot": resource_path(doc_path + "metawin_help.html#galbraith_plot", True),
    "glm_analysis": resource_path(doc_path + "metawin_help.html#glm_analysis", True),
    "graph_edit": resource_path(doc_path + "metawin_help.html#graph_edit", True),
    "grouped_analysis": resource_path(doc_path + "metawin_help.html#grouped_analysis", True),
    "importing_data": resource_path(doc_path + "metawin_help.html#importing_data", True),
    "jackknife_analysis": resource_path(doc_path + "metawin_help.html#jackknife_analysis", True),
    "linear_analysis": resource_path(doc_path + "metawin_help.html#linear_analysis", True),
    "localization": resource_path(doc_path + "metawin_help.html#localization", True),
    "metacalc": resource_path(doc_path + "metacalc_help.html", True),
    "metawin": resource_path(doc_path + "metawin_help.html", True),
    "nested_analysis": resource_path(doc_path + "metawin_help.html#nested_analysis", True),
    "normal_quantile_plot": resource_path(doc_path + "metawin_help.html#normal_quantile_plot", True),
    "phylogenetic_glm": resource_path(doc_path + "metawin_help.html#phylogenetic_glm", True),
    "rank_correlation": resource_path(doc_path + "metawin_help.html#rank_correlation", True),
    "saving_data": resource_path(doc_path + "metawin_help.html#saving_data", True),
    "saving_output": resource_path(doc_path + "metawin_help.html#saving_output", True),
    "scatter_plot": resource_path(doc_path + "metawin_help.html#scatter_plot", True),
    "trim_fill": resource_path(doc_path + "metawin_help.html#trim_fill", True),
    "weighted_histogram": resource_path(doc_path + "metawin_help.html#weighted_histogram", True)
}

# output styles
title_label_style = "font-weight: bold; font-size: 16px"

# full reference and citation list
references = {
    "Adams_et_1997": ["Adams, D.C., J. Gurevitch, and M.S. Rosenberg (1997) Resampling tests for meta-analysis of "
                      "ecological data. <em>Ecology</em> 78:1277&ndash;1283.", "Adams <em>et al.</em> (1997)",
                      "10.1890/0012-9658(1997)078[1277:RTFMAO]2.0.CO;2"],

    "Begg_1994": ["Begg, C.B. (1994) Publication bias. Pp. 399-409 in <em>The Handbook of Research Synthesis</em>, "
                  "H. Cooper and L.V. Hedges, eds. Sage, New York.", "Begg (1994)", ""],

    "Begg_Mazumdar_1994": ["Begg, C.B., and M. Mazumdar (1994) Operating characteristics of a rank correlation test "
                           "for publication bias. <em>Biometrics</em> 50:1088&ndash;1101.", "Begg and Mazumdar (1994)",
                           "10.2307/2533446"],

    "Berlin_et_1989": ["Berlin, J.A., N.M. Laird, H.S. Sacks, and T.C. Chalmers (1989) A comparison of statistical "
                       "methods for combining event rates from clinical trials. <em>Statistics in Medicine</em> "
                       "8:141&ndash;151.", "Berlin <em>et al.</em> (1989)", "10.1002/sim.4780080202"],

    "Chalmers_1991": ["Chalmers, T.C. (1991) Problems induced by meta-analyses. <em>Statistics in Medicine</em> "
                      "10:971&ndash;980.", "Chalmers (1991)", "10.1002/sim.4780100618"],

    "Cooper_1998": ["Cooper, H. (1998) <em>Synthesizing research: A guide for literature reviews</em> (3rd edition). "
                    "Sage, Thousand Oaks, CA.", "Cooper (1998)", ""],

    "DerSimonian_Laird_1986": ["DerSimonian, R., and N. Laird (1986) Meta-analysis in clinical trials. "
                               "<em>Controlled Clinical Trials</em> 7:177&ndash;188.", "DerSimonian and Laird (1986)",
                               "10.1016/0197-2456(86)90046-2"],

    "Dixon_1993": ["Dixon, P.M. (1993) The bootstrap and the jackknife: Describing the precision of ecological "
                   "indices. Pp. 290&mdash;318 in <em>Design and Analysis of Ecological Experiments</em>, "
                   "S.M. Scheiner and J. Gurevitch, eds. Chapman and Hall, New York.", "Dixon (1993)", ""],

    "Duval_Tweedie_2000a": ["Duval, S. and R. Tweedie (2000a) A nonparametric \"trim and fill\" method "
                            "of accounting for publication bias in meta-analysis. <em>Journal of the American "
                            "Statistical Association</em> 95(449):89&ndash;98.", "Duval and Tweedie (2000a)",
                            "10.1080/01621459.2000.10473905"],

    "Duval_Tweedie_2000b": ["Duval, S. and R. Tweedie (2000b) Trim and fill: A simple funnel-plot-based method of "
                            "testing and adjusting for publication bias in meta-analysis. "
                            "<em>Biometrics</em> 56:455&ndash;463.", "Duval and Tweedie (2000b)",
                            "10.1111/j.0006-341X.2000.00455.x"],

    "Egger_et_1997": ["Egger, M., G.D. Smith, M. Schneider, and C. Minder (1997) Bias in meta-analysis detected by a "
                      "simple, graphical test. <em>BMJ</em> 315:629&ndash;634.", "Egger <em>et al.</em> (1997)",
                      "10.1136/bmj.315.7109.629"],

    "Fisher_1928": ["Fisher, R.A. (1928) <em>Statistical methods for research workers</em> (2nd edition). "
                    "Oliver and Boyd, London.", "Fisher (1928)", ""],

    "Galbraith_1988": ["Galbraith, R.F. (1988) A note on graphical presentation of estimated odds ratios from "
                       "several clinical trials. <em>Statistics in Medicine</em> 7:889&ndash;894.",
                       "Galbraith (1988)", "10.1002/sim.4780070807"],

    "Galbraith_1994": ["Galbraith, R.F. (1994) Some applications of radial plots. <em>Journal of the American "
                       "Statistical Association</em> 89:1232&ndash;1242.", "Galbraith (1994)",
                       "10.1080/01621459.1994.10476864"],

    "Greenland_1987": ["Greenland, S. (1987) Quantitative methods in the review of epidemiologic literature. "
                       "<em>Epidemiologic Review</em> 9:1&ndash;30.", "Greenland (1987)",
                       "10.1093/oxfordjournals.epirev.a036298"],

    "Gurevitch_Heges_1993": ["Gurevitch, J., and L.V. Hedges (1993) Meta-analysis: Combining the results of "
                             "independent experiments. Pp. 378&ndash;398 in <em>Design and analysis of "
                             "experiments</em>, S.M. Scheiner and J. Gurevitch, eds. Chapman and Hall, New York.",
                             "Gurevitch and Hedges (1993)", ""],

    "Hedges_Olkin_1985": ["Hedges, L.V. and I. Olkin (1985) <em>Statistical Methods for Meta-analysis</em>. "
                          "Academic Press, Orlando, FL.", "Hedges and Olkin (1985)", ""],

    "Hedges_et_1999": ["Hedges, L.V., J. Gurevitch, and P.S. Curtis (1999) The meta-analysis of response ratios in "
                       "experimental ecology. <em>Ecology</em> 80(4):1150&ndash;1156.",
                       "Hedges <em>et al.</em> (1999)", "10.1890/0012-9658(1999)080[1150:TMAORR]2.0.CO;2"],

    "Higgins_Thompson_2002": ["Higgins, J.P.T. and S.G. Thompson (2002) Quantifying heterogeneity in a meta-analysis. "
                              "<em>Statistics in Medicine</em> 21:1539&ndash;1558.", "Higgins and Thompson (2002)",
                              "10.1002/sim.1186"],

    "Huedo-Medina_et_2006": ["Huedo-Medina, T.B., J. Sánchez-Meca, F. Marín-Martínez, and J. Botella (2006) "
                             "Assessing heterogeneity in meta-analysis: Q statistic or I2 index? "
                             "<em>Psychological Methods</em> 11:193&ndash;206.", "Huedo-Medina <em>et al.</em> (2006)",
                             "10.1037/1082-989X.11.2.193"],

    "Kendall_1938": ["Kendall, M. (1938) A new measure of rank correlation. <em>Biometrika</em>. "
                     "30(1&ndash;2):81&ndash;89.", "Kendall (1938)", "10.1093/biomet/30.1-2.81"],

    "LAbbe_et_1987": ["L&rsquo;Abbé, K.A., A.S. Detsky, and K. O&rsquo;Rourke (1987) Meta-analysis in clinical "
                      "research. <em>Annals of Internal Medicine</em> 107:224&ndash;233.",
                      "L&rsquo;Abbé <em>et al.</em> (1987)", "10.7326/0003-4819-107-2-224"],

    "Lajeunesse_2009": ["Lajeunesse, M.J. (2009) Meta-analysis and the comparative phylogenetic method. <em>American "
                        "Naturalist</em> 174:369&ndash;381.", "Lajeunesse (2009)", "10.1086/603628"],

    "Lajeunesse_et_2013": ["Lajeunesse, M.J., M.S. Rosenberg, and M.D. Jennions (2013) Phylogenetically independent "
                           "meta-analysis. Pp. 284–299 in <em>Handbook of Meta-analysis in Ecology and "
                           "Evolution</em>, J. Koricheva, J. Gurevitch and K.L. Mengersen, eds. Princeton University "
                           "Press: Princeton, NJ.</span></li>", "Lajeunesse <em>et al.</em> (2013)",
                           "10.23943/princeton/9780691137285.003.0017"],

    "Light_Pillemer_1984": ["Light, R.J., and D.B. Pillemer (1984) <em>Summing Up: The Science of Reviewing "
                            "Research</em>. Harvard University Press: Cambridge.", "Light and Pillemer (1984)", ""],

    "Lin_Chu_2018": ["Lin, L., and H. Chu (2018) Quantifying publication bias in meta-analysis. <em>Biometrics</em> "
                     "74(3):785-794.", "Lin and Chu (2018)", "10.1111/biom.12817"],

    "Mantel_and_Haenszel_1959": ["Mantel, N., and W. Haenszel (1959) Statistical aspects of the analysis of data "
                                 "from retrospective studies of disease. <em>Journal of the National Cancer "
                                 "Institute</em> 22:719&ndash;748.", "Mantel and Haenszel (1959)",
                                 "10.1093/jnci/22.4.719"],

    "Mengerson_Gurevitch_2013": ["Mengersen, K., and J. Gurevitch (2013) Using other metrics of effect size in "
                                 "meta-analysis. Pp. 72&ndash;85 in <em>Handbook of Meta-analysis in Ecology and "
                                 "Evolution</em>, J. Koricheva, J. Gurevitch and K.L. Mengersen, eds. "
                                 "Princeton University Press: Princeton, NJ.", "Mengersen and Gurevitch (2013)",
                                 "10.23943/princeton/9780691137285.003.0007"],

    "Nakagawa_et_2022": ["Nakagawa, S., M. Lagisz, M.D. Jennions, J. Koricheva, D.W.A. Noble, T.H. Parker, A. "
                         "Sánchez-Tójar, Y. Yang, and R.E. O'Dea (2022) Methods for testing publication bias in "
                         "ecological and evolutionary meta-analyses. <em>Methods in Ecology and Evolution</em> "
                         "13(1):4&ndash;21.", "Nakagawa <em>et al.</em> (2022)", "10.1111/2041-210X.13724"],

    "Normand_1999": ["Normand, S.-L.T. (1999) Meta-analysis: Formulating, evaluating, combining, and reporting. "
                     "<em>Statistics in Medicine</em> 18:321&mdash;359.", "Normand (1999)",
                     "10.1002/(SICI)1097-0258(19990215)18:3<321::AID-SIM28>3.0.CO;2-P"],

    "Orwin_1983": ["Orwin, R.G. (1983) A fail-safe <em>N</em> for effect size in meta-analysis. <em>Journal of "
                   "Educational Statistics</em> 8(2):157&ndash;159.", "Orwin (1983)", "10.2307/1164923"],

    "Rosenberg_et_2000": ["Rosenberg, M.S., D.C. Adams, and J. Gurevitch (2000) <em>MetaWin: Statistical Software "
                          "for Meta-analysis</em>. Sinauer Associates, Sunderland, MA.",
                          "Rosenberg <em>et al.</em> (2000)", ""],

    "Rosenberg_2005": ["Rosenberg, M.S. (2005) The file-drawer problem revisited: A general weighted method for "
                       "calculating fail-safe numbers in meta-analysis. <em>Evolution</em> 59(2):464&ndash;468.",
                       "Rosenberg (2005)", "10.1554/04-602"],

    "Rosenberg_2013": ["Rosenberg, M.S. (2013) Moment and least-squares based approaches to meta-analytic inference. "
                       "Pp. 108&ndash;124 in <em>Handbook of Meta-analysis in Ecology and Evolution</em>, "
                       "J. Koricheva, J. Gurevitch and K.L. Mengersen, eds. Princeton University Press: Princeton, NJ.",
                       "Rosenberg (2013)", "10.23943/princeton/9780691137285.003.0009"],

    "Rosenthal_1979": ["Rosenthal, R. (1979) The &ldquo;file drawer problem&rdquo; and tolerance for null results. "
                       "<em>Psychological Bulletin</em> 86(3):638&ndash;641.", "Rosenthal (1979)",
                       "10.1037/0033-2909.86.3.638"],

    "Rosenthal_1991": ["Rosenthal, R. (1991) <em>Meta-analytic procedures for social research<em> (revised edition). "
                       "Sage, Newbury Park, CA.", "Rosenthal (1991)", ""],

    "Sokal_Rohlf_1995": ["Sokal, R.R., and F.J. Rohlf (1995) <em>Biometry</em> (3rd edition). Freeman, San Francisco.",
                         "Sokal and Rohlf (1995)", ""],

    "Spearman_1904": ["Spearman C. (1904) The proof and measurement of association between two things. <em>American "
                      "Journal of Psychology</em>. 15(1):72&ndash;101.", "Spearman (1904)", "10.2307/1412159"],

    "Wang_and_Bushman_1998": ["Wang, M.C., and B.J. Bushman (1998) Using the normal quantile plot to explore "
                              "meta-analytic data sets. <em>Psychological Methods</em> 3:46&ndash;54.",
                              "Wang and Bushman (1998)", "10.1037/1082-989X.3.1.46"]
}
