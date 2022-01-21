import numpy as np

class Point():

    def __init__(self, newx, newy, newz):
        self.x = newx
        self.y = newy
        self.z = newz

    def Update(self, otherx, othery, otherz):
        self.x = otherx
        self.y = othery
        self.z = otherz

    def __pow__(v, u):
        ##Crossproduct
    	return Point(
            v.y * u.z - v.z * u.y,
            v.z * u.x - v.x * u.z,
            v.x * u.y - v.y * u.x)
    def mod(self):
    	return pow((self.x ** 2) + (self.y ** 2) + (self.z ** 2), 0.5)
    def dot(self, v):
        return (self.x * v.x) + (self.y * v.y) + (self.z * v.z)
    def __add__(v, u):
        return Point(v.x + u.x, v.y + u.y, v.z + u.z)
    def __sub__(v, u):
        return Point(v.x - u.x, v.y - u.y, v.z - u.z)
    def __mul__(self, a):
        return Point(self.x*a,self.y*a,self.z*a)
    def __rmul__(self, a:float):
        return Point(self.x*a,self.y*a,self.z*a)
    def __eq__(self, other):
        if isinstance(other, Point):
            return (self.x==other.x and self.y==other.y and self.z==other.z)
        else:
            return False
    def __str__(self):
        return "{x},{y},{z}".format(x = self.x, y = self.y, z = self.z)
    def __eq__(self, other):
        if isinstance(other, Point):
            if self.x == other.x and self.y == other.y and self.z == other.z:
                return True
        return False

