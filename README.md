
A collection of parametric CAD and equivalent Constructive Solid Geometry
models (CSG) for comparing neutronics simulations with both geometry types.

| Model | Testing Status |
|---|---|
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374951-5e711a8b-a3db-4476-8f56-03a620d74b93.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cuboid.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cuboid.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374950-ef8696dd-adbc-4fd8-bd44-c5304e1d0709.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_sphere.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_sphere.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374954-20dee8fb-5199-4fc2-86a7-00452b6bdc89.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_sphericalshell.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_sphericalshell.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374945-aea2582b-1d5f-40b1-a77b-bef79dce50da.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_two_touching_cuboids.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_two_touching_cuboids.yml) |



# Installation prerequisite

In principle, any Conda/Mamba distribution will work. A few Conda/Mamba options are:
- [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge)
- [Miniforge](https://github.com/conda-forge/miniforge#miniforge-pypy3)
- [Anaconda](https://www.anaconda.com/download)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)


# Install using Mamba and pip

This example assumes you have installed the MambaForge option or separately
installed Mamba with ```conda install -c conda-forge mamba -y```

Create a new conda environment, I've chosen Python 3.9 here but new versions are
also supported.
```bash
mamba create --name new_env python=3.9 -y
```

Activate the environment
```bash
mamba activate new_env
```

Install the dependencies
```bash
mamba install -y -c cadquery -c conda-forge moab gmsh python-gmsh cadquery=master openmc
```

Then you can install the cad_to_dagmc package with ```pip```
```bash
pip install cad_to_dagmc
```

Then you can install the model benchmark zoo with ```pip```
```bash
pip install git+git://github.com/fusion-energy/model_benchmark_zoo.git
```

# Usage

Example scripts that make CSG and DAGMC geometry can be found in [the examples folder](https://github.com/fusion-energy/model_benchmark_zoo/tree/main/examples)
