#!/bin/bash

#SBATCH -n 36 # Number of nodes
#SBATCH -N 1 # All nodes on 1 machine
#SBATCH -p cpu36 # Name of partition to submit to
#SBATCH -o output_%j.out
#SBATCH -e errors_%j.err

# Load OpenFOAM
FOAM_INST_DIR=/opt/OpenFOAM  
source $FOAM_INST_DIR/.OF2012.bashrc

echo `hostname`

#cd $1
./Allrun
./Allpost
#cd ..
