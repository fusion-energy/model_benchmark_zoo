
A collection of parametric CAD and equivalent Constructive Solid Geometry
models (CSG) for comparing neutronics simulations with both geometry types.

| Model | Testing Status |
|---|---|
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374951-5e711a8b-a3db-4476-8f56-03a620d74b93.png" width="100"></p>  |     [![cuboid](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cuboid_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cuboid_cad_to_dagmc.yml) <br> [![cuboid - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cuboid_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cuboid_cad_to_openmc.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374950-ef8696dd-adbc-4fd8-bd44-c5304e1d0709.png" width="100"></p>  |     [![sphere](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/sphere_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/sphere_cad_to_dagmc.yml) <br> [![sphere - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/sphere_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/sphere_cad_to_openmc.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374954-20dee8fb-5199-4fc2-86a7-00452b6bdc89.png" width="100"></p>  |     [![nested_sphere](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_sphere_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_sphere_cad_to_dagmc.yml) <br> [![nested sphere - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_sphere_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_sphere_cad_to_openmc.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/262374945-aea2582b-1d5f-40b1-a77b-bef79dce50da.png" width="100"></p>  |     [![two_touching_cuboids](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/two_touching_cuboids_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/two_touching_cuboids_cad_to_dagmc.yml) <br> [![two touching cuboids - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/two_touching_cuboids_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/two_touching_cuboids_cad_to_openmc.yml) |
|         <p align="center"><img src="https://user-images.githubusercontent.com/8583900/284880533-c18e3345-52ec-4253-baa8-e1dbe2a52944.png" width="100"></p>  |     [![cylinder](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cylinder_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cylinder_cad_to_dagmc.yml) <br> [![cylinder - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cylinder_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/cylinder_cad_to_openmc.yml)|
|         <p align="center"><img src="https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/examples/nestedcylinder.png" width="100"></p>  |     [![nested_cylinder](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_cylinder_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_cylinder_cad_to_dagmc.yml) <br> [![nested cylinder - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_cylinder_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/nested_cylinder_cad_to_openmc.yml) |
|         <p align="center"><img src="https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/examples/circulartorus.png" width="100"></p>  |     [![circular_torus](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/circular_torus_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/circular_torus_cad_to_dagmc.yml) <br> [![circular torus - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/circular_torus_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/circular_torus_cad_to_openmc.yml) |
|         <p align="center"><img src="https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/examples/ellipticaltorus.png" width="100"></p>  |     [![elliptical_torus](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/elliptical_torus_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/elliptical_torus_cad_to_dagmc.yml) <br> [![elliptical torus - cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/elliptical_torus_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/elliptical_torus_cad_to_openmc.yml) |

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

Install the dependencies, if this fails to solve the environment you could also try [installing OpenMC from source](https://docs.openmc.org/en/stable/quickinstall.html) which might be prefered.

```bash
mamba install -y -c conda-forge moab gmsh python-gmsh "openmc=0.14.0=dagmc*nompi*"
```

CadQuery should then be installed, here is the mamba command and the pip command. If the mamba command fails to solve the environment then try the pip command as this points to a specific version (before OCP 7.7.2 was made the default).
```bash
mamba install -y -c cadquery cadquery=master
pip install git+https://github.com/CadQuery/cadquery.git@79e64e557e87d63b84c1c8a60c0df8e941a1a4a1
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
