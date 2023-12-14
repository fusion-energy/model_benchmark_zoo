https://github.com/fusion-energy/paramak/blob/main/src/paramak/parametric_reactors/flf_system_code_reactor.py


# surfaces
    inner_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius)
    outer_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness)

    inner_vessel_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness + blanket_vv_gap)
    outer_vessel_cylinder = openmc.ZCylinder(
        r=inner_blanket_radius + blanket_thickness + blanket_vv_gap + vv_thickness,
        boundary_type="vacuum",
    )

    upper_vessel_bottom = openmc.ZPlane(z0=blanket_height + lower_vv_thickness + lower_blanket_thickness)
    upper_vessel_top = openmc.ZPlane(z0=blanket_height + lower_vv_thickness + lower_blanket_thickness + upper_vv_thickness)

    lower_blanket_top = openmc.ZPlane(z0=lower_vv_thickness + lower_blanket_thickness)
    lower_blanket_bottom = openmc.ZPlane(z0=lower_vv_thickness)

    upper_blanket_bottom = upper_vessel_top
    upper_blanket_top = openmc.ZPlane(
        z0=blanket_height + lower_vv_thickness + lower_blanket_thickness + upper_vv_thickness + upper_blanket_thickness,
        boundary_type="vacuum",
    )

    lower_vessel_top = lower_blanket_bottom
    lower_vessel_bottom = openmc.ZPlane(
        z0=0,
        boundary_type="vacuum",
    )

    # regions
    inner_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_blanket_cylinder
    blanket_region = -upper_vessel_bottom & +lower_blanket_top & +inner_blanket_cylinder & -outer_blanket_cylinder

    blanket_upper_region = -inner_vessel_cylinder & -upper_blanket_top & +upper_blanket_bottom
    blanket_lower_region = -inner_vessel_cylinder & -lower_blanket_top & +lower_blanket_bottom

    outer_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_vessel_cylinder & +outer_blanket_cylinder

    vessel_region = -upper_blanket_top & +lower_vessel_bottom & -outer_vessel_cylinder & +inner_vessel_cylinder
    vessel_upper_region = -upper_vessel_top & +upper_vessel_bottom & -inner_vessel_cylinder
    vessel_lower_region = -lower_vessel_top & +lower_vessel_bottom & -inner_vessel_cylinder

    # cells
    vessel_cell_lower = openmc.Cell(region=vessel_lower_region)
    vessel_cell_upper = openmc.Cell(region=vessel_upper_region)
    vessel_cell_cylinder = openmc.Cell(region=vessel_region)
    vessel_cell_lower.fill = mat_vessel
    vessel_cell_upper.fill = mat_vessel
    vessel_cell_cylinder.fill = mat_vessel

    blanket_cell_cylinder = openmc.Cell(region=blanket_region)
    blanket_cell_upper = openmc.Cell(region=blanket_upper_region)
    blanket_cell_lower = openmc.Cell(region=blanket_lower_region)
    blanket_cell_cylinder.fill = mat_blanket
    blanket_cell_upper.fill = mat_blanket
    blanket_cell_lower.fill = mat_blanket

    void_cell1 = openmc.Cell(region=inner_void_region)
    void_cell2 = openmc.Cell(region=outer_void_region)