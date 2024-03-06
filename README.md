# Skywalk Data Generator

## Building the docker container
docker build --no-cache -t openfoam_skywalk .  

## Running the container
### Comand Prompt
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

## Debugging
```
docker run --gpus all --shm-size 10.24gb -it -p 8888:8888 -p 5678:5678 --rm -v $(pwd):/skywalk_generator openfoam_skywalk bash


# Add this to the top of the Python file:
import debugpy
debugpy.listen(("0.0.0.0", 5678))
```

## Running the pipline
```
bash run.sh
python3 src/1_generate_cases.py [SAMPLES: optional int > 0. default=None]
python3 src/2_run_cases.py
python3 src/3_postprocess_cfd_data.py
```

## TODO:
- Add pyproject.toml file and modify the docker file
- ~~Add CLI arguments for testing and number of cases limit to generate_cases.py~~
- ~~Perhaps the image could be conditioned with a single number representing the elevation of the skywalk?~~
- ~~How to save top down snapshot of geometry? Distance from plane at z=100m to the ground/bottom of skywalk~~
- ~~Write python/bash file to run the cases with OpenFOAM~~
- ~~Write scripts to post process the data~~