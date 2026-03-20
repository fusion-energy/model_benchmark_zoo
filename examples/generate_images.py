"""Generate PNG preview images for all geometries in the zoo.

Usage:
    python examples/generate_images.py              # generate all
    python examples/generate_images.py Cuboid Sphere # generate specific ones
"""

import sys
import os
import tempfile

import vtk
from cadquery import exporters

from model_benchmark_zoo import (
    Cuboid,
    Sphere,
    NestedSphere,
    Cylinder,
    NestedCylinder,
    TwoTouchingCuboids,
    Circulartorus,
    Nestedtorus,
    Ellipticaltorus,
    SimpleTokamak,
    Oktavian,
    Tetrahedral,
    TwoTetrahedrons,
    SphereWithCylindricalHole,
    BoxWithSphericalCavity,
    ThreeTouchingCuboids,
    Hemisphere,
)

# Each entry: (class, output_filename, camera_kwargs)
# camera_kwargs: position, focal_point, view_up, dolly
GEOMETRIES = {
    "Cuboid": (
        Cuboid,
        "cuboid.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "Sphere": (
        Sphere,
        "sphere.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "NestedSphere": (
        NestedSphere,
        "nestedsphere.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "Cylinder": (
        Cylinder,
        "cylinder.png",
        {"position": (5, 15, 25), "dolly": 0.95},
    ),
    "NestedCylinder": (
        NestedCylinder,
        "nestedcylinder.png",
        {"position": (15, 20, 18), "dolly": 0.95},
    ),
    "TwoTouchingCuboids": (
        TwoTouchingCuboids,
        "two_touching_cuboids.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "Circulartorus": (
        Circulartorus,
        "circulartorus.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "Nestedtorus": (
        Nestedtorus,
        "nestedtorus.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "Ellipticaltorus": (
        Ellipticaltorus,
        "ellipticaltorus.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "SimpleTokamak": (
        SimpleTokamak,
        "simpletokamak.png",
        {"position": (800, 600, 500), "dolly": 0.95},
    ),
    "Oktavian": (
        Oktavian,
        "oktavian.png",
        {"position": (25, 30, 20), "dolly": 0.95},
    ),
    "Tetrahedral": (
        Tetrahedral,
        "tetrahedral.png",
        {"position": (2, 3, 2), "dolly": 0.95},
    ),
    "TwoTetrahedrons": (
        TwoTetrahedrons,
        "two_tetrahedrons.png",
        {"position": (2, 3, 2), "dolly": 0.95},
    ),
    "SphereWithCylindricalHole": (
        SphereWithCylindricalHole,
        "sphere_with_cylindrical_hole.png",
        {"position": (5, 15, 25), "dolly": 0.95},
    ),
    "BoxWithSphericalCavity": (
        BoxWithSphericalCavity,
        "box_with_spherical_cavity.png",
        {"position": (15, 20, 12), "dolly": 0.95},
    ),
    "ThreeTouchingCuboids": (
        ThreeTouchingCuboids,
        "three_touching_cuboids.png",
        {"position": (15, -12, 18), "dolly": 0.95},
    ),
    "Hemisphere": (
        Hemisphere,
        "hemisphere.png",
        {"position": (15, 20, 8), "dolly": 0.95},
    ),
}

# Colors cycled for multi-part assemblies
COLORS = [
    (0.4, 0.6, 0.9),
    (0.9, 0.5, 0.3),
    (0.3, 0.8, 0.4),
    (0.8, 0.3, 0.7),
    (0.9, 0.8, 0.2),
    (0.3, 0.7, 0.8),
]


def get_assembly_shapes(assembly):
    """Extract individual Shape objects from a CadQuery Assembly."""
    shapes = []
    for name, obj in assembly.objects.items():
        if hasattr(obj, "shapes") and obj.shapes:
            for shape in obj.shapes:
                shapes.append(shape)
        elif hasattr(obj, "obj") and obj.obj is not None:
            shapes.append(obj.obj)
    return shapes


