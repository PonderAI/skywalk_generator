# Skywalk Data Generator

## Building the docker container
docker build --no-cache -t openfoam_skywalk .  

## Running the container
### Comand Prompt
<!-- docker run --gpus all --shm-size 10.24gb -it -p 8888:8888 --rm -v %cd%/cases:/skywalk_generator/cases openfoam_skywalk bash -->
```
docker run --gpus all --shm-size 10.24gb -it -p 8888:8888 --rm -v %cd%:/skywalk_generator openfoam_skywalk bash
```

### PowerShell
```
docker run --gpus all --shm-size 10.24gb -it -p 8888:8888 --rm -v ${pwd}:/skywalk_generator openfoam_skywalk bash
```

### Linux
```
docker run --gpus all --shm-size 10.24gb -it -p 8888:8888 --rm -v $(pwd):/skywalk_generator openfoam_skywalk bash
```

## Testing the data generator on a single case
```
python3 src/1_generate_cases.py  
cd cases/case_0_0  
. $WM_PROJECT_DIR/bin/tools/RunFunctions  
runApplication blockMesh  
runApplication snappyHexMesh -overwrite  
runApplication simpleFoam
```  

## Running the pipline
```
python3 src/1_generate_cases.py
python3 src/2_run_cases.py
xvfb-run -a --server-args='-screen 0 1024x768x24' python3 src/3_postprocess_cfd_data.py


## or ##

bash run.sh
python3 src/1_generate_cases.py
python3 src/2_run_cases.py
python3 src/3_postprocess_cfd_data.py
```

## TODO:
- Add pyproject.toml file and modify the docker file
- Add CLI arguments for testing and number of cases limit to generate_cases.py
- ~~write python/bash file to run the cases with OpenFOAM~~
- write scripts to post process the data