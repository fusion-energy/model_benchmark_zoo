[![cad to dagmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cad_to_dagmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cad_to_dagmc.yml)

[![cad to openmc](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cad_to_openmc.yml/badge.svg)](https://github.com/fusion-energy/model_benchmark_zoo/actions/workflows/ci_cad_to_openmc.yml)

# A collection of CAD and equivalent Constructive Solid Geometry

Matching geometries in CAD format and Constructive Solid Geometry (CSG) for computational benchmarks. This provides particle transport codes an opportunity to verify particle transport with both geometry types.

This benchmark is unique and invaluable if you want to test that a particle transport code gets the same results in CSG and CAD geometry transport as it provides geometries that:
- cover all standard CSG surface types
    - planes
    - spheres
    - cylinders
    - tori
    - cones
    - general quadratics
- cover contacting and non-contacting geometries (to test imprint and merging)
- cover single and multibody geometries
- models are parametric so can easily be changed for parameter studies

I originally made this repository as there was no other comparison of CSG geometry with DAGMC geometry available and I wanted to verify the level of surface discretisation that was needed to provide accurate results.

The repository then grew into a way to test my DAGMC geometry making package [cad-to-dagmc](https://github.com/fusion-energy/cad_to_dagmc). Later on tests for [cad-to-openmc](https://github.com/openmsr/CAD_to_OpenMC) which is another geometry making package were also added.  



| Model | Description |
|---|---|
| <p align="center"><img src="images/simpletokamak.png" width="100"></p> | Simplified tokamak |
| <p align="center"><img src="images/oktavian.png" width="100"></p> | Oktavian sphere |
| <p align="center"><img src="images/nestedtorus.png" width="100"></p> | Nested tori |
| <p align="center"><img src="images/ellipticaltorus.png" width="100"></p> | Elliptical torus |
| <p align="center"><img src="images/circulartorus.png" width="100"></p> | Circular torus |
| <p align="center"><img src="images/hyperboloid.png" alt="Hyperboloid" width="100"></p> | Hyperboloid |
| <p align="center"><img src="images/paraboloid.png" alt="Paraboloid" width="100"></p> | Paraboloid |
| <p align="center"><img src="images/ellipsoid.png" alt="Ellipsoid" width="100"></p> | Ellipsoid |
| <p align="center"><img src="images/sphere_with_cylindrical_hole.png" width="100"></p> | Sphere with cylindrical hole |
| <p align="center"><img src="images/box_with_spherical_cavity.png" width="100"></p> | Box with spherical cavity |
| <p align="center"><img src="images/nestedsphere.png" width="100"></p> | Nested sphere |
| <p align="center"><img src="images/sphere.png" width="100"></p> | Sphere |
| <p align="center"><img src="images/hemisphere.png" alt="Hemisphere" width="100"></p> | Hemisphere |
| <p align="center"><img src="images/truncated_cone.png" alt="Truncated cone" width="100"></p> | Truncated cone |
| <p align="center"><img src="images/pipe.png" alt="Pipe" width="100"></p> | Pipe |
| <p align="center"><img src="images/nestedcylinder.png" width="100"></p> | Nested cylinders |
| <p align="center"><img src="images/elliptic_cylinder.png" alt="Elliptic cylinder" width="100"></p> | Elliptic cylinder |
| <p align="center"><img src="images/cylinder.png" width="100"></p> | Cylinder |
| <p align="center"><img src="images/three_touching_cuboids.png" width="100"></p> | Three touching cuboids |
| <p align="center"><img src="images/two_touching_cuboids.png" width="100"></p> | Two touching cuboids |
| <p align="center"><img src="images/two_tetrahedrons.png" width="100"></p> | Two tetrahedrons in contact |
| <p align="center"><img src="images/tetrahedral.png" width="100"></p> | Tetrahedron |
| <p align="center"><img src="images/cuboid.png" width="100"></p> | Cuboid |


First clone the repository:

```bash
git clone https://github.com/fusion-energy/model_benchmark_zoo.git
cd model_benchmark_zoo
```

## Install using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install .
```

This uses an [extra index](https://shimwell.github.io/wheels) for pre-built OpenMC wheels.

## Install using Mamba

Requires a Conda/Mamba distribution:

- [Miniforge](https://github.com/conda-forge/miniforge#miniforge-pypy3) (recommended as it includes mamba)
- [Anaconda](https://www.anaconda.com/download)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

```bash
mamba env create -f environment.yml
mamba activate model_benchmark_zoo
pip install .
```

If the environment solve fails, you can try [installing OpenMC from source](https://docs.openmc.org/en/stable/quickinstall.html) instead.

## Usage

Example scripts that make CSG and DAGMC geometry can be found in [the examples folder](https://github.com/fusion-energy/model_benchmark_zoo/tree/main/examples)