class Perimeter():

    def __init__(self, *args):
        self.normal = Point(0,0,0)
        self.area = Point(0,0,0)
        self.blend_points = np.array([])
        if args:
            if not isinstance(args[0][0], Point):
                ## np array of classes seems to point (memory level) at
                ##the first element only!!!
                ## This is a serious problem, keep an eye on it!!
                self.points = [Point(0,0,0) for i in range(args[0].shape[0])]
                for i in range(args[0].shape[0]):
                    self.points[i].Update(
                        args[0][i][0],
                        args[0][i][1],
                        args[0][i][2]
                        )
                ## Now back to numpy arrays...
                self.points = np.array(self.points)
            else:
                self.points = args[0]
        else:
            self.points = np.empty(0)

    def append(self, np_array):
    	self.points = np.append(self.points, np.array([np_array]), axis=0)
    def fix_distance(self, subdivision = 3):
        ## Creates new points between points that are too
        ##far apart from each other
        counter = 0
        distance = np.array([0.]*(self.points.shape[0]-1), dtype=float)

        for i in range(self.points.shape[0]-1):
            distance[i] = (self.points[i]-self.points[i+1]).mod()**2

        d0 = np.sum(distance)/(self.points.shape[0])
        aux = 0
        for i in range(self.points.shape[0]-1):
            if distance[i] >= (d0*subdivision):
                factor = int(distance[i]/d0)
                points_list = np.array([Point(0,0,0)]*(factor-1))
                for j in range(1, factor):
                    np_index = j/factor
                    new_point = (self.points[i+counter]-self.points[i+1+counter])*(np_index)
                    new_point += self.points[i+counter+1]
                    points_list[j-1] = new_point
                    aux += 1
                points_list = np.flip(points_list, axis=0)
                self.points = np.insert(self.points, i+counter+1, points_list)
                counter += aux
                aux = 0
    def remove_overlap(self,delta=0.01): #fix conditions
        def neighbourhood(p1, p2, mean, delta) -> bool:
            if (self.points[i] - self.points[j]).mod() <= delta*mean:
                return True
            return False
        aux = self.points
        counter = 0
        mean = 0
        for i in range(self.points.shape[0]-1):
            mean += (self.points[i]-self.points[i+1]).mod()
        mean = mean/(self.points.shape[0]-1)
        for i in range(self.points.shape[0]-1):
            for j in range(i+1,self.points.shape[0]-1):
                if neighbourhood(self.points[i],self.points[j],mean, delta):
                    aux = np.delete(aux,i-counter)
                    counter += 1
        self.points = aux
    def area_vec(self):
        self.area = Point(0,0,0)
        for n in range(1,self.points.shape[0]-1):
            v1 = self.points[n]-self.points[0]
            v2 = self.points[n+1]-self.points[0]
            cross = v1**v2
            self.area += cross*(1/2)
    def c_clockwise(self, global_orientation=Point(1,0,0)):
        ## Reorients surface to counter-clockwise
        ##and creates a area vector
        if self.area.mod()==0:
            self.area_vec()
        if self.area.dot(global_orientation)<0:
            self.points = np.flip(self.points,0)
            self.area = -1*self.area
            for bridges in range(self.blend_points.shape[0]):
                self.blend_points[bridges] = np.flip(self.blend_points[bridges], axis=0)
    def geometric_center(self) -> Point:
        x = 0
        y = 0
        z = 0
        N = self.points.shape[0]
        for i in range(N):
            x += self.points[i].x
            y += self.points[i].y
            z += self.points[i].z
        return Point(x/N,y/N,z/N)
    def find_intersection(self, p1, p2, p3, p4, border = True) -> bool:
        ## Lets find a new algorithm to find intersections
        ##between lines
        '''
        https://stackoverflow.com/questions/2316490/the-algorithm-to-find-the-point-of-intersection-of-two-3d-line-segment
        Read all the comments!!

        s = Dot(Cross(dc, db), Cross(da, db)) / Norm2(Cross(da, db))

        t = Dot(Cross(dc, da), Cross(da, db)) / Norm2(Cross(da, db))

        da = p2 - p1
        db = p4 - p3
        dc = p3 - p1
        '''
        da = p2 - p1
        db = p4 - p3
        dc = p3 - p1

        norm2 = ((da**db).mod())**2
        if norm2 == 0:
            d1 = p1 - p3
            d2 = p2 - p3
            d3 = p1 - p4
            d4 = p2 - p4
            cond1 = d1.dot(d2) < 0
            cond2 = d3.dot(d4) < 0
            if cond1 or cond2:
                return True
            else:
                return False
        s = (dc**db).dot(da**db) / norm2
        t = (dc**da).dot(da**db) / norm2
        if border:
            if ((s>=0 and s<=1) and (t>=0 and t<=1)):
                return True
            return False
        else:
            if ((s>0 and s<1) and (t>0 and t<1)):
                return True
            return False
    def fix_intersection(self):
        '''
        --Fixing intersections
        .Let i and j be two independent indexations to a list of Points (x,y)
        .With i < j, if the Points between i and i+1 creates a line that
        .intersects the line created by j and j+1, than fix the intersection by:
        revesing the order of the Points in the list from i+1 and j+1
        .This fixes the list in the sense that it will be no longer a
        self-intersecting curve
        '''
        p_points = self.points.shape[0]
        check = True
        Loops = 0   ## flexibility condition to avoid infinity
                    ##loops that may occur inside the while

        while check:
            found = False
            for i in range(p_points-3):
                for j in range(i+2, p_points-1):
                    if i==0 and j==p_points-2:
                        break
                    '''
                        If we find a point that rests exactly on top of a line
                    segment, then we will perturbe it by a small amount to avoid
                    having a self intersecting surface on the final mesh.
                        Trying to figure out w
                    '''
                    if self.find_intersection(
                            self.points[i],
                            self.points[i+1],
                            self.points[j],
                            self.points[j+1]):
                        found = True
                        aux = np.array([Point(0,0,0)])
                        for fix in self.points[(i+1):(j+1)]:
                            aux = np.append(aux,fix)
                        aux = np.delete(aux,0)
                        aux = np.flip(aux, axis=0)
                        if aux.size != 0:
                            for blends in range(self.blend_points.shape[0]):
                                sup = np.copy(self.blend_points[blends])
                                count1 = 0
                                count2 = 0
                                count3 = 0
                                count4 = 0
                                compile = np.array([self.points[i],
                                                    self.points[i+1],
                                                    self.points[j],
                                                    self.points[j+1]])
                                if sup[0] in compile:
                                    count1 += 1
                                if sup[1] in compile:
                                    count2 += 1
                                if sup[2] in compile:
                                    count3 += 1
                                if sup[3] in compile:
                                    count4 += 1
                                if count1 or count2 or count3 or count4: #remove later
                                    if 0:
                                        print(count1, count2, count3, count4)
                                        for p in self.points:
                                            print('"[{},{},{}]",'.format(p.x,p.y,p.z))
                                        print("blend")
                                        for p in self.blend_points[0]:
                                            print('"[{},{},{}]",'.format(p.x,p.y,p.z))
                                if count1 and not count2 and count3 and count4:
                                    self.blend_points[blends][0] = self.points[i]
                                    self.blend_points[blends][1] = self.points[j]
                                    self.blend_points[blends][2] = sup[1]
                                    self.blend_points[blends][3] = self.points[i+1]
                                if count1 and count2 and not count3 and count4:
                                    self.blend_points[blends][0] = self.points[i]
                                    self.blend_points[blends][1] = self.points[j]
                                    self.blend_points[blends][2] = sup[1]
                                    self.blend_points[blends][3] = self.points[j+1]
                                if count1 and count2 and count3 and not count4:
                                    self.blend_points[blends][0] = self.points[i]
                                    self.blend_points[blends][1] = self.points[j]
                                    self.blend_points[blends][2] = self.points[j+1]
                                    self.blend_points[blends][3] = sup[3]
                                if count1 and count2 and count3 and count4:
                                    self.blend_points[blends][1] = sup[2]
                                    self.blend_points[blends][2] = sup[1]
                            for replace in range(i+1, j+1):
                                self.points[replace] = aux[replace-i-1]

                        break
            ##Loop break if many intersections are encoutered
            Loops += 1
            if not found:
                check = False
            if Loops > 20:
                check = False
    def islands_ensemble(self, other): #needs commenting
        M = self.points.shape[0]-1
        N = other.points.shape[0]-1
        other.c_clockwise(self.area)
        small_dist = np.inf
        for i in range(M):
            p_i = self.points[i]
            for j in range(N):
                p_j = other.points[j]
                if (p_i-p_j).mod()<small_dist:
                    small_dist = (p_i-p_j).mod()
                    best_p_i = i
                    best_p_j = j
        vari = M+N+1
        merged = np.array([Point(0,0,0)]*(vari))
        delta = 0
        if best_p_i<M-1:
            for i in range(M):
                if i==best_p_i+1:
                    for j in range(N):
                        if best_p_j+j<N:
                            merged[i+j] = other.points[best_p_j+j]
                            last_j = best_p_j+j
                        else:
                            merged[i+j] = other.points[j-(N-best_p_j)]
                            last_j = j-(N-best_p_j)
                    delta = N
                    merged[i+delta] = self.points[i]
                else:
                    merged[i+delta] = self.points[i]

        else:
            for i in range(M+1):
                if i<M-1:
                    merged[i] = self.points[i]
                else:
                    for j in range(N):
                        if best_p_j+j<N:
                            merged[i+j] = other.points[best_p_j+j]
                            last_j = best_p_j+j
                        else:
                            merged[i+j] = other.points[j-(N-best_p_j)]
                            last_j = j-(N-best_p_j)
        merged[vari-1] = self.points[0]
        if self.blend_points.shape[0]==0:
            self.blend_points = np.array([[self.points[best_p_i],
                                    other.points[best_p_j],
                                    other.points[last_j],
                                    self.points[best_p_i+1]]])
        else:
            self.blend_points = np.append(self.blend_points,np.array([[self.points[best_p_i],
                                    other.points[best_p_j],
                                    other.points[last_j],
                                    self.points[best_p_i+1]]]), axis=0)
        self.points = merged
    def __str__(self):
        return "{L}\nwith shape = {S}".format(
                    L = [self.points[i].__str__()\
                        for i in range(self.points.shape[0])],
                    S = (self.points.shape)+(2,)
                    )
    def __add__(v,u):
        ## Caculates best point to connect two contours contained in the
        ## same slice

        M = v.points.shape[0]
        N = u.points.shape[0]
        cost_matrix = np.zeros((M-1,N-1))
        for m in range(M-1):
        	for n in range(N-1):
        		cost_matrix[m,n] = (v.points[m]-u.points[n]).mod()
        allMin = np.where(cost_matrix==np.amin(cost_matrix))
        final_min_cord = list(zip(allMin[0], allMin[1]))[0]
        vari = M+N
        final = [Point(0,0,0)]*(vari)
        m = 0
        n = final_min_cord[1]
        mc = 0
        nc = 0
        while mc<M:

            final[mc+nc] = Point(
                v.points[m].x,
                v.points[m].y,
                v.points[m].z)

            if m == final_min_cord[0]:

                while nc<N-1:

                    final[mc+nc] = Point(
                        u.points[n].x,
                        u.points[n].y,
                        u.points[n].z)
                    n += 1
                    nc += 1

                    if n == N:
                        n = 0

                final[mc+nc] = Point(
                    u.points[final_min_cord[1]].x,
                    u.points[final_min_cord[1]].y,
                    u.points[final_min_cord[1]].z)
                final[mc+nc + 1] = Point(
                    v.points[final_min_cord[0]-1],
                    v.points[final_min_cord[0]-1],
                    v.points[final_min_cord[0]-1])
                m += 0
                mc += 1

            m += 1
            mc += 1

            if m == M:

                m = 0

        final[vari-1] = Point(
            v.points[v.points.shape[0]-2].x,
            v.points[v.points.shape[0]-2].y,
            v.points[v.points.shape[0]-2].z)

        return final

