#!/usr/bin/env python3
from cov_support import __version__
import argparse
import os.path
import snakemake
import sys
from tempfile import gettempdir
import tempfile
import pprint
import json

import pkg_resources
from Bio import SeqIO


from . import _program


thisdir = os.path.abspath(os.path.dirname(__file__))
cwd = os.getcwd()

def main(sysargs = sys.argv[1:]):

    parser = argparse.ArgumentParser(prog = _program, 
    description='cov-support: update guide tree or train a new model. Update webpages. Do all sorts of support related tasks')

    parser.add_argument('-o','--outdir', action="store",help="Output directory. Default: current working directory")
    parser.add_argument('-d', '--data', action='store',help="Data directory minimally containing alignment.fasta, global.tree metadata.csv and lineages.csv")
    
    parser.add_argument('--pangolin-prep', action="store_true",help="Run legacy pangolin prep pipeline",dest="pangolin_prep")
    parser.add_argument('--num-taxa', action="store",type=int,default=5,help="Number of taxa in guide tree",dest="num_taxa")
    
    parser.add_argument('--update-web', action="store_true",help="Run website update pipeline",dest="update_web")    
    parser.add_argument('--website-dir', action="store",help="Path to website repo",dest="website_dir")    
    parser.add_argument('--assignment-dir', action="store",help="Path to assignment repo",dest="assignment_dir")    
    parser.add_argument('--updated-metadata', action="store",help="Updated metadata file",dest="metadata")    
    parser.add_argument('--lineage-descriptions', action="store",help="Updated descriptions file",dest="descriptions")    

    parser.add_argument('-n', '--dry-run', action='store_true',help="Go through the motions but don't actually run")
    parser.add_argument('-t', '--threads', action='store',type=int,help="Number of threads")
    parser.add_argument("--verbose",action="store_true",help="Print lots of stuff to screen")
    parser.add_argument("-v","--version", action='version', version=f"pangolin {__version__}")

    if len(sysargs)<1:
        parser.print_help()
        sys.exit(-1)
    else:
        args = parser.parse_args(sysargs)

    if args.pangolin_prep:
        snakefile = os.path.join(thisdir, 'scripts','prepare_package_data.smk')
    # find the Snakefile
    elif args.update_web:
        snakefile = os.path.join(thisdir, 'scripts','update_lineage_data.smk')
    # elif args.run_training:
    #     snakefile
    if not os.path.exists(snakefile):
        sys.stderr.write('Error: cannot find Snakefile at {}\n'.format(snakefile))
        sys.exit(-1)
    else:
        print("Found the snakefile")

    if args.pangolin_prep and args.update_web:
        sys.stderr.write(f'Error: please specify only one of `--pangolin-prep` or `--update-web`')
        sys.exit(-1)
    
    if not args.pangolin_prep and not args.update_web:
        sys.stderr.write(f'Error: please specify either `--pangolin-prep` or `--update-web`')
        sys.exit(-1)

    if args.pangolin_prep:
        if args.data:
            data_dir = os.path.join(cwd, args.data)
            
            metadata = os.path.join(data_dir, "metadata.csv")
            alignment = os.path.join(data_dir, "alignment.fasta")
            tree = os.path.join(data_dir, "global.tree")
            lineages = os.path.join(data_dir, "lineages.csv")
            if not os.path.exists(metadata) or not os.path.exists(alignment) or not os.path.exists(tree) or not os.path.exists(lineages):
                sys.stderr.write(f"""Error: directory must contain the following files:
    - metadata.csv
    - alignment.fasta
    - global.tree
    - lineages.csv\n""")
                sys.exit(-1)
        elif not args.data:
            sys.stderr.write(f'Error: please specify data directory')
            sys.exit(-1)
        num_taxa = args.num_taxa

    outdir = ''
    if args.outdir:
        outdir = os.path.join(cwd, args.outdir)
        if not os.path.exists(outdir):
            try:
                os.mkdir(outdir)
            except:
                sys.stderr.write(f'Error: cannot create directory {outdir}')
                sys.exit(-1)
    else:
        outdir = cwd


    # how many threads to pass
    if args.threads:
        threads = args.threads
    else:
        threads = 1

    print("Number of threads is", threads)

    config = {        
        "outdir":outdir
        }

    if args.pangolin_prep:
        config["lineages"]=lineages
        config["metadata"]=metadata
        config["fasta"]=alignment
        config["global_tree"]=tree
        config["num_taxa"]=num_taxa
    # find the data
    if args.update_web:
        country_coordinates = pkg_resources.resource_filename('cov_support', 'data/country_coordinates.csv')
        config["country_coordinates"] = country_coordinates

        if args.assignment_dir:
            assignment_dir = os.path.join(cwd, args.assignment_dir)
            if not os.path.exists(assignment_dir):
                sys.stderr.write(f'Error: cannot find directory {assignment_dir}')
                sys.exit(-1)
            else:
                config["assignment_dir"] = assignment_dir
        else:
            sys.stderr.write(f'Error: please provide path to assignment repo')
            sys.exit(-1)

        if args.website_dir:
            website_dir = os.path.join(cwd, args.website_dir)
            if not os.path.exists(website_dir):
                sys.stderr.write(f'Error: cannot find directory {website_dir}')
                sys.exit(-1)
            else:
                config["website_dir"] = website_dir
        else:
            sys.stderr.write(f'Error: please provide path to website repo')
            sys.exit(-1)

        if args.metadata:
            metadata = os.path.join(cwd, args.metadata)
            if not os.path.exists(metadata):
                sys.stderr.write(f'Error: cannot find metadata at {metadata}')
                sys.exit(-1)
            else:
                config["metadata"] = metadata
        else:
            sys.stderr.write(f'Error: please provide updated metadata')
            sys.exit(-1)

        if args.descriptions:
            descriptions = os.path.join(cwd, args.descriptions)
            if not os.path.exists(descriptions):
                sys.stderr.write(f'Error: cannot find descriptions at {descriptions}')
                sys.exit(-1)
            else:
                config["descriptions"] = descriptions
        else:
            sys.stderr.write(f'Error: please provide descriptions')
            sys.exit(-1)

        if args.data:
            data_dir = os.path.join(cwd, args.data)
            
            if not os.path.exists(data_dir):
                sys.stderr.write(f'Error: cannot find directory {data_dir}')
                sys.exit(-1)
            else:
                config["data_dir"] = data_dir
                summary_figures = os.path.join("data_dir","summary_figures")
                if not os.path.exists(summary_figures):
                    os.mkdir(summary_figures)
                config["summary_figures_dir"] = summary_figures
                lineages = os.path.join(config["data_dir"],"lineages.metadata.csv")
                recall_file = os.path.join(config["data_dir"],"lineage_recall_report.csv")            
                if not os.path.exists(lineages) or not os.path.exists(recall_file):
                    sys.stderr.write(f"""Error: cannot find files in {data_dir}.\nPlease provide path to:\n \
    - lineage_recall_report.csv 
    - lineages.metadata.csv\n""")
                    sys.exit(-1)
                else:
                    config["lineages_metadata"] = lineages
                    config["recall_file"] = recall_file
        else:
            sys.stderr.write(f'Error: please provide path to data repo')
            sys.exit(-1)
        
    to_include = pkg_resources.resource_filename('cov_support', 'data/to_include.csv')
    config["to_include"] = to_include


    if args.verbose:
        quiet_mode = False
    else:
        quiet_mode = True

    # run subtyping
    status = snakemake.snakemake(snakefile, printshellcmds=True,
                                 dryrun=args.dry_run, forceall=True,force_incomplete=True,
                                 config=config, cores=threads,lock=False,quiet=quiet_mode
                                 )

    if status: # translate "success" into shell exit code of 0
       return 0

    return 1

if __name__ == '__main__':
    main()
