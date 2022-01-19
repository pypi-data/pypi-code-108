#!/usr/bin/env python3
"""
# Created: Thu Jan  6 14:26:05 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import sys

sys.path.append('/Users/jacobfaibussowitsch/NoSync/warp4py')
import warp4py as warp

def main():
  model = warp.Model('Cohesive Dog Bone')

  interface_mat = warp.Material(
    model,'interface_exp','cohesive','exp1_intf',
    killable=True,
    delta_peak=0.000285,
    sig_peak=220,
    beta=1.0,
    compression_multiplier=15
  )
  bulk_mat = warp.Material(
    model,'bulkCarbonDeform',
    'deformation',
    E=108520,
    nu=0.21,
    yld_pt=57,
    n_power=1,
    rho=1.55
  )

  struct = warp.Structure(model,'dogBoneDisplacement')
  struct.input_from('../meshes/warpMeshFiles/cohesive_dogBone_coord',expand=False)
  struct.input_from('../meshes/warpMeshFiles/cohesive_dogBone_elem',expand=False)

  cstrnt = warp.Constraint(struct)
  cstrnt.append('plane',x=0,u=0,v=0,w=0)

  load = warp.StepLoad(struct,'xyzPull')
  load.append(75,constraints=1.0)
  load.append(150,constraints=0.8)

  nodelist = warp.GeometricList(struct,'pullX',x=59.5,tolerance=0.05)

  soln_params = warp.SolutionParameters(
    model,
    time_step=0.05,
    maximum_iterations=50,
    convergence_test_norm_res_tol=0.005,
    adaptive_solution=True,
    divergence_check=True,
    line_search=True
  )

  crack_params = warp.CrackGrowthParameters(
    model,
    critical_effective_cohesive_displacement_multiplier=1.1,
    force_release_type='steps',
    release_steps=5,
  )

  model.output()

  if 0:


    for cur,nextit in model.timesteps(stepsize=2):
      struct.compute(cur,nextit,load)
      struct.output('element','displacements','stresses','strains')

    model.output()
  model.view()
  return

if __name__ == '__main__':
  main()