class Surface():

    def __init__(self):
        self.slices = np.empty(0) ##collection of Perimeters
        self._surface = False ##Fully built surface
        self._intersection_range = 3000
        self.fix_limit = 3
        self.border_intersection = False ##
        self.surface_orientation = Point(0,0,0)
        self._intersection_counter = 0

    def set_parameters(self, **kwargs):
        eror = 0
        for k in kwargs:
            val = kwargs.get(k)
            if k=="intersection_range":
                self._intersection_range = val
                continue
            if k=="fix_limit":
                self.fix_limit= val
                continue
            print(f"Could not interpret {k} as valid argument")
            error+=1
        if error:
            self.help()
    def help():
        print("Send Help")
    def add_island(self, *arg):
        if arg:
            self.slices = np.append(
                self.slices,
                np.array([arg[0]]),
                axis=0
                )
        else:
            self.slices = np.append(
                self.slices,
                np.array([Perimeter()]),
                axis=0
                )
    def mesh_out(self): #implement and comment
        if self.out_surface:
            out = 0
        else:
            error = 0
    def build_surface(self, close_list=[]):
        self.surfaceV = "" ##3d reconstructed surface
        self.surfaceE = ""
        total_shift = 0
        self.slices[0].area_vec()
        self.surface_orientation = self.slices[0].area
        for n in range(self.slices.shape[0]-1):
            print(n)
            self.slices[n+1].c_clockwise(self.surface_orientation)
            dist_matrix = self.__CostMatrix(self.slices[n],self.slices[n+1])
            self.border_intersection = False
            '''
                After reordering the both sequences of points, we need
            to a way to conect all in between points that represent a
            surface that:
                1) is not self intersecting
                2) has the smallest possible area
                3) is closed
            -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
                If we find a point that all of its connections create
            intersections, than we must never use this point in our final
            mesh. So we list all this points per stitched surface and exclude
            them from our path find algorithm by setting its value to
            infinity.
            '''
            bad_connect = []
            rerun = False
            limit = 100000
            while not self.border_intersection:
                if len(bad_connect) >= limit:
                    skip_intersection = True
                    print("Skiping intersection check")
                else:
                    skip_intersection = False

                ##After finding a path with o intersections
                ## finding all min values contained inthe matrix
                ##there's usually only one, but the value might
                ##be repeated somewhere
                closest_point_dist = np.amin(dist_matrix)
                allMin = np.where(dist_matrix == closest_point_dist)
                list_cordinates = list(zip(allMin[0], allMin[1]))
                final_min_cord = list_cordinates[0]
                f0 = final_min_cord[0]
                f1 = final_min_cord[1]


                ## Re-order the points: put the first connection at (0,0)
                reordered_upper =  self.__Reordering(
                    self.slices[n],
                    final_min_cord[0])
                reordered_lower =  self.__Reordering(
                    self.slices[n+1],
                    final_min_cord[1])
                cost_matrix =  self.__CostMatrix(reordered_upper,reordered_lower)
                for bad in bad_connect:
                    if bad[0]>=f0:
                        bad1 = bad[0]-f0
                    else:
                        bad1 = bad[0]+(self.slices[n].points.shape[0]-f0-1)
                    if bad[1]>=f1:
                        bad2 = bad[1]-f1
                    else:
                        bad2 = bad[1]+(self.slices[n+1].points.shape[0]-f1-1)
                    cost_matrix[bad1,bad2] = np.inf
                mincost,the_path,wrong,total_cost = self.__FindPath(
                                                                cost_matrix,
                                                                self.slices[n].points.shape[0],
                                                                self.slices[n+1].points.shape[0],
                                                                reordered_upper,
                                                                reordered_lower,
                                                                skip_intersection)
                ##fixing relative order to absolute/initial order
                if not isinstance(wrong, int):
                    for w in wrong:
                        if w[0]+f0 <= self.slices[n].points.shape[0]-2:
                            wrong[0] += f0
                        else:
                            w[0] += f0-self.slices[n].points.shape[0]-2
                        if w[1]+f1 <= self.slices[n+1].points.shape[0]-2:
                            w[1] += f1
                        else:
                            w[1] += f1-self.slices[n+1].points.shape[0]-2
                        if [w[0],w[1]] in bad_connect:
                            dist_matrix[f0,f1] = np.inf
                        else:
                            bad_connect.append([w[0],w[1]])
                else:
                    dist_matrix[f0,f1] = np.inf

            ## The path is calculated based on the reordered points,
            ##so we should invert the transformation so that we have
            ##the path for the original set of points

            the_path = self.__FixPathOrder(
                the_path,
                final_min_cord,
                self.slices[n].points.shape[0],
                self.slices[n+1].points.shape[0])

            self.surfaceV += self.__Vertices(self.slices[n].points)
            self.surfaceE += self.__Edges(
                the_path,
                self.slices[n].points.shape[0]-1,
                self.slices[n+1].points.shape[0]-1,
                total_shift)

            total_shift += self.slices[n].points.shape[0] - 1
            self.border_intersection = False

        self.surfaceV += self.__Vertices(self.slices[n+1].points)
        for i in close_list:
            closing_points = self.slices[i].points
            self.slices[i].area_vec()
            area_vec = self.slices[i].area
            if i == 0:
                closing_shift = 0
            else:
                closing_shift = total_shift
            self.surfaceE += self.__CloseSurface(closing_points, area_vec, closing_shift)
        self.out_surface = True
    def super_resolution(self): #implement and comment
        self.super_surface
    def closebif(self, file_index, bif_list):
        '''
            There are 2 pairs of lines per connection created by merging
        islands. So we need to select those 2 pairs and put a surface on them
        to close all sruface holes.
            There are however some procidures such fix_intersection(), that
        may cause each pair to flip oriention individually. Instead of
        finding if they did or did not flip, we chose to simple allert when
        passing by one of the points.
            On the first pass, we record the next points because they are part
        of the line segment. On the second alert, we stop the recording.
        Finally, we grab 2 pairs at a time and triangulate them.
            Note that having more than 2 pairs means that there 3 or more
        islands on a given slice.
        '''

        bif = np.copy(self.slices[file_index].points)
        blend_points = np.copy(self.slices[file_index].blend_points)
        area = self.slices[file_index].area

        shift = 0
        for s in range(file_index):
            shift += self.slices[s].points.shape[0]-1

        for bridges in self.slices[file_index].blend_points:
            bridge_mut = np.copy(bridges) #dont mess with the original: leanrt the hard way

            def side(bridge_mut, bif, case = [0,0]):
                '''
                    Nice exception has appeared more than once. iF the link
                between two islands is point zero, we have to cosinder the cases
                of the bridge being the points before and after.
                    There's no good proof, but its quite intuitive that the
                smallest sequence of points should be the actuall bridge.
                '''
                part1 = np.array([bridge_mut[0],bridge_mut[1]])
                part2 = np.array([bridge_mut[2],bridge_mut[3]])
                bif_diff = np.array([Point(0,0,0)])
                index_list = np.array([],dtype=int)
                count1 = 0
                count2 = 0
                start_part1 = False
                start_part2 = False
                for point in range(case[0],bif.shape[0]-case[1]): #reccording loop
                    if bif[point] in part1:
                        start_part1 = True
                        count1 += 1
                    if bif[point] in part2:
                        start_part2 = True
                        count2 += 1
                    if start_part1:
                        bif_diff = np.append(bif_diff, bif[point])
                        if point+1==bif.shape[0]:
                            index_list = np.append(index_list, shift+1)
                        else:
                            index_list = np.append(index_list, point+shift+1)
                        if count1==2:
                            start_part1 = False
                    if start_part2:
                        bif_diff = np.append(bif_diff, bif[point])
                        if point+1==bif.shape[0]:
                            index_list = np.append(index_list, shift+1)
                        else:
                            index_list = np.append(index_list, point+shift+1)
                        if count2==2:
                            start_part2 = False
                return bif_diff, index_list

            bif_diff1, index_list1 = side(bridge_mut, bif, case = [0,1])
            bif_diff2, index_list2 = side(bridge_mut, bif, case = [1,0])
            if index_list1.shape[0]<index_list2.shape[0]:
                bif_diff, index_list = bif_diff1, index_list1
            else:
                bif_diff, index_list = bif_diff2, index_list2
            index_list = np.append(index_list, index_list[0])
            bif_diff = np.delete(bif_diff,0,0)
            bif_diff = np.append(bif_diff, bif_diff[0])
            #print(index_list-shift,self.slices[file_index].points.shape[0])
            self.surfaceE += self.__CloseSurface(bif_diff, area, shift, index_list)
    def close_extra(self, island):
        ## Simply takes an island and triangulate it
        closing_points = island.points
        self.surfaceV_extra = self.__Vertices(closing_points)
        island.area_vec()
        area_vec = island.area
        self.surfaceE_extra = self.__CloseSurface(closing_points, area_vec, 0)

    ## Not meant for end-user
    def __CloseSurface(self, closing_points, area_vec, shift=0, index_list = None):#needs comments
        '''
            Explanation
        '''
        number_points = closing_points.shape[0]-1
        points = np.array([[Point(0,0,0),0]]*number_points)
        edges = ''

        for i in range(number_points):
            points[i][0] = closing_points[i]
            #print('"[{},{},{}]",'.format(closing_points[i].x,closing_points[i].y,closing_points[i].z))
            if not isinstance(index_list, np.ndarray):
                points[i][1] = i+1+shift #+1 corrects the .obj file format counting
            else:
                points[i][1] = index_list[i]

        def is_ear(GSP, p_i,area_vec): #check for intersection, points inside triangulation...
            def point_tiangle_3D(p1, p2, p3, p):
                ##returns if a point is inside the triangle surface or not
                v0 = p3 - p1
                v1 = p2 - p1
                v2 = p - p1
                dot00 = v0.dot(v0)
                dot01 = v0.dot(v1)
                dot02 = v0.dot(v2)
                dot11 = v1.dot(v1)
                dot12 = v1.dot(v2)
                if (dot00 * dot11 - dot01 * dot01) == 0:
                    return False
                invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
                u = (dot11 * dot02 - dot01 * dot12) * invDenom
                v = (dot00 * dot12 - dot01 * dot02) * invDenom
                eta = 1e-5
                return (u>=0-eta) and (v>=0-eta) and (u+v<1+eta)
            if p_i == 0:
                p1 = GSP.shape[0]-1
            else:
                p1 = p_i-1
            if p_i == GSP.shape[0]-1:
                p3 = 0
            else:
                p3 = p_i+1
            displacement1 = GSP[p1][0] - GSP[p_i][0]
            displacement2 = GSP[p3][0] - GSP[p_i][0]
            displacement1 = displacement1*(1/displacement1.mod())
            displacement2 = displacement2*(1/displacement2.mod())
            the_dot = displacement1.dot(displacement2)
            if the_dot>1:
                the_dot = 1
            if the_dot<-1:
                the_dot = -1
            angle1 = np.arccos(the_dot)

            if ((-1*displacement1)**displacement2).dot(area_vec) < 0:
                return False
            if angle1==np.pi:
                return False

            for index in range(GSP.shape[0]):
                if index==p_i or index==p1 or index==p3:
                    continue
                if point_tiangle_3D(GSP[p_i][0], GSP[p1][0], GSP[p3][0], GSP[index][0]):
                    return False
            for index in range(GSP.shape[0]-1):
                if index==p_i or index==p1 or index==p3:
                    continue
                if index==p_i+1 or index==p1+1 or index==p3+1:
                    continue
                if Perimeter().find_intersection(
                    GSP[index][0],
                    GSP[index+1][0],
                    GSP[p1][0],
                    GSP[p3][0],
                    False):
                    return False
            return True
        def triang_ear(GSP, p_i): #string outrput
            if p_i == 0:
                p0 = GSP[GSP.shape[0]-1][1]
            else:
                p0 = GSP[p_i-1][1]
            p1 = GSP[p_i][1]
            if p_i == GSP.shape[0]-1:
                p2 = GSP[0][1]
            else:
                p2 = GSP[p_i+1][1]
            s = "f " +str(p0) +\
                    " " + str(p1) +\
                    " " + str (p2) + "\n"
            return s

        loop_max = points.shape[0]-2
        triang_count = 1
        while triang_count!=loop_max:
            for i in range(points.shape[0]):
                if is_ear(points,i,area_vec):
                    edges += triang_ear(points,i)
                    points = np.delete(points,i,0)
                    triang_count += 1
                    break
                if i == points.shape[0]-1:
                    close_problem = True
                    triang_count=loop_max
                else:
                    close_problem = False
                if points.shape[0]==3:
                    triang_count=loop_max
        edges += triang_ear(points,1)

        return edges
    def __CostMatrix(self, reordered_upper, reordered_lower) -> np.ndarray:
        ## Upper stands for the surface on top and Lower for the one in the bottom
        M = reordered_upper.points.shape[0]
        N = reordered_lower.points.shape[0]
        cost_matrix = np.zeros((M-1,N-1))

        for m in range(M-1):
            for n in range(N-1):
                cost_matrix[m,n] = (reordered_upper.points[m] - reordered_lower.points[n]).mod()

        return cost_matrix
    def __FindPath(self, final_matrix, M, N, reordered_upper, reordered_lower, skip_intersection = False):#needs comments
        def surface_intersection(the_path, path_limit, next, upper, reordered_upper, reordered_lower, skip_intersection = False, final_cond=[False,[0,0]]) -> bool:
            '''
                Given a triangle with vertices p1, p2 and p3, we wish to know if a line segment
            (q1,q2) intersects it.
                1) a0 and b0 are the index of the points
                2) The given triangle is the new triangle being inserted in the 3D mesh
                3) Loop over all pairs of lines because thats the information contained
                    in the the_path list -> think that to get the triangles we still need
                    to process the_path in __Vertices() and __Edges() functions
            '''
            def line_triangle_intersection(q1, q2, p1, p2, p3):
                ## stackoverflow.com/questions/42740765/intersection-between-line-and-triangle-in-3d
                def volume(a, b, c, d):
                    vol = (b-a) ** (c-a)
                    vec = d - a
                    ## inner product
                    vol = vol.x*vec.x + vol.y*vec.y + vol.z*vec.z
                    return vol

                condition = volume(q1,p1,p2,p3)*volume(q2,p1,p2,p3)
                eta = 1e-8
                if condition < 0:
                    if volume(q1,q2,p1,p2)*volume(q1,q2,p2,p3) > 0-eta and\
                        volume(q1,q2,p1,p2)*volume(q1,q2,p3,p1) > 0-eta:
                        return True
                return False
            if path_limit < 3:
                return [-1,-1], False

            ## if speed is needed in the future
            ##we may try limiting the search range
            if path_limit > self._intersection_range-1:
                search_limit = path_limit - self._intersection_range
            else:
                search_limit = 0
            if not final_cond[0]:
                if path_limit < the_path.shape[0]:
                    p_index = the_path[path_limit]
                else:
                    return [-1,-1], False
            else:
                p_index = final_cond[1]

            if upper:
                p1 = reordered_upper.points[next[0]]
                p2 = reordered_lower.points[next[1]]
                p3 = reordered_lower.points[p_index[1]]
            else:
                p1 = reordered_lower.points[next[1]]
                p2 = reordered_upper.points[next[0]]
                p3 = reordered_upper.points[p_index[0]]
            for i in the_path[search_limit:path_limit+1]:
                a0 = int(i[0])
                b0 = int(i[1])
                q1 = reordered_upper.points[a0]
                q2 = reordered_lower.points[b0]
                if line_triangle_intersection(q1, q2, p1, p2, p3):
                    if skip_intersection:
                        self._intersection_counter += 1
                        return [-1,-1], False
                    return [a0,b0], True

            return [-1,-1], False

        def retract(m_local,n_local,min_cost_local,index_local,the_path, counter_local):
            m_local,n_local=the_path[index_local]
            min_cost_local[m_local][n_local]=np.inf
            the_path[index_local]=[0,0]
            #print(the_path[index_local-3:index_local+3],index_local,the_path[index_local],m_local,n_local)
            index_local -= 1
            return m_local,n_local,min_cost_local,index_local,counter_local+1

        M = M - 1
        N = N - 1

        ofinal_matrix = final_matrix
        min_cost = np.zeros((M,N))
        min_cost[0][0] = final_matrix[0][0]

        ## setting the upper border cost
        for j in range(1,N):
            min_cost[0][j] = min_cost[0][j-1] + final_matrix[0][j]

        ## setting the left border cost
        for i in range(1,M):
            min_cost[i][0] = min_cost[i-1][0] + final_matrix[i][0]

        for i in range(1,M):
            for j in range(1,N):
                best = min(min_cost[i-1][j],min_cost[i][j-1])
                min_cost[i][j] = best + final_matrix[i][j]
                if min_cost[i][j]<=0:
                    print("Negative cost on the path")

        ## Everything from now on is a way of finding what's the acctual path
        ##not only the cost of getting there.
        total_cost = min_cost[M-1][N-1]
        var1 = False
        var2 = False
        the_path = np.array([[0,0]]*(M+N-2), dtype=int)
        the_path[M+N-3] = [M-1,N-1]
        m = M-1
        n = N-1
        the_path = np.insert(the_path, 0, [[M-1,N-1]], axis=0)
        index = 0
        fix_counter = 0
        while index<=M+N-3:
            ##  01/2022 -> changed to while loop beacause the index needs to be
            ##manipulated on the fly.

            '''
                1) The loop starts at the end of the 2D path matrix (M,N)
                2) We get the smallest value when going up (M-1,N) or left (M,N-1)
                3) Check for intersections with previous triangles in the mesh:
                    3.1) If up/left is intersection, go to check for left/up
                        If it is:
                        3.1.1) Try to retract the path find mark current point as infinity cost (bad point)
                        3.1.2) If too many retracts are performed -> return and try a new starting point
                        If not intersection pick left/up
                4) If reached (0,x) or (x,0) -> the rest of the path is trivial: go either
                    all the way up, or all the way left -> This should never happen in a realistic
                    reconstruction, be aware!
            '''
            if index<-1:
                return 0,0,[[0,0]],total_cost
            if m>0 and n>0:
                if min_cost[m-1][n] < min_cost[m][n-1]:
                    check = surface_intersection(the_path,
                                index,
                                [m-1,n],
                                False,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:
                        check2 = surface_intersection(the_path,
                                    index,
                                    [m,n-1],
                                    True,
                                    reordered_upper,
                                    reordered_lower,
                                    skip_intersection)
                        if check2[1]:# or min_cost[m-1][n]==np.inf:
                            ##[m,n] -> Bad point that always create intersection
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                    return 0,0,[[m,n],check[0],check2[0]],total_cost
                                else:
                                    return 0,0,[[m,n],check[0]],total_cost
                        else:
                            if not min_cost[m][n-1] == np.inf:
                                n = n - 1
                            else:
                                if fix_counter<self.fix_limit:
                                    m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                    m,n = the_path[index]
                                    continue
                                else:
                                    if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                        return 0,0,[[m,n],check[0],check2[0]],total_cost
                                    else:
                                        return 0,0,[[m,n],check[0]],total_cost
                                n=n-1
                    else:
                        if not min_cost[m-1][n] == np.inf:
                            m = m - 1
                        else:
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                return 0,0,[[m,n],check[0]],total_cost
                else:
                    check = surface_intersection(the_path,
                                index,
                                [m,n-1],
                                True,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:
                        check2 = surface_intersection(the_path,
                                    index,
                                    [m-1,n],
                                    False,
                                    reordered_upper,
                                    reordered_lower,
                                    skip_intersection)
                        if check2[1]:# or min_cost[m][n-1]==np.inf:
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                    return 0,0,[[m,n],check[0],check2[0]],total_cost
                                else:
                                    return 0,0,[[m,n],check[0]],total_cost
                        else:
                            if not min_cost[m-1][n] == np.inf:
                                m = m - 1
                            else:
                                if fix_counter<self.fix_limit:
                                    m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                    m,n = the_path[index]
                                    continue
                                else:
                                    if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                        return 0,0,[[m,n],check[0],check2[0]],total_cost
                                    else:
                                        return 0,0,[[m,n],check[0]],total_cost
                                m=m-1
                    else:
                        if not min_cost[m][n-1] == np.inf:
                            n = n - 1
                        else:
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                return 0,0,[[m,n],check[0]],total_cost
            else:
                if m<=0:
                    check = surface_intersection(the_path,
                                index,
                                [m,n-1],
                                True,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:# or min_cost[m][n-1]==np.inf:
                        if fix_counter<self.fix_limit:
                            m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                            m,n = the_path[index]
                            continue
                        else:
                            return 0,0,[[m,n],check[0]],total_cost
                    n = n - 1
                else:
                    check = surface_intersection(the_path,
                                index,
                                [m-1,n],
                                False,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:# or min_cost[m-1][n]==np.inf:
                        if fix_counter<self.fix_limit:
                            m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                            m,n = the_path[index]
                            continue
                        else:
                            return 0,0,[[m,n],check[0]],total_cost
                    m = m - 1

            the_path[index+1] = [m,n] ##+1 because of the insert before the loop

            if [m,n] == [0,N-1]:
                var1 = True
            if [m,n] == [M-1,0]:
                var2 = True

            index += 1
        ##var1 and var2 are used to add a single point in order to make the
        ##the graph a closed cicle

        ## The final connections are made by inserting EITHER the top right corner
        ## or the left low corener.
        ## Note that, in this case ONLY, two triangles are made With the begining
        ##and the end of the of the path, making it a closed loop
        ## For that reason, two checks are necessary for intersection.

        if var1:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],[0,0]],total_cost

            the_path = np.append(the_path, [[M-1,0]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[0][N-1]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]

        if var2:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],check[0]],total_cost

            the_path = np.append(the_path, [[0,N-1]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[0][N-1]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]

        if ofinal_matrix[M-1][0]<ofinal_matrix[0][N-1]:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],[0,0]],total_cost
            the_path = np.append(the_path, [[M-1,0]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[M-1][0]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]
        else:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],check[0]],total_cost
            the_path = np.append(the_path, [[0,N-1]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[0][N-1]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]
    def __Reordering(self, contour, final_min_cord : int):
        M = contour.points.shape[0]
        reordered = [Point(0,0,0)]*M

        for i in range(M):

            if (i-final_min_cord) >= 0:

                index = i - final_min_cord
                reordered[index] = Point(
                    contour.points[i].x,
                    contour.points[i].y,
                    contour.points[i].z
                    )
            else:
                index = M - final_min_cord + i - 1
                reordered[index] = Point(
                    contour.points[i].x,
                    contour.points[i].y,
                    contour.points[i].z
                    )

        reordered[M-1] = Point(
            contour.points[final_min_cord].x,
            contour.points[final_min_cord].y,
            contour.points[final_min_cord].z
            )

        return Perimeter(np.array(reordered))
    def __FixPathOrder(self, path, final_min_cord : list, M, N) -> np.ndarray:
        fix_path = np.zeros(path.shape, dtype=int)
        for i in range(path.shape[0]):
            if path[i][1]+final_min_cord[1]<=N-2:
                fix_path[i][1] = path[i][1] + final_min_cord[1]
            else:
                fix_path[i][1] = path[i][1] - (N - 1 - final_min_cord[1])
            if path[i][0]+final_min_cord[0]<=M-2:
                fix_path[i][0] = path[i][0] + final_min_cord[0]
            else:
                fix_path[i][0] = path[i][0] - (M - 1 - final_min_cord[0])
        return fix_path
    def __Vertices(self, vertices) -> str:
        string = ""
        for i in range(vertices.shape[0]-1):
            text =  "v " + str(vertices[i].x) +\
                    " " + str(vertices[i].y) +\
                    " " + str(vertices[i].z) + "\n"
            string = string + text
        return string
    def __Edges(self, the_path : np.ndarray, M, N, shift) -> str:
        string = ""

        for i in range(the_path.shape[0]-1):

            if int(the_path[i][1]) == int(the_path[i+1][1]):

                text1 = "f " +str(int(the_path[i][0])+1+shift) +\
                        " " + str(int(the_path[i][1])+1+M+shift) +\
                        " " + str (int(the_path[i+1][0])+1+shift) + "\n"

                string += text1

            else:

                text2 = "f " +str(int(the_path[i][1])+1+M+shift) + \
                        " " + str(int(the_path[i+1][0])+1+shift) + \
                        " " + str (int(the_path[i+1][1])+1+M+shift) + "\n"

                string += text2

        if  int(the_path[the_path.shape[0]-1][0])+1 == int(the_path[the_path.shape[0]-1][1])+1+M or\
            int(the_path[the_path.shape[0]-1][0])+1 == int(the_path[0][0])+1 or\
            int(the_path[0][0])+1 == int(the_path[the_path.shape[0]-1][1])+1+M:

            string =    string + "f " +\
                        str(int(the_path[the_path.shape[0]-1][1])+1+M+shift) + " " +\
                        str(int(the_path[the_path.shape[0]-1][0])+1+shift) + " " +\
                        str (int(the_path[0][1])+1+M+shift) + "\n"

        else:

            string =    string + "f " +\
                        str(int(the_path[the_path.shape[0]-1][0])+1+shift) + " " +\
                        str(int(the_path[the_path.shape[0]-1][1])+1+M+shift) + " " +\
                        str (int(the_path[0][0])+1+shift) + "\n"

        return string
    def __str__(self):
        return "Surface shape = {S}\nPerimeters shape = {L}".format(
                                            L = [self.slices[i].points.shape[0] for i in range(self.slices.shape[0])],
                                            S = (self.slices.shape[0]))
