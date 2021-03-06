""" The common code for a gradient editor for `tvtk.LookupTables` and
`tvtk.VolumeProperty` color transfer functions.  Most of the code is
independent of tvtk however.

The toolkit specific code is in toolkit specific files.  This code is
distributed under the conditions of the BSD license.

This code was originally written by Gerald Knizia <cgk.d@gmx.net> and
later modified by Prabhu Ramachandran for tvtk and MayaVi2.

Copyright (c) 2005-2006, Gerald Knizia and Prabhu Ramachandran
"""

from os.path import splitext

from tvtk.api import tvtk


##########################################################################
# Utility functions.
##########################################################################
def lerp(arg0,arg1,f):
    """linearly interpolate between arguments arg0 and arg1.

       The weight f is from [0..1], with f=0 giving arg0 and f=1 giving arg1"""
    return (1-f)*arg0 + f*arg1

def rgba_to_hsva(r,g,b,a):
    """Convert color from RGBA to HSVA.

    input: r,g,b,a are from [0..1]
    output: h,s,v,a are from [0..1] (h will never be 1.0)

    See http://en.wikipedia.org/wiki/HSV_color_space
    Only difference: hue range is [0..1) here, not [0..360)."""
    max_comp = max((r,g,b))
    min_comp = min((r,g,b))
    h = 1.0/6.0 #60.0
    if ( max_comp != min_comp ):
        if ( r >= g) and ( r >= b ):
            h *= 0 + (g-b)/(max_comp-min_comp)
        elif ( g >= b ):
            h *= 2 + (b-r)/(max_comp-min_comp)
        else:
            h *= 4 + (r-g)/(max_comp-min_comp)
    if h < 0:
            h += 1.0
    if h > 1.0:
            h -= 1.0
    if ( max_comp != 0 ):
        s = ( max_comp - min_comp )/max_comp
    else:
        s = 0
    v = max_comp
    return (h,s,v,a)

def hsva_to_rgba(h_,s,v,a):
    """Convert color from HSVA to RGBA.

    input: h,s,v,a are from [0..1]
    output: r,g,b,a are from [0..1]

    See http://en.wikipedia.org/wiki/HSV_color_space
    Only difference: hue range is [0..1) here, not [0..360)."""
    (r,g,b,a) = (v,v,v,a)
    h = h_ * 360.0
    if ( s < 1e-4 ):
        return (r,g,b,a)#zero saturation -> color acromatic
    hue_slice_index = int(h/60.0)
    hue_partial = h/60.0 - hue_slice_index
    p = v * ( 1 - s )
    q = v * ( 1 - hue_partial * s )
    t = v * ( 1 - (1-hue_partial) * s )
    if ( 0 == hue_slice_index ):
        r, g, b = v, t, p
    elif ( 1 == hue_slice_index ):
        r, g, b = q, v, p
    elif ( 2 == hue_slice_index ):
        r, g, b = p, v, t
    elif ( 3 == hue_slice_index ):
        r, g, b = p, q, v
    elif ( 4 == hue_slice_index ):
        r, g, b = t, p, v
    elif ( 5 == hue_slice_index ):
        r, g, b = v, p, q
    return (r,g,b,a)


##########################################################################
# `Color` class.
##########################################################################
class Color:
    """Represents a color and provides means of automatic conversion between
    HSV(A) and RGB(A) color spaces. The color is stored in HSVA space."""
    def __init__(self):
        self.hsva = (0.0, 0.0, 0.5, 1.0)

    def set_rgb(self,r,g,b):
        self.set_rgba(r,g,b,1.0)

    def set_rgba(self,r,g,b,a):
        self.hsva = rgba_to_hsva(r,g,b,a)

    def get_rgb255(self):
        """returns a tuple (r,g,b) of 3 integers in range [0..255] representing
        the color."""
        rgba = self.get_rgba()
        return (int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255) )

    def get_rgba(self):
        h,s,v,a = self.hsva
        return hsva_to_rgba(h,s,v,a)

    def get_hsva(self):
        return self.hsva

    def set_hsva(self,h,s,v,a):
        self.hsva = (h,s,v,a)

    def set_lerp(self, f,A,B):
        """Set self to result of linear interpolation between colors A and
           B in HSVA space.

           The weight f is from [0..1], with f=0 giving A and f=1 giving
           color B."""
        h = lerp(A.hsva[0], B.hsva[0], f)
        s = lerp(A.hsva[1], B.hsva[1], f)
        v = lerp(A.hsva[2], B.hsva[2], f)
        a = lerp(A.hsva[3], B.hsva[3], f)
        self.hsva = (h,s,v,a)


