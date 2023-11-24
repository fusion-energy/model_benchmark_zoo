
A collection of parametric CAD and equivalent Constructive Solid Geometry
models (CSG) for comparing neutronics simulations with both geometry types.

| Model | Testing Status |
|---|---|
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374951-5e711a8b-a3db-4476-8f56-03a620d74b93.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cuboid.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cuboid.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374950-ef8696dd-adbc-4fd8-bd44-c5304e1d0709.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_sphere.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_sphere.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374954-20dee8fb-5199-4fc2-86a7-00452b6bdc89.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_nestedsphere.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_nestedsphere.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374945-aea2582b-1d5f-40b1-a77b-bef79dce50da.png" width="100"></p>  |     [![Cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_two_touching_cuboids.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_two_touching_cuboids.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/284880533-c18e3345-52ec-4253-baa8-e1dbe2a52944.png" width="100"></p>  |     [![Cylinder](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cylinder.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cylinder.yml) |
|         <p align="center"><img src="https://private-user-images.githubusercontent.com/8583900/285550797-7154e687-27d2-41a9-a3fc-083d8535899c.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTEiLCJleHAiOjE3MDA4NjU1NDYsIm5iZiI6MTcwMDg2NTI0NiwicGF0aCI6Ii84NTgzOTAwLzI4NTU1MDc5Ny03MTU0ZTY4Ny0yN2QyLTQxYTktYTNmYy0wODNkODUzNTg5OWMucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQUlXTkpZQVg0Q1NWRUg1M0ElMkYyMDIzMTEyNCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyMzExMjRUMjIzNDA2WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZTY2MTIyZTdlOTFjY2JkMTA3NGM5OWJjNjc4YjZjMzVjZGRhMzVmNGFkYWU0Y2ZmZTU1MjZiOGYxMzA5OWRiYiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmYWN0b3JfaWQ9MCZrZXlfaWQ9MCZyZXBvX2lkPTAifQ.dL3a0rc7zCxTOc-fHuiBqsJ8kQDO1u641drCKgVG70U" width="100"></p>  |     [![Cylinder](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cylinder.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_nestedcylinder.yml) |

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
