# model_benchmark_zoo
A collection of parametric CAD and equivalent Constructive Solid Geometry
models (CSG) for comparing neutronics simulations with both geometry types.


# Usage

```python
from model_benchmark_zoo import Sphere

my_sphere = Sphere(radius=5)

my_sphere.openmc_cell()

my_sphere.export_stp()
```