##########################################################################
# `ColorControlPoint` class.
##########################################################################
class ColorControlPoint:
    """A control point represents a fixed position in the gradient
    and its assigned color. A control point can have indifferent
    color channels in hsv space, i.e. channels, on which its
    presence does not impose any effect."""
    def __init__(self, active_channels, fixed=False):
        self.color = Color()
        # position in the gradient table. range: [0..1].
        self.pos = 0.0
        # fixed control points can not be moved to other positions. The
        # control points for the begin and the end of the gradient are usually
        # the only fixed control points.
        self.fixed = fixed

        if ( 'a' != active_channels ):
            self.active_channels = "rgb"
            self.activate_channels(active_channels)
        else:
            self.active_channels = "a"

    def activate_channels(self,new_channels):
        """NewChannels: string consisting of the new color channel names"""
        for c in new_channels:
            if ( not ( c in self.active_channels ) ):
                self.active_channels += c

    def set_pos(self,f):
        self.pos = max(min(f,1.0), 0.0)

##########################################################################
# `GradientTableOld` class.
##########################################################################
class GradientTableOld:
    """this class represents a logical gradient table, i.e. an array
    of colors and the means to control it via control points"""

    def __init__( self, num_entries ):
        self.size = num_entries
        self.table = [[0.0]*self.size, [0.0]*self.size,
                      [0.0]*self.size, [0.0]*self.size]
        self.table_hsva = [[0.0]*self.size, [0.0]*self.size,
                           [0.0]*self.size, [0.0]*self.size]
        # ^- table[channel][index]: rgba values of the colors of the table.
        # range: [0..1]^4.

        # insert the control points for the left and the right end of the
        # gradient. These are fixed (i.e. cannot be moved or deleted) and
        # allow one to set begin and end colors.
        left_control_point = ColorControlPoint(fixed=True, active_channels="hsva")
        left_control_point.set_pos(0.0)
        left_control_point.color.set_rgb(0.0, 0.0, 0.0)
        right_control_point = ColorControlPoint(fixed=True, active_channels="hsva")
        right_control_point.set_pos(1.0)
        right_control_point.color.set_rgb(1.0, 1.0, 1.0)
        self.control_points = [left_control_point, right_control_point]
        # note: The array of control points always has to be sorted by gradient
        # position of the control points.

        # insert another control point. This one has no real function, it
        # is just there to make the gradient editor more colorful initially
        # and suggest to the (first time user) that it is actually possible to
        # place more control points.
        mid_control_point = ColorControlPoint(active_channels="hsv")
        mid_control_point.set_pos(0.4)
        mid_control_point.color.set_rgb(1.0,0.4,0.0)
        self.insert_control_point( mid_control_point )

        # it is possible to scale the output gradient using a nonlinear function
        # which maps [0..1] to [0..1], aviable using the "nonlin" option in the
        # gui. Per default, this option is disabled however.
        self.scaling_function_string = ""  # will receive the function string if
                                           # set, e.g. "x**(4*a)"

        self.scaling_function_parameter = 0.5 # the parameter a, slider controlled
        self.scaling_function = None      # the actual function object. takes one
                                          # position parameter. None if disabled.

        self.update()

    def get_color_hsva(self,idx):
        """return (h,s,v,a) tuple in self.table_hsva for index idx"""
        return (self.table_hsva[0][idx],self.table_hsva[1][idx],
                self.table_hsva[2][idx],self.table_hsva[3][idx])

    def get_color(self,idx):
        """return (r,g,b,a) tuple in self.table for index idx"""
        return (self.table[0][idx],self.table[1][idx],
                self.table[2][idx],self.table[3][idx])

    def set_color_hsva(self,idx,hsva_color):
        """set hsva table entry for index idx to hsva_color, which must be
        (h,s,v,a)"""
        self.table_hsva[0][idx] = hsva_color[0]
        self.table_hsva[1][idx] = hsva_color[1]
        self.table_hsva[2][idx] = hsva_color[2]
        self.table_hsva[3][idx] = hsva_color[3]

    def set_color(self,idx,rgba_color):
        """set rgba table entry for index idx to rgba_color, which must be
        (r,g,b,a)"""
        self.table[0][idx] = rgba_color[0]
        self.table[1][idx] = rgba_color[1]
        self.table[2][idx] = rgba_color[2]
        self.table[3][idx] = rgba_color[3]

    def get_pos_index(self,f):
        """return index in .table of gradient position f \in [0..1]"""
        return int(f*(self.size-1))

    def get_index_pos(self,idx):
        """return position f \in [0..1] of gradient table index idx"""
        return (1.0*idx)/(self.size-1)

    def get_pos_color(self,f):
        """return a Color object representing the color which is lies at
        position f \in [0..1] in the current gradient"""
        result = Color()
        #e = self.table_hsva[:,self.get_pos_index(f)]
        e = self.get_color_hsva(self.get_pos_index(f))
        result.set_hsva(e[0], e[1], e[2], e[3])
        return result

    def get_pos_rgba_color_lerped(self,f):
        """return a (r,g,b,a) color representing the color which is lies at
        position f \in [0..1] in the current gradient. if f is outside the
        [0..1] interval, the result will be clamped to this interval"""
        scaled_pos = max(min(f,1.0), 0.0)*(self.size-1)
        idx0 = int(scaled_pos)
        fraction = scaled_pos - idx0
        idx1 = min( self.size - 1, 1 + idx0 )
        r = lerp( self.table[0][idx0], self.table[0][idx1], fraction )
        g = lerp( self.table[1][idx0], self.table[1][idx1], fraction )
        b = lerp( self.table[2][idx0], self.table[2][idx1], fraction )
        a = lerp( self.table[3][idx0], self.table[3][idx1], fraction )
        return (r,g,b,a)

    def insert_control_point(self,new_point):
        """Insert a new control point into the table. Does sort the control
        points, but does NOT update the table."""
        self.control_points += [new_point]
        self.sort_control_points()

    def sort_control_points(self):
        """Sort control points by position. Call this if the position of
        any control point was changed externally. The control point array
        always has to be sorted."""
        def pred(x, y):
            if x < y:
                return -1
            elif y < x:
                return +1
            else:
                return 0
        self.control_points.sort( lambda x, y: pred(x.pos, y.pos) )

    def update(self):
        """Recalculate the gradient table from the control points. The colors
        are interpolated linearly between each two control points in hsva space.
        """
        #self.Sortcontrol_points()
        control_point_indices_total = []
        for point in self.control_points:
            control_point_indices_total.append((self.get_pos_index(point.pos),point))

        # first, recalculate the Hsva table channel-wise from the control points
        for it in [("h",0),("s",1),("v",2),("a",3)]:
            # take into account only control points which are active
            # for the current channel
            control_point_indices = filter( \
                lambda x: it[0] in x[1].active_channels,
                control_point_indices_total )
            assert( len( control_point_indices ) >= 2 )

            # we always interpolate between two adjacent control points on the
            # current channel. NextIntervalBeginIdx marks the first table index
            # on which the next set of control points is to be choosen.
            start_point_id = -1
            end_point_id = 0
            start_pos = 0 #dummy value
            end_pos = 0 #dummy value
            next_interval_begin_idx = 0
            end_point = control_point_indices[0][1]
            assert( next_interval_begin_idx == 0 )
            for k in range(self.size):
                while( k == next_interval_begin_idx ):
                    # ^-- this loop makes sure that we won't attempt to
                    # interpolate between two control points that lie on
                    # each other. read "if" instead of "while".
                    start_point_id += 1
                    end_point_id += 1
                    start_point = end_point
                    start_pos = end_pos
                    end_point = control_point_indices[end_point_id][1]
                    end_pos = end_point.pos
                    next_interval_begin_idx = 1+control_point_indices[end_point_id][0]

                # calculate float position of this entry in the gradient table
                # and (linear) position in the current gradient between the
                # two current control points
                cur_pos = self.get_index_pos(k)
                f = ( cur_pos - start_pos ) / ( end_pos - start_pos )
                assert( ( 0 <= f ) and ( f <= 1 ) )
                # ^-- this might happen when two control points lie on each
                # other. Since this case only occurs as an intermediate case
                # when dragging it is not really problematic.
                #f = min( 1.0, max( 0.0, f ) )

                self.table_hsva[it[1]][k] = lerp(start_point.color.hsva[it[1]],
                        end_point.color.hsva[it[1]], f)
            assert( next_interval_begin_idx == self.size )
        # convert hsva colors to rgba
        for k in range(self.size):
            h,s,v,a = self.get_color_hsva(k)
            self.set_color(k, hsva_to_rgba(h, s, v, a))

    def store_to_vtk_lookup_table(self, vtk_table, num_entries=256):
        """Store current color table in `vtk_table`, an instance of
        `tvtk.LookupTable`.
        """
        vtk_table.number_of_table_values = num_entries
        scale_xform = lambda x:x
        if self.scaling_function:
            scale_xform = self.scaling_function
        for idx in range(num_entries):
            f = scale_xform(float(idx)/(num_entries-1))
            rgba = self.get_pos_rgba_color_lerped(f)
            vtk_table.set_table_value( idx, rgba )

    def store_to_vtk_volume_prop(self, volume_prop, scalar_range):
        """Given a `tvtk.VolumeProperty` and a scalar range to map
        values into, this sets the CTF based on the current control
        points.
        """
        # FIXME: This method does not support scaling!
        ctf = volume_prop.rgb_transfer_function
        ctf.remove_all_points()
        otf = volume_prop.get_scalar_opacity()
        otf.remove_all_points()
        s1, s2 = scalar_range
        size = s2 - s1
        for point in self.control_points:
            x = s1 + point.pos*size
            h, s, v, a = point.color.get_hsva()
            if point.active_channels != 'a':
                ctf.add_hsv_point(x, h, s, v)
            if 'a' in point.active_channels:
                otf.add_point(x, a)

    def load_from_vtk_volume_prop(self, volume_prop):
        """Given a vtkVolumeProperty, this initializes the control
        points of the gradient table.  This works best when a
        ctf.ColorTransferFunction and PiecewiseFunction are used.

        Note that it is not as easy to setup the control points from a
        LUT because the LUT may end up having more than the size of
        the table editor here.  It also usually does not make sense to
        do this with a LUT.
        """
        # FIXME: This method does not support scaling!
        ctf = volume_prop.rgb_transfer_function
        otf = volume_prop.get_scalar_opacity()
        # We need a CTF with at least 2 points.
        size = ctf.size
        assert (size > 1)
        assert (otf.size > 1)
        s1, s2 = ctf.range
        scale = float(s2 - s1)
        ds = scale/(size -1)
        new_ctl_pts = []
        has_nodes = False
        if hasattr(ctf, 'nodes'):
            has_nodes = True
        for i in range(size):
            if has_nodes:
                x = ctf.nodes[i]
            else:
                x = s1 + i*ds
            r, g, b = ctf.get_color(x)
            a = otf.get_value(x)
            if (i == 0) or (i == (size-1)):
                # First and last points are fixed.
                pt = ColorControlPoint(active_channels="hsva", fixed=True)
            else:
                pt = ColorControlPoint(active_channels="hsv", fixed=False)

            pt.color.set_rgba(r, g, b, a)
            pos = (x - s1)/scale
            pt.set_pos(pos)
            new_ctl_pts.append(pt)

        # The alpha values are indipendent of the hsv ones.
        size = otf.size
        ds = scale/(size -1)
        has_nodes = False
        if hasattr(ctf, 'nodes'):
            has_nodes = True
        for i in range(1, size-1):
            if has_nodes:
                x = otf.nodes[i]
            else:
                x = s1 + i*ds
            a = otf.get_value(x)
            r, g, b = ctf.get_color(x)
            pt = ColorControlPoint(active_channels="a", fixed=False)
            pt.color.set_rgba(r, g, b, a)
            pos = (x - s1)/scale
            pt.set_pos(pos)
            new_ctl_pts.append(pt)

        self.control_points = new_ctl_pts
        self.sort_control_points()
        self.update()

    def scaling_parameters_changed(self):
        """Recompile the scaling function."""
        from math import tan, atan, cos, acos, sin, asin, pow, log, exp, e, pi
        self.scaling_function = None

        # let python generate a new function via the exec statement. to make
        # the security risk calculable, we execute that function in a local
        # scope. The downside is that we have to provide math functions
        # one at a time.
        def_string = "def ParamFn(x): return %s " % (self.scaling_function_string)
        dict = {"a":self.scaling_function_parameter, "ParamFn":None,
            "atan":atan, "tan":tan, "cos":cos, "acos":acos,
            "sin":sin, "asin":asin, "pow":pow, "log":log, "exp":exp, "e":e,
            "pi":pi }
        if ( "" == self.scaling_function_string ):
            return
        try:
            exec def_string in dict
            self.scaling_function = dict["ParamFn"]
        except:
            raise ValueError("failed to compile function: ", def_string )

    def set_scaling_function_parameter(self,new_parameter):
        """Set the 'a' parameter of the scaling function"""
        self.scaling_function_parameter = new_parameter
        self.scaling_parameters_changed()

    def set_scaling_function(self,new_function_string):
        """Set scaling function. new_function_string is a string describing the
        function, e.g. 'x**(4*a)' """
        self.scaling_function_string = new_function_string
        self.scaling_parameters_changed()

    def save(self, file_name):
        """Save control point set into a new file FileName. It is not checked
        whether the file already exists. Further writes out a VTK .lut file
        and a .jpg file showing the gradients."""

        # Ensure that if the input file name had one of the extensions
        # we'll be writing out ourselves, it gets stripped out first.
        path_base,ext = splitext(file_name)
        #print(file_name)
        if ext.lower() in ['.lut','.jpg','.jpeg','.grad']:
            ext = ''
        file_name = path_base  + ext

        # Create the three names for the files we'll be actually
        # writing out.
        file_name_grad = file_name + '.grad'
        file_name_lut = file_name + '.lut'
        file_name_jpg = file_name + '.jpg'

        # write control points set.
        file = open( file_name_grad, "w" )
        file.write( "V 2.0 Color Gradient File\n" )
        file.write( "ScalingFunction: %s\n" % (self.scaling_function_string) )
        file.write( "ScalingParameter: %s\n" % (self.scaling_function_parameter) )
        file.write( "ControlPoints: (pos fixed bindings h s v a)\n" )
        for control_point in self.control_points:
            file.write( "  %s %s %s %s %s %s %s\n" % ( \
                control_point.pos, control_point.fixed, control_point.active_channels,
                control_point.color.get_hsva()[0], control_point.color.get_hsva()[1],
                control_point.color.get_hsva()[2], control_point.color.get_hsva()[3] ) )
        file.close()

        # write vtk lookup table. Unfortunatelly these objects don't seem to
        # have any built in and exposed means of loading or saving them, so
        # we build the vtk file directly
        vtk_table = tvtk.LookupTable()
        self.store_to_vtk_lookup_table(vtk_table)
        file = open( file_name_lut, "w" )
        num_colors = vtk_table.number_of_table_values
        file.write( "LOOKUP_TABLE UnnamedTable %s\n" % ( num_colors ) )
        for idx in range(num_colors):
            entry = vtk_table.get_table_value(idx)
            file.write("%.4f %.4f %.4f %.4f\n" % (entry[0],entry[1],entry[2],entry[3]))
        file.close()

        # if the python image library is aviable, also generate a small .jpg
        # file showing how the gradient looks. Based on code from Arnd Baecker.
        try:
            import Image
        except ImportError:
            pass  # we're ready otherwise. no jpg output tho.
        else:
            Ny=64  # vertical size of the jpeg
            im = Image.new("RGBA",(num_colors,Ny))
            for nx in range(num_colors):
                (r,g,b,a) = vtk_table.get_table_value(nx)
                for ny in range(Ny):
                    im.putpixel((nx,ny),(int(255*r),int(255*g),int(255*b),
                                         int(255*a)))
            im.save(file_name_jpg,"JPEG")
            # it might be better to store the gradient as .png file, as these
            # are actually able to store alpha components (unlike jpg files)
            # and might also lead to a better compression.

    def load(self, file_name):
        """Load control point set from file FileName and recalculate gradient
        table."""
        file = open( file_name, "r" )
        version_tag = file.readline()
        version = float(version_tag.split()[1])+1e-5
        if ( version >= 1.1 ):
            # read in the scaling function and the scaling function parameter
            function_line_split = file.readline().split()
            parameter_line = file.readline()
            if ( len(function_line_split)==2 ):
                self.scaling_function_string = function_line_split[1]
            else:
                self.scaling_function_string = ""
            self.scaling_function_parameter = float(parameter_line.split()[1])
        else:
            self.scaling_function_string = ""
            self.scaling_function_parameter = 0.5
        file.readline()
        new_control_points = []
        while True:
            cur_line = file.readline()
            if len(cur_line) == 0:
                # readline is supposed to return an empty string at EOF
                break
            args = cur_line.split()
            if ( len(args) < 7 ):
                msg = "gradient file format broken at line:\n"
                msg += cur_line
                raise ValueError(msg)
            new_point = ColorControlPoint(active_channels="")
            new_point.set_pos( float( args[0] ) )
            new_point.fixed = "True" == args[1] #bool( args[1] )
            new_point.active_channels = args[2]
            (h,s,v,a) = ( float(args[3]), float(args[4]),
                          float(args[5]), float(args[6]) )
            new_point.color.set_hsva(h,s,v,a)
            new_control_points.append(new_point)
        file.close()
        self.control_points = new_control_points
        self.sort_control_points()
        self.scaling_parameters_changed()
        self.update()


