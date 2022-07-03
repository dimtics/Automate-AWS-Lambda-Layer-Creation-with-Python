import argparse
import subprocess


def getParser():

    # create the parser
    parser = argparse.ArgumentParser(
        prog="createLambdaLayerPackage",
        description="Create a Lambda layer package",
        allow_abbrev=False,
    )

    # add arguments
    parser.add_argument(
        "--layer-package-name",
        required=True,
        type=str,
        help="Name of the package zip file",
    )

    parser.add_argument(
        "--runtime-version",
        required=True,
        type=str,
        help="Python version to use for the Lambda layer e.g. 3.7",
    )

    parser.add_argument(
        "--layer-library",
        nargs=argparse.REMAINDER,
        required=True,
        type=str,
        help="Python libraries to be included in the Lambda layer package. Separate multiple libraries with spaces.",
    )

    # parse the arguments
    args = parser.parse_args()
    return args


def createLambdaLayerPackage(myArgs: argparse.Namespace) -> None:
    """ A function to create an AWS Lambda layer package
    Args:
        --runtime-version (str): Python version to use for the Lambda layer e.g. 3.7
        --layer-library" (str): Python libraries to be included in the Lambda layer package.
        --layer-package-name (str): Name of the package zip file.

    Returns:
        A zip layer package/file under projectLambdaLayer directory.

    Usage: createLambdaLayerPackage.py --layer-package-name pandas-pyarrow-layer --runtime-version 3.9 --layer-library pandas pyarrow    
    """

    try:
        # get a dict of arguments and values
        mydict = vars(myArgs)

        # extract values from arguments
        modList = mydict["layer_library"]
        runtimeVal = mydict["runtime_version"]
        packageVal = mydict["layer_package_name"]

        # combine layer-library arg values into a string
        modStr = " ".join(modList)

        shellCmd = f"""
            pyLayerEnv="envLayer"
            projectDir="projectLambdaLayer"
            pythonVersion={runtimeVal}
            packageName={packageVal}

            # get your base conda environment name
            condaBase=$(conda info | grep "base environment" | awk '{{ print "$4" }}' | awk -F"/" '{{ print "$NF" }}')

            # create a new conda environment with python version desired
            conda create --name $pyLayerEnv python=$pythonVersion --yes

            # configure conda to avoid CommandNotFoundError 
            source ~/$condaBase/etc/profile.d/conda.sh

            # activate the conda environment
            conda activate $pyLayerEnv

            # create a project directory
            mkdir $projectDir

            # get into the project directory
            cd $projectDir

            # create a path for libraries to be added to the layer
            mkdir -p build/python/lib/python$pythonVersion/site-packages

            # create an array to store libraries
            declare -a libArr

            # Add libraries to array
            libArr+=({modStr})

            # install libraries in the array to the defined path
            for item in "${{libArr[@]}}"
                do 
                    pip install "$item" -t build/python/lib/python$pythonVersion/site-packages
                done    

            # consider removing unnecessary files and folders such as __pycache__, LICENSES, etc. to reduce package size
            find build/python/lib/python$pythonVersion/site-packages -type d -name "__pycache__" -exec rm -rf {{}} \;
            find build/python/lib/python$pythonVersion/site-packages -type f -name "*LICENSE*" -exec rm -rf {{}} \;

            # get into the build directory
            cd build

            # zip the installed libraries within the build folder and name the zip file
            zip -r $packageName python

            # deactivate the conda environment
            conda deactivate

            # remove the conda environment
            conda remove --name $pyLayerEnv --all --yes

            # move the zip layer package under the project directory
            mv $packageName.zip ../

            # step out of build folder
            cd ..

            # remove the build folder
            rm -rf build

            """

        # run the shell script
        result = subprocess.run(
            ["/bin/bash"],
            input=shellCmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )

        if result.returncode != 0:
            print(result.stderr)
            raise Exception("Error creating Lambda layer package")
        else:
            print("Lambda layer package created successfully")

    except Exception as err:
        print(err)


def main():
    # get the required arguments
    modArgs = getParser()
    # create the lambda layer
    createLambdaLayerPackage(modArgs)


if __name__ == "__main__":
    main()
