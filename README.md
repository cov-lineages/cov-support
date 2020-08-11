# cov-support


### Install cov-support

1. Clone this repository and ``cd cov-support``
2. ``conda env create -f environment.yml``
3. ``conda activate cov-support``
4. ``python setup.py install`` or ``pip install .``

> Note: we recommend using cov-support in the conda environment specified in the ``environment.yml`` file as per the instructions above. If you can't use conda for some reason, dependency details can be found in the ``environment.yml`` file.


### Check the install worked

Type (in the cov-support environment):

```
cov-support
```
and you should see the help for cov-support printed.


### Updating cov-support

To update:

1. ``conda activate cov-support``
2. ``git pull`` \
pulls the latest changes from github
3. ``python setup.py install`` \
re-installs cov-support
4. ``conda env update -f environment.yml`` \
updates the conda environment 



### Update website 

```
cov-support --update-web \
    --website-dir cov-lineages \
    --assignment-dir assignment \
    -d pangoLEARN/pangoLEARN/data \
    --updated-metadata data-dir/metadata.csv \
    --lineage-descriptions pangoLEARN/pangoLEARN/supporting_information/lineage_notes.txt
```


### Make guide tree and alignment

```
cov-support --pangolin-prep \
    -d data_dir \
    --num-taxa 5 
```

### Full usage


```
usage: cov-support [-h] [-o OUTDIR] [-d DATA] [--pangolin-prep]
                   [--num-taxa NUM_TAXA] [--update-web]
                   [--website-dir WEBSITE_DIR]
                   [--assignment-dir ASSIGNMENT_DIR]
                   [--updated-metadata METADATA]
                   [--lineage-descriptions DESCRIPTIONS] [-n] [-t THREADS]
                   [--verbose] [-v]

cov-support: update guide tree or train a new model. Update webpages. Do all
sorts of cov-lineage-support-related tasks

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        Output directory. Default: current working directory
  -d DATA, --data DATA  Data directory minimally containing alignment.fasta,
                        global.tree metadata.csv and lineages.csv
  --pangolin-prep       Run legacy pangolin prep pipeline
  --num-taxa NUM_TAXA   Number of taxa in guide tree
  --update-web          Run website update pipeline
  --website-dir WEBSITE_DIR
                        Path to website repo
  --assignment-dir ASSIGNMENT_DIR
                        Path to assignment repo
  --updated-metadata METADATA
                        Updated metadata file
  --lineage-descriptions DESCRIPTIONS
                        Updated descriptions file
  -n, --dry-run         Go through the motions but don't actually run
  -t THREADS, --threads THREADS
                        Number of threads
  --verbose             Print lots of stuff to screen
  -v, --version         show program's version number and exit
  ```