##########################################################################
# `GradientTable` class.
##########################################################################
class GradientTable:
    """this class represents a logical gradient table, i.e. an array
    of colors and the means to control it via control points

    This class (unlike the GradientTableOld) does not support scaling
    and uses VTK's ColorTransferFunction and PiecewiseFunction to
    perform the actual interpolation.
    """

    def __init__( self, num_entries ):
        self.size = num_entries
        self.table = tvtk.ColorTransferFunction()
        try:
            self.table.range = (0.0, 1.0)
        except Exception:
            # VTK versions < 5.2 don't seem to need this.
            pass

        self.alpha = tvtk.PiecewiseFunction()
        # These VTK classes perform the interpolation for us.

        # insert the control points for the left and the right end of the
        # gradient. These are fixed (i.e. cannot be moved or deleted) and
        # allow one to set begin and end colors.
        left_control_point = ColorControlPoint(fixed=True, active_channels="hsva")
        left_control_point.set_pos(0.0)
        left_control_point.color.set_rgb(0.0, 0.0, 0.0)
        right_control_point = ColorControlPoint(fixed=True, active_channels="hsva")
        right_control_point.set_pos(1.0)
        right_control_point.color.set_rgb(1.0, 1.0, 1.0)
        self.control_points = [left_control_point, right_control_point]
        # note: The array of control points always has to be sorted by gradient
        # position of the control points.

        # insert another control point. This one has no real function, it
        # is just there to make the gradient editor more colorful initially
        # and suggest to the (first time user) that it is actually possible to
        # place more control points.
        mid_control_point = ColorControlPoint(active_channels="hsv")
        mid_control_point.set_pos(0.4)
        mid_control_point.color.set_rgb(1.0,0.4,0.0)
        self.insert_control_point( mid_control_point )

        # These variables are only for compatibility with GradientTableOld.
        self.scaling_function_string = ""  # will receive the function string if
                                           # set, e.g. "x**(4*a)"

        self.scaling_function_parameter = 0.5 # the parameter a, slider controlled
        self.scaling_function = None      # the actual function object. takes one
                                          # position parameter. None if disabled.

        self.update()

    def get_color_hsva(self, f):
        """return (h,s,v,a) tuple in self.table_hsva for fraction f in
        [0,1]."""
        r, g, b = self.table.get_color(f)
        a = self.alpha.get_value(f)
        return rgba_to_hsva(r, g, b, a)

    def get_color(self, f):
        """return (r,g,b,a) tuple in self.table for fraction f in
        [0,1]."""
        r, g, b = self.table.get_color(f)
        a = self.alpha.get_value(f)
        return r, g, b, a

    def get_pos_color(self,f):
        """return a Color object representing the color which is lies at
        position f \in [0..1] in the current gradient"""
        result = Color()
        e = self.get_color_hsva(f)
        result.set_hsva(*e)
        return result

    def get_pos_rgba_color_lerped(self,f):
        """return a (r,g,b,a) color representing the color which is lies at
        position f \in [0..1] in the current gradient. if f is outside the
        [0..1] interval, the result will be clamped to this
        interval."""
        return self.get_color(f)

    def insert_control_point(self,new_point):
        """Insert a new control point into the table. Does sort the control
        points, but does NOT update the table."""
        self.control_points += [new_point]
        self.sort_control_points()

    def sort_control_points(self):
        """Sort control points by position. Call this if the position of
        any control point was changed externally. The control point array
        always has to be sorted."""
        def pred(x, y):
            if x < y:
                return -1
            elif y < x:
                return +1
            else:
                return 0
        self.control_points.sort( lambda x, y: pred(x.pos, y.pos) )

    def update(self):
        """Recalculate the gradient table from the control points. The
        colors are interpolated linearly between each two control
        points in hsva space.
        """
        #self.sort_control_points()

        table = self.table
        alpha = self.alpha
        table.remove_all_points()
        alpha.remove_all_points()
        for point in self.control_points:
            x = point.pos
            h, s, v, a = point.color.get_hsva()
            if point.active_channels != 'a':
                table.add_hsv_point(x, h, s, v)
            if 'a' in point.active_channels:
                alpha.add_point(x, a)

    def store_to_vtk_lookup_table(self, vtk_table, num_entries=256):
        """Store current color table in `vtk_table`, an instance of
        `tvtk.LookupTable`.
        """
        vtk_table.number_of_table_values = num_entries
        for idx in range(num_entries):
            f = float(idx)/(num_entries-1)
            rgba = self.get_color(f)
            vtk_table.set_table_value( idx, rgba )

    def store_to_vtk_volume_prop(self, volume_prop, scalar_range):
        """Given a `tvtk.VolumeProperty` and a scalar range to map
        values into, this sets the CTF based on the current control
        points.
        """
        # FIXME: This method does not support scaling!
        ctf = volume_prop.rgb_transfer_function
        ctf.remove_all_points()
        otf = volume_prop.get_scalar_opacity()
        otf.remove_all_points()
        s1, s2 = scalar_range
        try:
            ctf.range = s1, s2
        except Exception:
            # VTK versions < 5.2 don't seem to need this.
            pass
        size = s2 - s1
        for point in self.control_points:
            x = s1 + point.pos*size
            h, s, v, a = point.color.get_hsva()
            if point.active_channels != 'a':
                ctf.add_hsv_point(x, h, s, v)
            if 'a' in point.active_channels:
                otf.add_point(x, a)

    def load_from_vtk_volume_prop(self, volume_prop):
        """Given a vtkVolumeProperty, this initializes the control
        points of the gradient table.  This works best when a
        ctf.ColorTransferFunction and PiecewiseFunction are used.

        Note that it is not as easy to setup the control points from a
        LUT because the LUT may end up having more than the size of
        the table editor here.  It also usually does not make sense to
        do this with a LUT.
        """
        # FIXME: This method does not support scaling!
        ctf = volume_prop.rgb_transfer_function
        otf = volume_prop.get_scalar_opacity()
        # We need a CTF with at least 2 points.
        size = ctf.size
        assert (size > 1)
        assert (otf.size > 1)
        s1, s2 = ctf.range
        scale = float(s2 - s1)
        ds = scale/(size -1)
        new_ctl_pts = []
        has_nodes = False
        if hasattr(ctf, 'nodes'):
            has_nodes = True
        for i in range(size):
            if has_nodes:
                x = ctf.nodes[i]
            else:
                x = s1 + i*ds
            r, g, b = ctf.get_color(x)
            a = otf.get_value(x)
            if (i == 0) or (i == (size-1)):
                # First and last points are fixed.
                pt = ColorControlPoint(active_channels="hsva", fixed=True)
            else:
                pt = ColorControlPoint(active_channels="hsv", fixed=False)

            pt.color.set_rgba(r, g, b, a)
            pos = (x - s1)/scale
            pt.set_pos(pos)
            new_ctl_pts.append(pt)

        # The alpha values are indipendent of the hsv ones.
        size = otf.size
        ds = scale/(size -1)
        has_nodes = False
        if hasattr(ctf, 'nodes'):
            has_nodes = True
        for i in range(1, size-1):
            if has_nodes:
                x = otf.nodes[i]
            else:
                x = s1 + i*ds
            a = otf.get_value(x)
            r, g, b = ctf.get_color(x)
            pt = ColorControlPoint(active_channels="a", fixed=False)
            pt.color.set_rgba(r, g, b, a)
            pos = (x - s1)/scale
            pt.set_pos(pos)
            new_ctl_pts.append(pt)

        self.control_points = new_ctl_pts
        self.sort_control_points()
        self.update()

    def scaling_parameters_changed(self):
        """Recompile the scaling function."""
        raise NotImplementedError

    def set_scaling_function_parameter(self,new_parameter):
        """Set the 'a' parameter of the scaling function"""
        raise NotImplementedError

    def set_scaling_function(self,new_function_string):
        """Set scaling function. new_function_string is a string describing the
        function, e.g. 'x**(4*a)' """
        raise NotImplementedError

    def save(self, file_name):
        """Save control point set into a new file FileName. It is not checked
        whether the file already exists. Further writes out a VTK .lut file
        and a .jpg file showing the gradients."""

        # Ensure that if the input file name had one of the extensions
        # we'll be writing out ourselves, it gets stripped out first.
        path_base,ext = splitext(file_name)
        #print(file_name)
        if ext.lower() in ['.lut','.jpg','.jpeg','.grad']:
            ext = ''
        file_name = path_base  + ext

        # Create the three names for the files we'll be actually
        # writing out.
        file_name_grad = file_name + '.grad'
        file_name_lut = file_name + '.lut'
        file_name_jpg = file_name + '.jpg'

        # write control points set.
        file = open( file_name_grad, "w" )
        file.write( "V 2.0 Color Gradient File\n" )
        file.write( "ScalingFunction: %s\n" % (self.scaling_function_string) )
        file.write( "ScalingParameter: %s\n" % (self.scaling_function_parameter) )
        file.write( "ControlPoints: (pos fixed bindings h s v a)\n" )
        for control_point in self.control_points:
            file.write( "  %s %s %s %s %s %s %s\n" % ( \
                control_point.pos, control_point.fixed, control_point.active_channels,
                control_point.color.get_hsva()[0], control_point.color.get_hsva()[1],
                control_point.color.get_hsva()[2], control_point.color.get_hsva()[3] ) )
        file.close()

        # write vtk lookup table. Unfortunatelly these objects don't seem to
        # have any built in and exposed means of loading or saving them, so
        # we build the vtk file directly
        vtk_table = tvtk.LookupTable()
        self.store_to_vtk_lookup_table(vtk_table)
        file = open( file_name_lut, "w" )
        num_colors = vtk_table.number_of_table_values
        file.write( "LOOKUP_TABLE UnnamedTable %s\n" % ( num_colors ) )
        for idx in range(num_colors):
            entry = vtk_table.get_table_value(idx)
            file.write("%.4f %.4f %.4f %.4f\n" % (entry[0],entry[1],entry[2],entry[3]))
        file.close()

        # if the python image library is aviable, also generate a small .jpg
        # file showing how the gradient looks. Based on code from Arnd Baecker.
        try:
            import Image
        except ImportError:
            pass  # we're ready otherwise. no jpg output tho.
        else:
            Ny=64  # vertical size of the jpeg
            im = Image.new("RGBA",(num_colors,Ny))
            for nx in range(num_colors):
                (r,g,b,a) = vtk_table.get_table_value(nx)
                for ny in range(Ny):
                    im.putpixel((nx,ny),(int(255*r),int(255*g),int(255*b),
                                         int(255*a)))
            im.save(file_name_jpg,"JPEG")
            # it might be better to store the gradient as .png file, as these
            # are actually able to store alpha components (unlike jpg files)
            # and might also lead to a better compression.

    def load(self, file_name):
        """Load control point set from file FileName and recalculate gradient
        table."""
        file = open( file_name, "r" )
        version_tag = file.readline()
        version = float(version_tag.split()[1])+1e-5
        if ( version >= 1.1 ):
            # read in the scaling function and the scaling function parameter
            function_line_split = file.readline().split()
            parameter_line = file.readline()
            if ( len(function_line_split)==2 ):
                self.scaling_function_string = function_line_split[1]
            else:
                self.scaling_function_string = ""
            self.scaling_function_parameter = float(parameter_line.split()[1])
        else:
            self.scaling_function_string = ""
            self.scaling_function_parameter = 0.5
        file.readline()
        new_control_points = []
        while True:
            cur_line = file.readline()
            if len(cur_line) == 0:
                # readline is supposed to return an empty string at EOF
                break
            args = cur_line.split()
            if ( len(args) < 7 ):
                msg = "gradient file format broken at line:\n"
                msg += cur_line
                raise ValueError(msg)
            new_point = ColorControlPoint(active_channels="")
            new_point.set_pos( float( args[0] ) )
            new_point.fixed = "True" == args[1] #bool( args[1] )
            new_point.active_channels = args[2]
            (h,s,v,a) = ( float(args[3]), float(args[4]),
                          float(args[5]), float(args[6]) )
            new_point.color.set_hsva(h,s,v,a)
            new_control_points.append(new_point)
        file.close()
        self.control_points = new_control_points
        self.sort_control_points()
        #self.scaling_parameters_changed()
        self.update()
