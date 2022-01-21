## Reserved to unit and integration tests
if __name__ == "__main__":
    no_rotation = True
    S = Surface()
    I = Perimeter()
    if 0:
        I = Perimeter()
        I.append(Point(-4,6,0))
        I.append(Point(0,2,0))
        I.append(Point(2,5,0))
        I.append(Point(7,0,0))
        I.append(Point(5,-6,0))
        I.append(Point(3,3,0))
        I.append(Point(0,-5,0))
        I.append(Point(-6,0,0))
        I.append(Point(-2,1,0))
        I.append(Point(-4,6,0))
        I2 = Perimeter()
        I2.append(Point(-4,6,1))
        I2.append(Point(0,2,1))
        I2.append(Point(2,5,1))
        I2.append(Point(7,0,1))
        I2.append(Point(5,-6,1))
        I2.append(Point(3,3,1))
        I2.append(Point(0,-5,1))
        I2.append(Point(-6,0,1))
        I2.append(Point(-2,1,1))
        I2.append(Point(-4,6,1))
        S = Surface()
        S.add_island(I)
        S.add_island(I2)
        S.build_surface([0,1])
        print(Point(0,0,0)==1,1==Point(0,0,0),Point(0,0,0)==Point(1,1,1),Point(0,0,0)==Point(0,0,0))
        with open("gold_test4.obj", "w") as out_file:
            out_file.write(S.surfaceV)
            out_file.write(S.surfaceE)

    if 0:
        I.append(Point(0,0,0))
        I.append(Point(0,1,0))
        I.append(Point(1,1,0))
        I.append(Point(2,1,0))
        I.append(Point(3,1,0))
        I.append(Point(3,3,0))
        I.append(Point(1,3,0))
        I.append(Point(1,2,0))
        I.append(Point(4,2,0))
        I.append(Point(4,0.5,0))
        I.append(Point(2.5,0.5,0))
        I.append(Point(2.5,2.5,0))
        I.append(Point(1.5,2.5,0))
        I.append(Point(1.5,0.5,0))
        I.append(Point(1,0,0))
        I.append(Point(0,0,0))
    if no_rotation:
        ## 8 shape
        I.append(Point(1,1,0))
        I.append(Point(1,2,0))
        I.append(Point(-1,2,0))
        I.append(Point(-1,1,0))
        I.append(Point(1,-1,0))
        I.append(Point(1,-2,0))
        I.append(Point(-1,-2,0))
        I.append(Point(-1,-1,0))
        I.append(Point(1,1,0))
        I.fix_intersection()
        I.c_clockwise()
        S.add_island(I)

        ##big box
        I = Perimeter()
        I.append(Point(1,1,1))
        I.append(Point(1,2,1))
        I.append(Point(-1,2,1))
        I.append(Point(-1,1,1))
        I.append(Point(-1,-1,1))
        I.append(Point(-1,-2,1))
        I.append(Point(1,-2,1))
        I.append(Point(1,-1,1))
        I.append(Point(1,1,1))
        I.fix_intersection()
        I.fix_distance()
        I.c_clockwise()
        S.add_island(I)

        ##big box w/ double intersection
        I = Perimeter()
        I.append(Point(1,1,2))
        I.append(Point(1,2,2))
        I.append(Point(-1,2,2))
        I.append(Point(-1,1,2))
        I.append(Point(2,0,2))
        I.append(Point(-1,-1,2))
        I.append(Point(-1,-2,2))
        I.append(Point(1,-2,2))
        I.append(Point(1,-1,2))
        I.append(Point(1,1,2))
        I.fix_intersection()
        I.c_clockwise()
        S.add_island(I)
        S.build_surface()

        with open("control.obj", "w") as out_file:
            out_file.write(S.surfaceV)
            out_file.write(S.surfaceE)
    if 0:
        check2 = surface_intersection(the_path, index, [m,n-1], False, reordered_upper, reordered_lower)
        if check2[1]:
            for check_element_index in range(index):
                check_element = the_path[check_element_index]
                if check_element[0] == check2[0][0] and check_element[1] == check2[0][1]:
                    index = check_element_index
                    i = M + N - 3 - index
                    if check_element[0] == the_path[check_element_index-1][0]:
                        for j in range(check_element_index,index):
                            the_path[j] = [0,0]
                        n = the_path[check_element_index-1][1] -1
                        m = the_path[check_element_index-1][0]
                        skip = True
                    else:
                        for j in range(check_element_index,index):
                            the_path[j] = [0,0]
                        n = the_path[check_element_index-1][1]
                        m = the_path[check_element_index-1][0] - 1
                        skip = True
                    break
        else:
            do = 0
