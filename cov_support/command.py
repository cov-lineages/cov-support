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
    parser.add_argument('-n', '--dry-run', action='store_true',help="Go through the motions but don't actually run")
    parser.add_argument('--tempdir',action="store",help="Specify where you want the temp stuff to go. Default: $TMPDIR")
    parser.add_argument("--no-temp",action="store_true",help="Output all intermediate files, for dev purposes.")
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
    - lineages.csv""")
                sys.exit(-1)
        elif not args.data:
            sys.stderr.write(f'Error: please specify data directory')
            sys.exit(-1)
        num_taxa = args.num_taxa
    elif args.update_web:
        


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

    tempdir = ''
    if args.tempdir:
        to_be_dir = os.path.join(cwd, args.tempdir)
        if not os.path.exists(to_be_dir):
            os.mkdir(to_be_dir)
        temporary_directory = tempfile.TemporaryDirectory(suffix=None, prefix=None, dir=to_be_dir)
        tempdir = temporary_directory.name
    else:
        temporary_directory = tempfile.TemporaryDirectory(suffix=None, prefix=None, dir=None)
        tempdir = temporary_directory.name
    
    if args.no_temp:
        print(f"--no-temp: All intermediate files will be written to {outdir}")
        tempdir = outdir

    # how many threads to pass
    if args.threads:
        threads = args.threads
    else:
        threads = 1

    print("Number of threads is", threads)

    config = {
        "lineages":lineages,
        "metadata":metadata,
        "fasta":alignment,
        "global_tree":tree,
        
        "outdir":outdir,
        "tempdir":tempdir,
        "num_taxa":num_taxa
        }

    # find the data
    



    to_include = pkg_resources.resource_filename('cov_support', 'data/to_include.csv')
    config["to_include"] = to_include


    if args.verbose:
        quiet_mode = False
    else:
        quiet_mode = True

    # run subtyping
    status = snakemake.snakemake(snakefile, printshellcmds=True,
                                 dryrun=args.dry_run, forceall=True,force_incomplete=True,
                                 config=config, cores=threads,lock=False,quiet=quiet_mode,workdir=tempdir
                                 )

    if status: # translate "success" into shell exit code of 0
       return 0

    return 1

if __name__ == '__main__':
    main()
