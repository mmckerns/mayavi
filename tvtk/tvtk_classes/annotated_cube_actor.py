# Automatically generated code: EDIT AT YOUR OWN RISK
from traits import api as traits
from traitsui import api as traitsui

from tvtk import vtk_module as vtk
from tvtk import tvtk_base
from tvtk.tvtk_base_handler import TVTKBaseHandler
from tvtk import messenger
from tvtk.tvtk_base import deref_vtk
from tvtk import array_handler
from tvtk.array_handler import deref_array
from tvtk.tvtk_classes.tvtk_helper import wrap_vtk

from tvtk.tvtk_classes.prop3d import Prop3D


class AnnotatedCubeActor(Prop3D):
    """
    AnnotatedCubeActor - a 3d cube with face labels
    
    Superclass: Prop3D
    
    AnnotatedCubeActor is a hybrid 3d actor used to represent an
    anatomical orientation marker in a scene.  The class consists of a 3d
    unit cube centered on the origin with each face labelled in
    correspondance to a particular coordinate direction.  For example,
    with Cartesian directions, the user defined text labels could be: +X,
    -X, +Y, -Y, +Z, -Z, while for anatomical directions: A, P, L, R, S,
    I.  Text is automatically centered on each cube face and is not
    restriceted to single characters. In addition to or in replace of a
    solid text label representation, the outline edges of the labels can
    be displayed.  The individual properties of the cube, face labels and
    text outlines can be manipulated as can their visibility.
    
    Caveats:
    
    AnnotatedCubeActor is primarily intended for use with
    OrientationMarkerWidget. The cube face text is generated by
    VectorText and therefore the font attributes are restricted.
    
    See Also:
    
    AxesActor OrientationMarkerWidget VectorText
    
    """
    def __init__(self, obj=None, update=True, **traits):
        tvtk_base.TVTKBase.__init__(self, vtk.vtkAnnotatedCubeActor, obj, update, **traits)
    
    z_face_text_rotation = traits.Float(0.0, enter_set=True, auto_set=False, help=\
        """
        Augment individual face text orientations.
        """
    )
    def _z_face_text_rotation_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetZFaceTextRotation,
                        self.z_face_text_rotation)

    x_minus_face_text = traits.String(r"X-", enter_set=True, auto_set=False, help=\
        """
        Set/get the face text.
        """
    )
    def _x_minus_face_text_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetXMinusFaceText,
                        self.x_minus_face_text)

    y_plus_face_text = traits.String(r"Y+", enter_set=True, auto_set=False, help=\
        """
        Set/get the face text.
        """
    )
    def _y_plus_face_text_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetYPlusFaceText,
                        self.y_plus_face_text)

    face_text_visibility = traits.Int(1, enter_set=True, auto_set=False, help=\
        """
        Enable/disable drawing the vector text.
        """
    )
    def _face_text_visibility_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetFaceTextVisibility,
                        self.face_text_visibility)

    text_edges_visibility = traits.Int(1, enter_set=True, auto_set=False, help=\
        """
        Enable/disable drawing the vector text edges.
        """
    )
    def _text_edges_visibility_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetTextEdgesVisibility,
                        self.text_edges_visibility)

    y_face_text_rotation = traits.Float(0.0, enter_set=True, auto_set=False, help=\
        """
        Augment individual face text orientations.
        """
    )
    def _y_face_text_rotation_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetYFaceTextRotation,
                        self.y_face_text_rotation)

    z_minus_face_text = traits.String(r"Z-", enter_set=True, auto_set=False, help=\
        """
        Set/get the face text.
        """
    )
    def _z_minus_face_text_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetZMinusFaceText,
                        self.z_minus_face_text)

    x_plus_face_text = traits.String(r"X+", enter_set=True, auto_set=False, help=\
        """
        Set/get the face text.
        """
    )
    def _x_plus_face_text_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetXPlusFaceText,
                        self.x_plus_face_text)

    face_text_scale = traits.Float(0.5, enter_set=True, auto_set=False, help=\
        """
        Set/Get the scale factor for the face text
        """
    )
    def _face_text_scale_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetFaceTextScale,
                        self.face_text_scale)

    x_face_text_rotation = traits.Float(0.0, enter_set=True, auto_set=False, help=\
        """
        Augment individual face text orientations.
        """
    )
    def _x_face_text_rotation_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetXFaceTextRotation,
                        self.x_face_text_rotation)

    cube_visibility = traits.Int(1, enter_set=True, auto_set=False, help=\
        """
        Enable/disable drawing the cube.
        """
    )
    def _cube_visibility_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetCubeVisibility,
                        self.cube_visibility)

    y_minus_face_text = traits.String(r"Y-", enter_set=True, auto_set=False, help=\
        """
        Set/get the face text.
        """
    )
    def _y_minus_face_text_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetYMinusFaceText,
                        self.y_minus_face_text)

    z_plus_face_text = traits.String(r"Z+", enter_set=True, auto_set=False, help=\
        """
        Set/get the face text.
        """
    )
    def _z_plus_face_text_changed(self, old_val, new_val):
        self._do_change(self._vtk_obj.SetZPlusFaceText,
                        self.z_plus_face_text)

    def _get_assembly(self):
        return wrap_vtk(self._vtk_obj.GetAssembly())
    assembly = traits.Property(_get_assembly, help=\
        """
        Get the assembly so that user supplied transforms can be applied
        """
    )

    def _get_cube_property(self):
        return wrap_vtk(self._vtk_obj.GetCubeProperty())
    cube_property = traits.Property(_get_cube_property, help=\
        """
        Get the cube properties.
        """
    )

    def _get_text_edges_property(self):
        return wrap_vtk(self._vtk_obj.GetTextEdgesProperty())
    text_edges_property = traits.Property(_get_text_edges_property, help=\
        """
        Get the text edges properties.
        """
    )

    def _get_x_minus_face_property(self):
        return wrap_vtk(self._vtk_obj.GetXMinusFaceProperty())
    x_minus_face_property = traits.Property(_get_x_minus_face_property, help=\
        """
        Get the individual face text properties.
        """
    )

    def _get_x_plus_face_property(self):
        return wrap_vtk(self._vtk_obj.GetXPlusFaceProperty())
    x_plus_face_property = traits.Property(_get_x_plus_face_property, help=\
        """
        Get the individual face text properties.
        """
    )

    def _get_y_minus_face_property(self):
        return wrap_vtk(self._vtk_obj.GetYMinusFaceProperty())
    y_minus_face_property = traits.Property(_get_y_minus_face_property, help=\
        """
        Get the individual face text properties.
        """
    )

    def _get_y_plus_face_property(self):
        return wrap_vtk(self._vtk_obj.GetYPlusFaceProperty())
    y_plus_face_property = traits.Property(_get_y_plus_face_property, help=\
        """
        Get the individual face text properties.
        """
    )

    def _get_z_minus_face_property(self):
        return wrap_vtk(self._vtk_obj.GetZMinusFaceProperty())
    z_minus_face_property = traits.Property(_get_z_minus_face_property, help=\
        """
        Get the individual face text properties.
        """
    )

    def _get_z_plus_face_property(self):
        return wrap_vtk(self._vtk_obj.GetZPlusFaceProperty())
    z_plus_face_property = traits.Property(_get_z_plus_face_property, help=\
        """
        Get the individual face text properties.
        """
    )

    _updateable_traits_ = \
    (('origin', 'GetOrigin'), ('z_face_text_rotation',
    'GetZFaceTextRotation'), ('allocated_render_time',
    'GetAllocatedRenderTime'), ('cube_visibility', 'GetCubeVisibility'),
    ('dragable', 'GetDragable'), ('visibility', 'GetVisibility'),
    ('z_minus_face_text', 'GetZMinusFaceText'), ('face_text_visibility',
    'GetFaceTextVisibility'), ('z_plus_face_text', 'GetZPlusFaceText'),
    ('render_time_multiplier', 'GetRenderTimeMultiplier'),
    ('text_edges_visibility', 'GetTextEdgesVisibility'), ('use_bounds',
    'GetUseBounds'), ('orientation', 'GetOrientation'), ('scale',
    'GetScale'), ('global_warning_display', 'GetGlobalWarningDisplay'),
    ('estimated_render_time', 'GetEstimatedRenderTime'),
    ('y_face_text_rotation', 'GetYFaceTextRotation'), ('debug',
    'GetDebug'), ('face_text_scale', 'GetFaceTextScale'),
    ('y_plus_face_text', 'GetYPlusFaceText'), ('x_plus_face_text',
    'GetXPlusFaceText'), ('reference_count', 'GetReferenceCount'),
    ('position', 'GetPosition'), ('x_minus_face_text',
    'GetXMinusFaceText'), ('y_minus_face_text', 'GetYMinusFaceText'),
    ('x_face_text_rotation', 'GetXFaceTextRotation'), ('pickable',
    'GetPickable'))
    
    _full_traitnames_list_ = \
    (['debug', 'dragable', 'global_warning_display', 'pickable',
    'use_bounds', 'visibility', 'allocated_render_time',
    'cube_visibility', 'estimated_render_time', 'face_text_scale',
    'face_text_visibility', 'orientation', 'origin', 'position',
    'render_time_multiplier', 'scale', 'text_edges_visibility',
    'x_face_text_rotation', 'x_minus_face_text', 'x_plus_face_text',
    'y_face_text_rotation', 'y_minus_face_text', 'y_plus_face_text',
    'z_face_text_rotation', 'z_minus_face_text', 'z_plus_face_text'])
    
    def trait_view(self, name=None, view_element=None):
        if view_element is not None or name not in (None, '', 'traits_view', 'full_traits_view', 'view'):
            return super(AnnotatedCubeActor, self).trait_view(name, view_element)
        if name == 'full_traits_view':
            full_traits_view = \
            traitsui.View((traitsui.Item("handler._full_traits_list",show_label=False)),
            title='Edit AnnotatedCubeActor properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return full_traits_view
        elif name == 'view':
            view = \
            traitsui.View((['use_bounds', 'visibility'], [],
            ['allocated_render_time', 'cube_visibility', 'estimated_render_time',
            'face_text_scale', 'face_text_visibility', 'orientation', 'origin',
            'position', 'render_time_multiplier', 'scale',
            'text_edges_visibility', 'x_face_text_rotation', 'x_minus_face_text',
            'x_plus_face_text', 'y_face_text_rotation', 'y_minus_face_text',
            'y_plus_face_text', 'z_face_text_rotation', 'z_minus_face_text',
            'z_plus_face_text']),
            title='Edit AnnotatedCubeActor properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return view
        elif name in (None, 'traits_view'):
            traits_view = \
            traitsui.View((traitsui.HGroup(traitsui.spring, "handler.view_type", show_border=True), 
            traitsui.Item("handler.info.object", editor = traitsui.InstanceEditor(view_name="handler.view"), style = "custom", show_label=False)),
            title='Edit AnnotatedCubeActor properties', scrollable=True, resizable=True,
            handler=TVTKBaseHandler,
            buttons=['OK', 'Cancel'])
            return traits_view
            
