
class color_design:
    """ Creating a color class to get a color from DTU Design Guide
        
        Input
            color:  The color you want, you can either give a number between 1-11 (int). 
                    or you can give a color (str) from this list:
                    corporate red, blue, bright green, navy blue,
                    yellow, orange, pink, grey, red, green, purble.
 
        Output
            self.color = The wanted color in RGB values. The type is a tuple with numbers between 0-1.
    """
    def color_op(self,chosen_color):
        """This function is findning the RGB values for the wanted color
        Input
            _chosen_color:  The color you want, you can either give a number between 1-11. The type is a int. 
                    or you can give a color (str) from this list:
                    corporate red, blue, bright green, navy blue,
                    yellow, orange, pink, grey, red, green, purble.
 
        Output
            self.color = The wanted color in RGB values. The type is a tuple with numbers between 0-1.
        

        """
        def Corporate_red_dtu():
            """
            Given the Corporate red RGB values

            """
            color = [153,0,0]
            return color
        
        def blue_dtu():
            """
            Given the DTU blue RGB values
            
            """
            color = [47,62,234]
            return color

        def bright_green_dtu():
            """
            Given the DTU brigth green RGB values

            """
            color = [31,208,130]
            return color

        def navy_blue_dtu():
            """
            Given the DTU navy blue RGB values
            
            """
            color  = [3,15,79]
            return color

        def yellow_dtu():
            """
            Given the DTU yellow RGB values
            
            """
            color  = [246,208,77]
            return color
        
        def orange_dtu():
            """
            Given the DTU orange RGB values
            
            """
            color  =  [252,118,52]
            return color

        def pink_dtu():
            """
            Given the DTU pink RGB values
            
            """
            color  = [247,187,177]
            return color

        def grey_dtu():
            """
            Given the DTU grey RGB values
            
            """
            color   = [218,218,218]
            return color

        def red_dtu():
            """
            Given the DTU red RGB values
            
            """
            color  = [232,63,72]
            return color

        def green_dtu():
            """
            Given the DTU green RGB values

            """
            color  = [0,136,53]
            return color
        
        def purble_dtu():
            """
            Given the DTU purble RGB values
            
            """
            color  = [121,35,142]
            return color
        
        if type(chosen_color)==str:
            ops = {
                "corporate red": Corporate_red_dtu(),
                "blue": blue_dtu(),
                "bright green": bright_green_dtu(),
                "navy blue": navy_blue_dtu(),
                "yellow": yellow_dtu(),
                "orange": orange_dtu(),
                "pink": pink_dtu(),
                "grey": grey_dtu(),
                "red": red_dtu(),
                "green": green_dtu(),
                "purble": purble_dtu()

            }
        else:
            ops = {
                1: Corporate_red_dtu(),
                2: blue_dtu(),
                3: bright_green_dtu(),
                4: navy_blue_dtu(),
                5: yellow_dtu(),
                6: orange_dtu(),
                7: pink_dtu(),
                8: grey_dtu(),
                9: red_dtu(),
                10: green_dtu(),
                11: purble_dtu()

            }
        color = ops.get(chosen_color)
        return color

    def __init__(self,color):
        # The constructor
        temp = self.color_op(color)
        self.color = [x/255 for x in temp]