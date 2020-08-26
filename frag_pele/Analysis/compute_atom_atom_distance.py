import glob
import os
import argparse
import mdtraj as md
import pandas as pd

def parseArguments():
    """
        Parse the command-line options
        :returns: str, int, int --  path to file to results folder,
            index of the first atom,
            index of the second atom
    """
    desc = "It includes the atom-atom distance of the specified ones to report files\n"
    parser = argparse.ArgumentParser(description=desc)
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument("sim_folder", type=str, help="Path to the simulation results.")

    required_named.add_argument("-a1", type=int, help="Index of the first atom.")
    required_named.add_argument("-a2", type=int, help="Index of the second atom.")
    parser.add_argument("-t", "--traj", default="trajectory_",
                        help="Trajectory file prefix.")
    parser.add_argument("-r", "--rep", default="report_",
                        help="Report file prefix.")
    args = parser.parse_args()
    return args.sim_folder, args.a1, args.a2, args.traj, args.rep


def compute_atom_atom_dist(infile, atomnum1, atomnum2):
    traj = md.load_pdb(infile)
    name ="{}-{}".format(traj.topology.atom(atomnum1), traj.topology.atom(atomnum2))
    return md.compute_distances(traj, [[atomnum1, atomnum2]]), name

def compute_simulation_distance(sim_folder, atomnum1, atomnum2, traj_pref="trajectory_", report_pref="report_"):
    trajectories = sorted(glob.glob("{}*".format(os.path.join(sim_folder, traj_pref))))
    reports = sorted(glob.glob("{}*".format(os.path.join(sim_folder, report_pref))))
    for report, trajectory in zip(reports, trajectories):
        dist, colname = compute_atom_atom_dist(trajectory, atomnum1, atomnum2)
        new_lines = []
        with open(report) as rep:
            rep_lines = rep.readlines()
            rep_lines = [x.strip("\n") for x in rep_lines]
            for ind, line in enumerate(rep_lines):
                new_content = list(line.split("    "))
                new_content = new_content[:-1]
                if ind == 0:
                    new_content.append(colname)
                else:
                    value = "{:.3f}".format(dist[ind-1][0]*10)
                    new_content.append(value)
                new_line = "    ".join(new_content)
                new_lines.append(new_line)
        new_report = "\n".join(new_lines)
        new_rep_name = report.split("/")
        new_rep_name[-1] = "dist" + new_rep_name[-1]
        new_rep_name = "/".join(new_rep_name)
        with open(new_rep_name, "w") as out:
            out.write(new_report)

if __name__ == '__main__':
    sim_fold, atom1, atom2, traj, report = parseArguments()
    compute_simulation_distance(sim_fold, atom1, atom2, traj, report)
