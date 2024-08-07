#!/bin/bash

#### Description: This script creates an AWS Lambda layer package.
#### Author: Dimeji Salau
#### Arguments:
####    pythonVersion: string => Python runtime version e.g "3.12"
####    layerModule: string => Python library to be included in the Lambda layer package.
####                  Separate multiple libraries with spaces e.g. "polars pyarrow" within a single string construct
####    packageName: string => A name for the final zip layer package.
####
#### Usage: ./createLambdaLayerPackage.sh "polars-pyarrow-layer" "3.12" "polars pyarrow s3fs"


# Parameters
pyLayerEnv="proj_env"
packageName=$1
pythonVersion=$2
layerModule=$3
projectDir="lambdaLayerDir"

# get your base conda environment name
condaBase=$(conda info | grep "base environment" | awk '{print $4}' | awk -F"/" '{print $NF}')

# create a new conda environment with a desired python version
conda create --name $pyLayerEnv python=$pythonVersion --yes

# configure conda to avoid CommandNotFoundError
source ~/$condaBase/etc/profile.d/conda.sh

# activate the conda environment
conda activate $pyLayerEnv

# create a project directory and navigate into the folder
mkdir $projectDir && cd $projectDir

# create a path for libraries to be included in the layer
mkdir -p build/python/lib/python$pythonVersion/site-packages

# install desired libraries.
pip install --platform manylinux2014_x86_64 $layerModule -t build/python/lib/python$pythonVersion/site-packages

# consider removing unnecessary files and folders such as __pycache__, LICENSES, etc. to reduce package size
find build/python/lib/python$pythonVersion/site-packages -type d -name "__pycache__" -exec rm -rf {} \;
find build/python/lib/python$pythonVersion/site-packages -type f -name "*LICENSE*" -exec rm -rf {} \;

# change to build directory and zip the installed libraries
cd build && zip -r $packageName python

# deactivate and remove the conda environment
conda deactivate && conda remove --name $pyLayerEnv --all --yes

# move the zip layer package under the project directory
mv $packageName.zip ../

# step out of build folder
cd ..

# remove the build folder
rm -rf build
