from faserutil.Draw import *
from faserutil.disp.disp import *
from tm import tm
import FASER as fsr
import glob
import numpy as np
import math
from SP import MakeSP
from SP import LoadSP
import scipy as sci
from scipy import interpolate
import json

import sys
import copy
from os.path import dirname, basename, isfile

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]


class Assembler:

    @classmethod
    def loadAssembler(cls, fname, file_directory = "../RobotDefinitions/", baseloc = None):
        total_name = file_directory + fname
        print(total_name)
        with open(total_name, "r") as sp_file:
            sp_data = json.load(sp_file)
        num = sp_data["num_sps"]
        relative_rotation = sp_data["RelativeRotation"]
        constituent_sp = sp_data["ConstituentSP"]
        print("Loading: " + constituent_sp)
        temp_assembler = cls(4)
        sp_list = []
        alternate_rotation = 1
        for i in range(num):
            if i == 0:
                temp_sp = LoadSP(constituent_sp, file_directory = file_directory, baseloc = baseloc, alternate_rotation = alternate_rotation)
            else:
                temp_sp = LoadSP(constituent_sp, file_directory = file_directory, baseloc = temp_sp.getTopT(), alternate_rotation = alternate_rotation)
                if relative_rotation > 0:
                    temp_sp.SpinCustom((relative_rotation * i))
            sp_list.append(temp_sp)
            if relative_rotation == -1:
                alternate_rotation = alternate_rotation * -1
        temp_assembler.nominal_plate_transform = temp_sp.nominal_plate_transform.copy()

        for i in range(num -1):
            sp_list[i].bound_top = sp_list[i+1]
        for i in range(num):
            if i == 0:
                continue
            sp_list[i].bound_bottom = sp_list[i-1]

        temp_assembler.num_sps = num
        temp_assembler.sp_list = sp_list
        temp_assembler.sp_radius = sp_list[0].outer_bottom_radius
        temp_assembler.current_top_pos = temp_assembler.sp_list[temp_assembler.num_sps-1].getTopT()
        return temp_assembler


    def __init__(self, num, radius = .15, spacing = 8, nominal_height = 1, use_alternating_radius = 0, plateThickness = 0, lset = None, name = "ASM1", alternate_rotation = 0):
        self.sp_list = None
        self.current_top_pos = None
        self.name = name
        self.comm = None
        self.link_state = 0

        #Error Info
        self.validation_error = ""

        self.num_sps = num #How many platforms make up assembler? If you don't want bugs at the moment, choose 4.
        sp_list = [None] * num #Create empty list to hold stewart platform objects
        self.current_base_pos = tm() #Origin Transform
        self.sp_radius = radius #What's the radius?
        self.joint_cluster_spacing = spacing
        self.sp_top_plate_offset = nominal_height
        self.debug = 0

        #Create helper matrices for platform neutral pose offset and inversion
        self.nominal_plate_transform = tm(np.array([0.0, 0.0, nominal_height, 0.0, 0.0, 0.0]))
        self.plate_inverter = tm(np.array([0.0, 0.0, 0.0, 0.0, np.pi, 0.0]))

        #Create platform. The t indicator flip flops a 60 degree offset in the stewart platforms to make sure that the ball joints are aligned
        t = -1
        alternate_rotation_incrementer = alternate_rotation
        if use_alternating_radius == 0:
            radius_a = radius
            radius_b = radius
        else:
            radius_a = radius
            radius_b = use_alternating_radius
        #Declare a number of SPs and bind them to each other
        for i in range(num):
            if i == 0:
                temp_sp, bottom, top = MakeSP(radius_a, radius_b, spacing, self.current_base_pos.copy(), nominal_height, plateThickness = plateThickness, lset = lset, alternate_rotation = alternate_rotation_incrementer)
            else:
                temp_sp, bottom, top = MakeSP(radius_a, radius_b, spacing, sp_list[i-1].getTopT(), nominal_height, t, plateThickness = plateThickness, lset = lset, alternate_rotation = alternate_rotation_incrementer)
            #Alternate plate rotations so that joint clusters are attached
            if alternate_rotation == 0:
                t = t * -1 #Flip the 60 degree marker
            else:
                alternate_rotation_incrementer+=alternate_rotation
            if use_alternating_radius != 0:
                radius_temp = radius_a
                radius_a = radius_b
                radius_b = radius_temp
            sp_list[i] = (copy.deepcopy(temp_sp)) #I had some issues previously with SPs updating each others values, so I've tried very hard to make sure none are shared
            sp_list[i].nominal_height = nominal_height
        self.last_leg_lengths = np.zeros(((num * 3), 1))
        #Bind platforms to each other
        for i in range(num -1):
            sp_list[i].bound_top = sp_list[i+1]
        for i in range(num):
            if i == 0:
                continue
            sp_list[i].bound_bottom = sp_list[i-1]

        self.sp_list = sp_list
        self.current_top_pos = self.sp_list[self.num_sps-1].getTopT()

    """
       _  ___                            _   _
      | |/ (_)                          | | (_)
      | ' / _ _ __   ___ _ __ ___   __ _| |_ _  ___ ___
      |  < | | '_ \ / _ \ '_ ` _ \ / _` | __| |/ __/ __|
      | . \| | | | |  __/ | | | | | (_| | |_| | (__\__ \
      |_|\_\_|_| |_|\___|_| |_| |_|\__,_|\__|_|\___|___/
    """


    def FK(self, arr, protect = False):
        """
        Given a matrix of size (6, n), calculate the end effector location of the assembler stack via cumulative SP forward kinematics
        Tosses an error if your matrix size is screwed up. Uses Newton Raphson method by default. Can be changed via the setFKMode(mode) method
        """
        #Check dimensionality
        #(Must contain the correct number of vectors for the number of platforms)
        t_size = arr.shape
        if t_size[1] != self.num_sps:
            #If dimensionality is bad, so are you for calling this function with not enough values.
            print("Bad Dimensions")
            return -1
        top_transform = self.sp_list[0].getTopT()
        #Perform FK on each stewart platform, in order from 0 to N, with the bottom plate of the ith platform set to the i-1th top plate
        for i in range(self.num_sps):
            if i == 0:
                top_transform = self.sp_list[0].FK(arr[0:6,i].reshape((6,1)), protect = protect)
            else:
                #self.sp_list[i].move(tm())
                #self.sp_list[i].IK(self.sp_list[i].getBottomT(), self.sp_list[i].getBottomT() @ self.nominal_plate_transform)
                self.sp_list[i].FK(arr[0:6,i].reshape((6,1)), self.sp_list[i-1].getTopT(), protect = protect)
                #DrawSP(self.sp_list[i], ax, 'red')
                self.sp_list[i].move(self.sp_list[i-1].getTopT())
                top_transform = self.sp_list[i].getTopT()
        self.current_top_pos = top_transform
        #Return the top plate of the stack and set the stored position for the top plate.
        return top_transform


    def IK(self, coords, ax = 0):
        """
        Wrapper for IK.
        """
        return self.SplineIK(coords)


    def IKC(self, goal_list, protect = False):
        """
        #Perform IK on each platform individually with a list of coordinates, one for each platform.
        #Note that this isn't necessarily validated, and there can be errors in applying this function, because of relative positioning
        Takes a goal tmas a Target
        """
        #Perform IK on each platform individually with a list of coordinates, one for each platform.
        #Note that this isn't necessarily validated, and there can be errors in applying this function, because of relative positioning
        for i in range(self.num_sps):
            if i == 0:
                #disp(self.getBottomT(), "Assigned Bottom")
                #disp(goal_list[i], "Assigned Top")
                self.sp_list[i].IK(bottom_plate_pos = self.getBottomT(), top_plate_pos = goal_list[i], protect = protect)
            else:
                #disp(self.sp_list[i-1].getTopT(), "Assigned Bottom")
                #disp(goal_list[i], "Assigned Top")
                self.sp_list[i].IK(bottom_plate_pos = self.sp_list[i-1].getTopT(), top_plate_pos = goal_list[i], protect = protect)
        return self.sp_list[self.num_sps-1].getTopT()


    def IKR(self, goal_list, protect = True):
        """
        Perform IK Individually on each platform in the local frame.
        """
        for i in range(len(goal_list)):
            if i == 0:
                t_b = self.sp_list[i].getBottomT()
                self.sp_list[i].move(tm())
                self.sp_list[i].IK(top_plate_pos=goal_list[i], protect = protect)
                self.sp_list[i].move(t_b)
            else:
                self.sp_list[i].move(tm())
                self.sp_list[i].IK(top_plate_pos=goal_list[i], protect = protect)
                self.sp_list[i].move(self.sp_list[i-1].getTopT())
        if (len(goal_list) < self.num_sps):
            for i in range(len(goal_list), self.num_sps):
                self.sp_list[i].move(self.sp_list[i-1].getTopT(), True)
        return self.sp_list[self.num_sps-1].getTopT()


    def TransPS(self, trans):
        """
        Apply a given local transformation to each platform in the assemblers stack. Useful in niche situations.
        """
        for i in range(self.num_sps):
            if i == 0:
                self.sp_list[i].IK(self.sp_list[i].getBottomT(), trans)
            else:
                self.sp_list[i].IK(self.sp_list[i-1].getTopT(), self.sp_list[i-1].getTopT() @ trans)
        self.current_top_pos = self.sp_list[-1].getTopT()
        return self.sp_list[i].getTopT()

    def SplinedPath(self, target_pose_list, num_steps):
        nodes = []
        for i in range(len(target_pose_list)):
            nodes.append(target_pose_list[i].TAA.reshape((6)))
        nodes = np.array(nodes)
        x = nodes[:,0]
        y = nodes[:,1]
        z = nodes[:,2]
        xr = nodes[:,3]
        yr = nodes[:,4]
        zr = nodes[:,5]
        tck, u = interpolate.splprep( [x,y,z,xr,yr,zr] ,s = 0 )
        ls =  np.linspace( 0, 1, num_steps)
        x_new,y_new,z_new,xr_new,yr_new,zr_new = interpolate.splev(ls, tck,der = 0)
        plate_poses_list = []
        temporary_poses_list = []
        for i in range(num_steps):
            tpos = tm([x_new[i],y_new[i],z_new[i],xr_new[i],yr_new[i],zr_new[i]])
            self.SplineIK(tpos)
            plate_poses_list.append(self.gPlates())
            temporary_poses_list.append(tpos)
        temporary_poses_list[len(temporary_poses_list) - 1] = target_pose_list[len(target_pose_list) - 1]
        return plate_poses_list, temporary_poses_list

    def LegDeltaToGoal(self, goal, num_steps):
        old_top_pose = self.getTopT()
        self.SplineIK(goal)
        goal_leg_lengths = self.gLens().copy()
        self.SplineIK(old_top_pose)
        leg_lengths = self.gLens().copy()

        delta = (goal_leg_lengths - leg_lengths)/num_steps
        leg_lengths_list = []
        for i in range(num_steps):
            leg_lengths = leg_lengths + delta
            leg_lengths_list.append(leg_lengths)
        return leg_lengths_list

    def LegDeltaPath(self, target_pose_list, num_steps):
        top_pose_1 = self.getTopT()
        top_pose_2 = target_pose_list
        leg_lengths, _ = self.SplineIK(top_pose_1)
        poses = [self.gPlates()]
        leg_list_2, _ = self.SplineIK(top_pose_2)

        delta = (leg_list_2 - leg_lengths)/num_steps


        for i in range(num_steps):
            leg_lengths = leg_lengths + delta
            self.FK(leg_lengths)
            poses.append(self.gPlates())
        self.SplineIK(top_pose_1)
        return poses


    def SplineIK(self, target, ax = 0, protect = False):
        pos_target_b = target @ (-1 * (self.nominal_plate_transform/3 * 2))
        pos_target_a = self.current_base_pos @ (self.nominal_plate_transform/3 * 2)
        nodes = np.array([self.current_base_pos[0:3].reshape((3)), pos_target_a[0:3].reshape((3)), pos_target_b[0:3].reshape((3)), target[0:3].reshape((3))])
        x = nodes[:,0]
        y = nodes[:,1]
        z = nodes[:,2]

        tck,u     = interpolate.splprep( [x,y,z] ,s = 0 )
        ls =  np.linspace( 0, 1, self.num_sps + 1)
        x_new,y_new,z_new = interpolate.splev(ls, tck,der = 0)

        rotations_list = []
        for i in range((self.num_sps)//2):
            if i == 0:
                pos = tm([x_new[self.num_sps//2], y_new[self.num_sps//2], z_new[self.num_sps//2], 0, 0, 0])
                rot = fsr.RotFromVec(self.getBottomT(), target)
                #rot = fsr.lookat(self.getBottomT(), target)
                for j in range((3)):
                    if j % np.pi < .0001:
                        rot[j] += .001
                pos[3:6] = rot[3:6]# + .0001
                rotations_list.append(pos)
                #rotations_list.append(fsr.TMMidPoint(self.current_base_pos, target))
            else:
                #rotations_list.insert(0, fsr.RotFromVec(self.current_base_pos, rotations_list[0]))
                #rotations_list.append(fsr.RotFromVec(rotations_list[-1], target))
                #disp([self.getBottomT(), rotations_list[0]], "Bases")
                #disp(fsr.TMMidPoint(self.getBottomT(), rotations_list[0]))
                rotations_list.insert(0, fsr.TMMidPoint(self.getBottomT(), rotations_list[0]))
                rotations_list.append(fsr.TMMidPoint(rotations_list[len(rotations_list)-1], target))
        if len(rotations_list) == 1:
            rotations_list.insert(0, fsr.TMMidPoint(self.getBottomT(), rotations_list[0]))
            rotations_list[1] = fsr.TMMidPoint(rotations_list[1], target)
            #disp(rotations_list, "Rots")

        targets_list = []
        for i in range(self.num_sps):
            #disp(tm([x_new[i], y_new[i], z_new[i], 0, 0, 0]))
            if i == self.num_sps - 1:
                new_target = target
                self.sp_list[i].IK(bottom_plate_pos = self.sp_list[i-1].getTopT(), top_plate_pos = new_target, protect = protect)
            elif i == self.num_sps - 2:
                #new_target = fsr.RotFromVec(tm([x_new[i+1], y_new[i+1], z_new[i+1], 0, 0, 0]), target)
                new_target = tm([x_new[i+1], y_new[i+1], z_new[i+1], 0, 0, 0])
                new_target[3:6] = rotations_list[i][3:6]
                self.sp_list[i].IK(bottom_plate_pos = self.sp_list[i-1].getTopT(), top_plate_pos = new_target, protect = protect)

            elif i != 0:
                #new_target = fsr.RotFromVec(tm([x_new[i+1], y_new[i+1], z_new[i+1], 0, 0, 0]) ,tm([x_new[i+2], y_new[i+2], z_new[i+2], 0, 0, 0]))
                new_target = tm([x_new[i+1], y_new[i+1], z_new[i+1], 0, 0, 0])
                new_target[3:6] = rotations_list[i][3:6]
                self.sp_list[i].IK(bottom_plate_pos = self.sp_list[i-1].getTopT(), top_plate_pos = new_target, protect = protect)
            else:
                new_target = tm([x_new[i+1], y_new[i+1], z_new[i+1], 0, 0, 0])
                new_target[3:6] = rotations_list[i][3:6]
                #new_target = fsr.RotFromVec(tm([x_new[i+1], y_new[i+1], z_new[i+1], 0, 0, 0]), tm([x_new[i+2], y_new[i+2], z_new[i+2], 0, 0, 0]))
                self.sp_list[i].IK(top_plate_pos = new_target, protect = protect)
            targets_list.append(new_target)
            if i > 0:
                self.sp_list[i].move(self.sp_list[i-1].getTopT(), protect = True)
        if ax != 0:
            print("Called")
            ax.plot3D( x,y,z,'o')
            ax.plot3D(x_new,y_new,z_new)
        if not self.comprehensiveValidation():
            #return self.IK(target, ax)
            return self.gLens(), False

        return self.gLens(), True




    """
        _  ___                            _   _            _    _      _
       | |/ (_)                          | | (_)          | |  | |    | |
       | ' / _ _ __   ___ _ __ ___   __ _| |_ _  ___ ___  | |__| | ___| |_ __   ___ _ __ ___
       |  < | | '_ \ / _ \ '_ ` _ \ / _` | __| |/ __/ __| |  __  |/ _ \ | '_ \ / _ \ '__/ __|
       | . \| | | | |  __/ | | | | | (_| | |_| | (__\__ \ | |  | |  __/ | |_) |  __/ |  \__ \
       |_|\_\_|_| |_|\___|_| |_| |_|\__,_|\__|_|\___|___/ |_|  |_|\___|_| .__/ \___|_|  |___/
                                                                        | |
                                                                        |_|
    """

    def _PlSlvLmbd(self, plateRotVec, plate_list):
        leg_lengths = np.zeros((6,self.num_sps))
        for i in range(self.num_sps -2):
            pos = plate_list[i]
            if i == 0:
                pos[3:6] = plateRotVec[3*i:3*i+3]
                leg_lengths[:,i] = self.sp_list[i].IK(top_plate_pos=pos, protect = True).reshape((6))
            else:
                pos[3:6] = plateRotVec[3*i:3*i+3]
                leg_lengths[:,i] = self.sp_list[i].IK(bottom_plate_pos = self.sp_list[i-1].getTopT(), top_plate_pos=pos, protect = True).reshape((6))
        leg_lengths[:,self.num_sps-1] = self.sp_list[-1].IK(bottom_plate_pos = self.sp_list[-2].getTopT(), top_plate_pos = plate_list[-1]).reshape((6))
        if self.comprehensiveValidation():
            print("RANDOM SUCCESS")
        return np.std(leg_lengths.reshape((24)))

    def BadPoseGenerator(self, goal, iters, wrench = []):
        self.SplineIK(goal)
        fmax_overall = 0
        perturb_key = [.15, .15, .15, np.pi/8, np.pi/8, np.pi/8]
        best_config = self.gPlates()[1:]
        for pose_iter in range(iters):
            old = self
            plate_select = random.randint(1, self.num_sps-1)
            old_pose_b = self.sp_list[plate_select].getBottomT()
            old_pose_t = self.sp_list[plate_select].getTopT()
            new_pose_b = old_pose_b.copy()
            for j in range(6):
                new_pose_b[j] = new_pose_b[j] + random.uniform(-1 * perturb_key[j], perturb_key[j])
            self.sp_list[plate_select-1].IK(top_plate_pos = new_pose_b)
            self.sp_list[plate_select].IK(bottom_plate_pos = self.sp_list[plate_select-1].getTopT(), top_plate_pos = old_pose_t)
            self.sp_list[self.num_sps-1].IK(top_plate_pos = goal)
            if not self.comprehensiveValidation(goal):
                self.sp_list[plate_select-1].IK(top_plate_pos = old_pose_b)
                self.sp_list[plate_select].IK(self.sp_list[plate_select-1].getTopT(), old_pose_t)
                if not self.comprehensiveValidation(goal):
                    disp("Attempting To Return")
                    self.SplineIK(goal)
            if len(wrench) != 0:
                fmax = max(abs(self.ApplyForcesFromEE(wrench)[0].flatten()))
                if fmax > fmax_overall and self.comprehensiveValidation(goal):
                    fmax_overall = fmax
                    best_config = self.gPlates()[1:]
        self.IKC(best_config)

    """
       __      __   _ _     _       _
       \ \    / /  | (_)   | |     | |
        \ \  / /_ _| |_  __| | __ _| |_ ___  _ __ ___
         \ \/ / _` | | |/ _` |/ _` | __/ _ \| '__/ __|
          \  / (_| | | | (_| | (_| | || (_) | |  \__ \
           \/ \__,_|_|_|\__,_|\__,_|\__\___/|_|  |___/
    """


    def reValidate(self):
        """
        Please use subPlatformValidation() instead
        Remaining for Backwards Compatibility
        """
        #Remaining for Backwards Compatibility
        return self.subPlatformValidation()


    def subPlatformValidation(self):
        """
        Calls Validation Function on Each SubPlate
        """
        #Calls the Validation Function On Each Sub Plate
        for i in range(self.num_sps):
            validation = self.sp_list[i].validate()
            if validation == False:
                if i != 0:
                    self.sp_list[i].move(self.sp_list[i-1].getTopT())
        return self.gLens()


    def legLenValidator(self):
        leg_lengths = self.gLens().reshape((6*self.num_sps))
        if self.debug:
            disp(leg_lengths[np.where(leg_lengths > self.sp_list[0].leg_ext_max)], "over max")
            disp(leg_lengths[np.where(leg_lengths < self.sp_list[0].leg_ext_min)], "below min")
        if np.any(leg_lengths > self.sp_list[0].leg_ext_max+.00001) or np.any(leg_lengths < self.sp_list[0].leg_ext_min-.00001):
            return False
        return True
    def comprehensiveValidation(self, goal = None, donothing = True):
        """
        Validates everything. This Function is primarily used for Force Optimization
        Note that this Function does not correct plate positions. For that, call subPlatformValidation()
        """
        self.validation_error  = ""
        valid = True
        if goal != None:
            if(np.sum(abs(fsr.Error(self.getTopT(), goal))) > .001):
                if self.debug:
                    disp("Failure: End Effector Is Not At Goal")
                valid = False
                self.validation_error = "End Effector Is Not At Goal"
                return False

        for i in range(self.num_sps):
            if not self.sp_list[i].validate(donothing):
                self.validation_error += "SP[" + str(i) + "]:" + self.sp_list[i].validation_error + ", "
                valid = False
            if i > 0:
                if(np.sum(abs(fsr.Error(self.sp_list[i].getBottomT(), self.sp_list[i-1].getTopT()))) > .001):
                    self.validation_error += "SPs " + str(i) + " and " + str(i-1) + " are separated, "
                    valid = False
            if self.sp_list[i].curTrans[2] < .1 or fsr.Distance(self.getBottomT(), self.getTopT()) > 5 * self.sp_list[0].nominal_height:
                self.validation_error += "SP[" + str(i) + "]:" + " Potential Glitch With Plate Height"
                valid = False
        if valid:
            self.validation_error  = ""
        return valid


    def PlateValidity(self, pos1, sp):
        """
        Determines if a plate is "In front of" the plate preceeding it, at all points
        As of 2/14/2020, this function may be bugged, and is commented out in comprehensiveValidation()
        """
        locPos = fsr.GlobalToLocal(pos1, sp.getTopT())
        negative_sum = 0
        if locPos[2] < 0:
            negative_sum + locPos[2]
        for i in range(6):
            jpos = tm(np.concatenate([sp._tJS[0:3,i].reshape((3)),(np.zeros((3)))]))
            locPos = fsr.GlobalToLocal(pos1,jpos)
            if locPos[2] < 0:
                negative_sum + locPos[2]
        if negative_sum == 0:
            return 1
        print("Plate Validation Failed: " + str(negative_sum))
        return negative_sum


    def PosReValidate(self):
        """
        Please use subPlatformValidation() instead
        Remaining for Backwards Compatibility
        """
        for i in range(self.num_sps):
            if i == 0:
                self.sp_list[i].IK(self.sp_list[i].getBottomT(), self.sp_list[i].getTopT())
            else:
                self.sp_list[i].IK(self.sp_list[i-1].getTopT(), self.sp_list[i].getTopT())


    def Validator(self):
        """
        Calls Internal Validity
        Featureset has been rolled into comprehensiveValidation() and plateValidity().
        This Function is deprecated.
        """
        #Like individual SP, the Assemblers class has a validator that applies to the entire stack. This is it.
        if np.any(self.InteriorAngles()) > np.pi:
            return False
        for i in range(self.num_sps):
            bT = self.sp_list[i].getBottomT()
            tT = self.sp_list[i].getTopT()
            cT = abs(bT-tT)
            if np.any(cT[3:6] >= np.pi/2):
                #disp("Failed Her")
                return False
        return True

    def ForceValidator(self, wrench, maxForce):
        forces, wrenches = self.ApplyForcesFromEEWithGrav(wrench)
        for i in range(self.num_sps):
            if (np.any(self.sp_list[i].legForces > maxForce[i])):
                return False
        return True



    """
       _____      _   _                                     _    _____      _   _
      / ____|    | | | |                    /\             | |  / ____|    | | | |
     | |  __  ___| |_| |_ ___ _ __ ___     /  \   _ __   __| | | (___   ___| |_| |_ ___ _ __ ___
     | | |_ |/ _ \ __| __/ _ \ '__/ __|   / /\ \ | '_ \ / _` |  \___ \ / _ \ __| __/ _ \ '__/ __|
     | |__| |  __/ |_| ||  __/ |  \__ \  / ____ \| | | | (_| |  ____) |  __/ |_| ||  __/ |  \__ \
      \_____|\___|\__|\__\___|_|  |___/ /_/    \_\_| |_|\__,_| |_____/ \___|\__|\__\___|_|  |___/

    """

    def RandomPos(self, leglims):
        lengths = np.zeros((6,self.num_sps))
        for i in range(6):
            for j in range(self.num_sps):
                lengths[i,j] = random.uniform(self.sp_list[0].leg_ext_min+leglims, self.sp_list[0].leg_ext_max-leglims)
        self.FK(lengths)
        if (self.comprehensiveValidation() == False):
            self.RandomPos(leglims)
        return self.getTopT()


    def InteriorAngles(self):
        """
        Return the Interior Angles of the Assembler
        """
        angs = np.zeros((self.num_sps - 1))
        for i in range(self.num_sps - 1):
            angs[i] = fsr.AngleBetween(self.sp_list[i].getBottomT(), self.sp_list[i].getTopT(), self.sp_list[i + 1].getTopT())
        return angs


    def LegAngles(self):
        """
        Return the Angles from Normal of the Assembler Legs
        """
        angs = np.zeros((self.num_sps, 12))
        for i in range(self.num_sps):
            temp = self.sp_list[i].AngleFromNorm()
            angs[i, 0:12] = temp.reshape((12))
        return angs


    def gLens(self):
        """
        Return the leg lengths of the Assembler in its current pose
        """
        leg_lengths = np.zeros((6,self.num_sps))
        for i in range(self.num_sps):
            leg_lengths[0:6,i] = self.sp_list[i].lengths.copy().reshape((6))
        return leg_lengths


    def gPlates(self):
        """
        Return the poses of all the assembler plates in a list
        """
        plates = []
        plates.append(self.getBottomT())
        for i in range(self.num_sps):
            plates.append(self.sp_list[i].getTopT())
        return plates

    def gPlatesLocal(self):
        """
        Return the poses of all the assembler plates in a list
        """
        plates = []
        for i in range(self.num_sps):
            plates.append(self.sp_list[i].curTrans)
        return plates


    def getTopT(self):
        """
        Return the End Effector position of the Assembler"""
        return self.sp_list[self.num_sps - 1].getTopT()


    def getBottomT(self):
        """
        Return the Base Pose of the Assembler
        """
        return self.sp_list[0].getBottomT()

    def getJointPositions(self):
        """
        Returns a 3x6xn matrix of joint positions for the entire Assembler in the global space.
        n is the number of plates in the overall platform.
        [0:3,0,0] for example corresponds to the first joint position of the first plate.
        """
        jointPosMat = np.zeros((3,6,self.num_sps + 1))
        for i in range(self.num_sps):
            jointPosMat[0:3,:,i] = self.sp_list[i]._bJS.reshape((3,6))
        jointPosMat[0:3,:,self.num_sps] = self.sp_list[-1]._tJS.reshape((3,6))
        return jointPosMat

    def SetMasses(self, plateMass, actuatorTop, actuatorBottom, grav = 9.81):
        """
        Set masses for each SP in the Assembler, note that because central platforms share plates, these weights are halved with respect to end plates
        Takes in plateMass, actuator shaft mass, actuator bottom mass, and acceleration due to gravity
        """
        for i in range(self.num_sps):
            if i == 0:
                self.sp_list[i].SetMasses(plateMass, actuatorTop, actuatorBottom, grav, plateMass/2)
            elif i == self.num_sps - 1:
                self.sp_list[i].SetMasses(plateMass/2, actuatorTop, actuatorBottom, grav, plateMass)
            else:
                self.sp_list[i].SetMasses(plateMass/2, actuatorTop, actuatorBottom, grav)



    """
      ______                                        _   _____                              _
     |  ____|                                      | | |  __ \                            (_)
     | |__ ___  _ __ ___ ___  ___    __ _ _ __   __| | | |  | |_   _ _ __   __ _ _ __ ___  _  ___ ___
     |  __/ _ \| '__/ __/ _ \/ __|  / _` | '_ \ / _` | | |  | | | | | '_ \ / _` | '_ ` _ \| |/ __/ __|
     | | | (_) | | | (_|  __/\__ \ | (_| | | | | (_| | | |__| | |_| | | | | (_| | | | | | | | (__\__ \
     |_|  \___/|_|  \___\___||___/  \__,_|_| |_|\__,_| |_____/ \__, |_| |_|\__,_|_| |_| |_|_|\___|___/
                                                                __/ |
                                                               |___/
    """


    def ApplyForcesFromEE(self, eewrench):
        """
        Apply Forces from the end effector. Does not take into account gravity. Takes in A Force Wrench as an argument
        """
        legForces = np.zeros((6, self.num_sps))

        for i in range(self.num_sps - 1, -1, -1):
            tau = self.sp_list[i].MeasureForcesFromWrenchEE(self.sp_list[i].getBottomT(), self.sp_list[i].getTopT(), eewrench)
            eewrench = self.sp_list[i].WrenchBottomFromMeasuredForces(self.sp_list[i].getBottomT(), self.sp_list[i].getTopT(), tau)[0]
            legForces[0:6,i] = tau.reshape((6))
        return legForces, eewrench

    def ApplyForcesFromEE2(self, eewrench):
        """
        Refined Version of the ApplyForcesFromEE
        """
        legForces = np.zeros((6, self.num_sps))

        for i in range(self.num_sps):
            tau = self.sp_list[i].MeasureForcesFromWrenchEE(self.sp_list[i].getBottomT(), self.sp_list[i].getTopT(), eewrench)
            legForces[0:6,i] = tau.reshape((6))
        return legForces, self.sp_list[0].WrenchBottomFromMeasuredForces(self.sp_list[0].getBottomT(), self.sp_list[0].getTopT(), tau)[0]

    def ApplyForcesFromEEWithGrav(self, wrench, protect = False):
        """
        Carry Forces down from the top of the assembler, include gravity. Factor in Plate Masses and Actuator Masses
        """
        wrenches = [wrench]
        legForces = np.zeros((6, self.num_sps))
        for i in range(self.num_sps - 1, -1, -1):
            tau, wrench = self.sp_list[i].CarryMassCalc(wrench, protect)
            legForces[0:6,i] = tau.reshape((6))
            wrenches.append(wrench)
        return legForces, wrenches

    def ApplyForcesFromEEWithGravNew(self, wrench, protect = False):
        """
        Carry Forces down from the top of the assembler, include gravity. Factor in Plate Masses and Actuator Masses
        """
        wrenches = [wrench]
        legForces = np.zeros((6, self.num_sps))
        for i in range(self.num_sps - 1, -1, -1):
            tau, wrench = self.sp_list[i].CarryMassCalcNew(wrench, protect)
            legForces[0:6,i] = tau.reshape((6))
            wrenches.append(wrench)
        return legForces, wrenches

    def ApplyForcesBothEndsLocked(self, protect = False):
        #Case 1, There are an even number of stewart platforms
        wrenchi = fsr.GenForceWrench(self.sp_list[1].getTopT(), 0, np.array([0, 0, 0]))
        if (self.num_sps % 2) == 0:
            tau, wrencha = self.sp_list[0].CarryMassCalcUp(wrenchi, protect)
            tau, wrencha = self.sp_list[1].CarryMassCalcUp(wrencha, protect)
            tau, wrenchb = self.sp_list[3].CarryMassCalc(wrenchi, protect)
            tau, wrenchb = self.sp_list[2].CarryMassCalc(wrenchb, protect)


    """
      _    _               _                          _      _       _
     | |  | |             | |                        | |    (_)     | |
     | |__| | __ _ _ __ __| |_      ____ _ _ __ ___  | |     _ _ __ | | __
     |  __  |/ _` | '__/ _` \ \ /\ / / _` | '__/ _ \ | |    | | '_ \| |/ /
     | |  | | (_| | | | (_| |\ V  V / (_| | | |  __/ | |____| | | | |   <
     |_|  |_|\__,_|_|  \__,_| \_/\_/ \__,_|_|  \___| |______|_|_| |_|_|\_\

    """
    def linkHardware(self, IPList, portList, name = "", comm = None):
        if name == "":
            name = self.name
        else:
            self.name = name
        if self.comm == None and comm == None:
            self.comm = Communications()
        elif self.comm == None:
            self.comm = comm
        if self.link_state == 1:
            return
        else:
            for i in range(len(IPList)):
                self.sp_list[i].linkHardware(self.IPList[i], self.portList[i], self.name + "SP" + str(i), self.comm)
            self.link_state = 1



    """
       _____ _                 __  __      _   _               _
      / ____| |               |  \/  |    | | | |             | |
     | |    | | __ _ ___ ___  | \  / | ___| |_| |__   ___   __| |___
     | |    | |/ _` / __/ __| | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
     | |____| | (_| \__ \__ \ | |  | |  __/ |_| | | | (_) | (_| \__ \
      \_____|_|\__,_|___/___/ |_|  |_|\___|\__|_| |_|\___/ \__,_|___/

    """


    def move(self, T, protect = False, stationary = False):
        """
        Move entire Assembler Stack to another location and orientation
        This function and syntax are shared between all kinematic structures.
        """
        #Move entire Assembler Stack to another location and orientation
        #This function and syntax are shared between all kinematic structures.
        oldT = self.getTopT()
        self.sp_list[0].bottom_plate_pos = T
        self.current_base_pos = T
        for i in range(len(self.sp_list)):
            if i == 0:
                #Move each platform based on the stored translations and offsets from their base.
                self.sp_list[i].IK(top_plate_pos = fsr.LocalToGlobal(self.sp_list[i].getBottomT(), self.sp_list[i].curTrans), protect = protect)
                continue
            #Set each sp bottom transform to the top transform of the sp before it.
            self.sp_list[i].bottom_plate_pos = self.sp_list[i-1].getTopT()
            self.sp_list[i].IK(top_plate_pos = fsr.LocalToGlobal(self.sp_list[i].getBottomT(), self.sp_list[i].curTrans), protect = protect)
        if(stationary):
            self.SplineIK(oldT)

    def clone(self):
        """
        Duplicate Assembler Stack, return one with identical configuration
        This function and syntax are shared between all kinematic structures.
        """
        t_assembler = Assembler(self.num_sps, self.sp_radius, self.joint_cluster_spacing, self.sp_top_plate_offset)
        for i in range(self.num_sps):
            t_assembler.sp_list[i] = self.sp_list[i].clone()
        for i in range(self.num_sps-1):
            t_assembler.sp_list[i].bound_top = 0
            t_assembler.sp_list[i].bound_bottom = 0
        t_assembler.current_top_pos = self.sp_list[self.num_sps-1].getTopT()
        return t_assembler


    def flip(self):
        """
        Flip Assembler Stack, end pose is now home pose and vice versa
        This function and syntax are shared between all kinematic structures.

        This function is going to require additional work in the future TODO
        """
        #Reverse the ordering of the SPs, meaning the top is now the bottom platform.
        i = self.num_sps - 1
        self.current_base_pos = self.sp_list[self.num_sps - 1].getTopT() @ self.plate_inverter
        t_base = self.current_base_pos
        t_lst_top = self.sp_list[0].getBottomT() @ self.plate_inverter
        while i >= 0:
            t_trans = self.sp_list[i].getTopT() @ self.plate_inverter
            self.sp_list[i].top_plate_pos = self.sp_list[i].getBottomT() @ self.plate_inverter
            self.sp_list[i].bottom_plate_pos = t_trans
            t_joints = self.sp_list[i].topJoints
            self.sp_list[i].topJoints = self.sp_list[i].bottomJoints
            self.sp_list[i].bottomJoints = t_joints
            t_js = self.sp_list[i]._tJS
            self.sp_list[i]._tJS = self.sp_list[i]._bJS
            self.sp_list[i]._bJS = t_js
            self.sp_list[i].IK(protect = True)
            i = i - 1
        self.move(self.current_base_pos)


    def __str__(self):
        """
        Prints a string
        """
        return (str(self.num_sps) + " platform Assembler stack")


    def Draw(self, ax):
        """
        Draw a plot of the stack, requires an axis/plt object
        This function and syntax are shared between all kinematic structures.
        """
        DrawAssembler(self, ax)
