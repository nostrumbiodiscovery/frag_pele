import sys
import os
import re
import glob
import pandas as pd
import argparse


def parse_arguments():
    """
            Parse user arguments

            Output: list with all the user arguments
        """
    # All the docstrings are very provisional and some of them are old, they would be changed in further steps!!
    parser = argparse.ArgumentParser(description="""From an input file, correspondent to the template of the initial 
        structure of the ligand,this function will generate "x_fragments" intermediate templates until reach the final 
        template,modifying Vann Der Waals, bond lengths and deleting charges.""")
    required_named = parser.add_argument_group('required named arguments')
    # Growing related arguments
    required_named.add_argument("-r", "--rep_pref", required=True,
                                help="""Prefix of the report file: usually 'report_'. """)
    required_named.add_argument("-p", "--path", required=True,
                                help="""Path of the folder to be analyzed""")

    parser.add_argument("-s", "--steps", default=False,
                        help="Used to filter n by PELE steps")
    parser.add_argument("-f", "--file", default=False,
                        help="Used to set the flag 'export file? to True'")
    parser.add_argument("-o", "--out", default="",
                        help="Name of the output file")
    parser.add_argument("-e", "--equil_folder", default="equilibration_result_*",
                        help="Prefix of the equilibration folder (where the results are)")
    parser.add_argument("-c", "--col", default="Binding Energy",
                        help="Name of the column that we will use to find the minimum value of the PELE report")
    parser.add_argument("-q", "--quart", default=0.25,
                        help="Quartile that will be used to compute the mean")

    args = parser.parse_args()

    return args.rep_pref, args.path, args.steps, args.file, args.out, args.equil_folder, args.col, args.quart


def pele_report2pandas(prefix, folder):
    """
        This function merge the content of different report for PELE simulations in a single file pandas Data Frame.
    """
    data = []
    report_list = glob.glob('{}/{}*[0-9]*'.format(folder, prefix))
    for report in report_list:
        tmp_data = pd.read_csv(report, sep='    ', engine='python')
        processor = re.findall('\d+$'.format(prefix), report)
        tmp_data['Processor'] = processor[0]
        data.append(tmp_data)
    return pd.concat(data)


def select_subset_by_steps(dataframe, steps):
    """
    Given a pandas dataframe from PELE's result it returns a subset of n PELE steps.
    :param dataframe: pandas object
    :param steps: int
    :return: dataframe
    """
    subset = dataframe[dataframe['Step'] <= int(steps)]
    return subset


def get_min_value(dataframe, column):
    minimum = dataframe.loc[dataframe[column] == dataframe[column].min()]
    if len(minimum) > 1:
        return minimum.iloc[0][column].min()
    else:
        return minimum[column].min()


def compute_mean_quantile(dataframe, column, quantile_value):
    dataframe = dataframe[dataframe[column] < dataframe[column].quantile(quantile_value)]
    dataframe = dataframe[column]
    mean_subset = dataframe.mean()
    return mean_subset


def get_csv(dataframe, output_path):
    dataframe.to_csv(path_or_buf=output_path, sep='\t', header=True, index=False)


def compute_sterr(dataframe, column, quantile_value):
    dataframe = dataframe[dataframe[column] < dataframe[column].quantile(quantile_value)]
    dataframe = dataframe[column]
    err_subset = dataframe.sem()
    return err_subset


def main(report_prefix, path_to_equilibration, steps=False, out_report=False, column="Binding Energy", quantile_value=0.25):
    folder = glob.glob("{}".format(path_to_equilibration))
    df = pele_report2pandas(report_prefix, folder)
    if steps:
        df = select_subset_by_steps(df, steps)
    mean_quartile = compute_mean_quantile(df, column, quantile_value)
    results = (folder, mean_quartile)
    line_of_report = "{}\t{:.2f}\n".format(results[0], float(results[1]))
    print(line_of_report)
    if out_report:
        if os.path.exists(out_report):
            with open(out_report, "a") as report:
                report.write(line_of_report)
        else:
            with open(out_report, "w") as report:
                report.write("# FragmentResultsFolder\tFrAG-score\n")


if __name__ == '__main__':
    rep_pref, path, steps, file,  equil_folder, out, col, quart = parse_arguments()
    main(report_prefix=rep_pref, path_to_equilibration=path, steps=steps, out_report=out, column=col,
         quantile_value=quart)



