import bpy
import os

from . import utilities_ui
from . import utilities_uv
from . import utilities_bake
from . import op_bake
from . import settings
from .settings import tt_settings

class op(bpy.types.Operator):
    bl_idname = "uv.textools_load_bakeset"
    bl_label = "Load bakeset from disk"
    bl_description = "Names bakeset after a texture file and loads related texture files"
    bl_options = {'REGISTER', 'UNDO'}

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        root, ext = os.path.splitext(self.filepath)
        dirname = os.path.dirname(root)
        filename = os.path.basename(root)
        found_mode = None
        prefix = None
        bkg_image = None
        for mode in op_bake.modes:
            pos = filename.find("_"+mode)
            if pos != -1:
                found_mode = mode
                prefix = filename[:pos]
                break
        if found_mode:
            #print(f"bakeset found mode:{found_mode} {prefix}")
            imgfiles = [f for f in os.listdir(dirname) if (os.path.isfile(os.path.join(dirname, f)) and f.startswith(prefix) and f.endswith(ext))]
            if len(imgfiles) > 0:
                tt_settings().single_prefix = prefix
                for imgfile in imgfiles:
                    bNeedsLoadFromDisk = True
                    imgfile_no_ext, ext = os.path.splitext(imgfile)
                    for image in bpy.data.images:
                        if image.name.startswith(imgfile_no_ext):
                            if image.size[0] == tt_settings().size[0] and image.size[1] == tt_settings().size[1]:
                                print("bakeset image already found internally:" ,imgfile_no_ext)
                                bkg_image = image
                            else:
                                print("bakeset image ignored (wrong size) :" ,imgfile_no_ext)
                            bNeedsLoadFromDisk = False
                            break
                    if bNeedsLoadFromDisk:
                        print("loading bakeset image from disk:" ,imgfile)
                        image = bpy.data.images.load(os.path.join(dirname, imgfile), check_existing=False)
                        if image.size[0] == tt_settings().size[0] and image.size[1] == tt_settings().size[1]:
                            print("bakeset image already found inside:" ,imgfile_no_ext)
                            bkg_image = image
                        else:
                            print("bakeset image ignored (wrong size) :" ,imgfile_no_ext)
                        bpy.data.images[imgfile].name = imgfile_no_ext
            def set_image_as_background(image):
                for area in bpy.context.screen.areas:
                    if area.ui_type == 'UV':
                        area.spaces[0].image = bpy.data.images[image.name]

            #preferably activate the selected one
            for image in bpy.data.images:
                if image.name.startswith(prefix + '_'+ found_mode) and image.size[0] == tt_settings().size[0] and image.size[1] == tt_settings().size[1]:
                    bkg_image = image
                    break

            #TODO: cleanup coincident but wrong size ones if zero users
 
            def set_bake_mode_from_image (sets,image):
                for s,bset in enumerate(sets):
                    name_texture = f"{utilities_bake.get_texture_prefix(s)}_"
                    if name_texture in image.name:
                        imagefilename = image.name.split('.')
                        bakemode = imagefilename[0].replace(name_texture,'').split('_',0)#supports modes containing '_'
                        if  len(bakemode) > 0:
                            bakemode = bakemode[0] +".bip"
                            bpy.context.window_manager.TT_bake_mode = bakemode
                            break
            if bkg_image: 
                set_image_as_background(bkg_image)  
                set_bake_mode_from_image(settings.sets,bkg_image)    

        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