def shape_to_actor(shape, color, opacity=0.85):
    """Convert a CadQuery shape to a VTK actor via VTP export."""
    with tempfile.NamedTemporaryFile(suffix=".vtp", delete=False) as f:
        tmpfile = f.name

    try:
        exporters.exportVTP(shape, tmpfile)

        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(tmpfile)
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetOpacity(opacity)
        return actor
    finally:
        os.remove(tmpfile)


def render_png(actors, output_path, camera_kwargs, size=(400, 400)):
    """Render a list of VTK actors to a PNG file."""
    renderer = vtk.vtkRenderer()
    for actor in actors:
        renderer.AddActor(actor)
    renderer.SetBackground(1, 1, 1)

    cam = renderer.GetActiveCamera()
    pos = camera_kwargs.get("position", (15, 20, 12))
    focal = camera_kwargs.get("focal_point", (0, 0, 0))
    up = camera_kwargs.get("view_up", (0, 0, 1))
    dolly = camera_kwargs.get("dolly", 0.95)

    cam.SetPosition(*pos)
    cam.SetFocalPoint(*focal)
    cam.SetViewUp(*up)
    renderer.ResetCamera()
    cam.Dolly(dolly)
    renderer.ResetCameraClippingRange()

    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.SetSize(*size)
    render_window.AddRenderer(renderer)
    render_window.Render()

    window_to_image = vtk.vtkWindowToImageFilter()
    window_to_image.SetInput(render_window)
    window_to_image.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(output_path)
    writer.SetInputConnection(window_to_image.GetOutputPort())
    writer.Write()


def generate_image(name, geometry_cls, filename, camera_kwargs, output_dir):
    """Generate a PNG image for a single geometry."""
    print(f"Generating {name}...", end=" ", flush=True)

    try:
        obj = geometry_cls()
        assembly = obj.cadquery_assembly()
    except Exception as e:
        print(f"FAILED to build geometry: {e}")
        return False

    # Extract shapes from the assembly
    # Assembly children can be Workplane (call .val()), Solid/Compound (use directly), or None (root node, skip)
    shapes = []
    for child in assembly.objects.values():
        if not hasattr(child, "obj") or child.obj is None:
            continue
        obj = child.obj
        if hasattr(obj, "val"):
            # Workplane -> extract the underlying Shape
            shapes.append(obj.val())
        else:
            # Solid, Compound, or other Shape subclass
            shapes.append(obj)

    if not shapes:
        print("FAILED: no shapes extracted from assembly")
        return False

    actors = []
    for i, shape in enumerate(shapes):
        color = COLORS[i % len(COLORS)]
        try:
            actor = shape_to_actor(shape, color)
            actors.append(actor)
        except Exception as e:
            print(f"FAILED to convert shape {i}: {e}")
            return False

    output_path = os.path.join(output_dir, filename)
    try:
        render_png(actors, output_path, camera_kwargs)
    except Exception as e:
        print(f"FAILED to render: {e}")
        return False

    print(f"OK -> {output_path}")
    return True


def main():
    output_dir = os.path.join(os.path.dirname(__file__))

    # If specific names given on CLI, only generate those
    requested = sys.argv[1:]
    if requested:
        entries = {k: v for k, v in GEOMETRIES.items() if k in requested}
        not_found = set(requested) - set(entries.keys())
        if not_found:
            print(f"Unknown geometries: {', '.join(not_found)}")
            print(f"Available: {', '.join(GEOMETRIES.keys())}")
            sys.exit(1)
    else:
        entries = GEOMETRIES

    successes = 0
    failures = 0
    for name, (cls, filename, cam_kwargs) in entries.items():
        ok = generate_image(name, cls, filename, cam_kwargs, output_dir)
        if ok:
            successes += 1
        else:
            failures += 1

    print(f"\nDone: {successes} generated, {failures} failed")


if __name__ == "__main__":
    main()
