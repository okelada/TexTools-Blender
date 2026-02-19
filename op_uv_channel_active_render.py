import bpy
from . import utilities_uv
from . import settings

from .settings import tt_settings, prefs

class op(bpy.types.Operator):
	bl_idname = "uv.textools_uv_channel_active_render"
	bl_label = "Make UV Channel render default"
	bl_description = "Make the active UV channel render default for all the selected Objects"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		if bpy.context.active_object.type != 'MESH':
			return False
		if not bpy.context.object.data.uv_layers:
			return False
		return True


	def execute(self, context):
		# premode = bpy.context.active_object.mode
		# utilities_uv.multi_object_loop(removeuvs, self, context)
		# bpy.ops.object.mode_set(mode=premode)
		selected_obs = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
		if selected_obs:
			for ob in selected_obs:
				if ob.data.uv_layers:
					# Change Mesh UV Channel
					index = int(tt_settings().uv_channel)
					if index < len(ob.data.uv_layers):
						ob.data.uv_layers.active_index = index
						ob.data.uv_layers[index].active_render = True
		return {'FINISHED'}



# def removeuvs(self, context):
# 	if bpy.context.object.data.uv_layers:
# 		# Remove active UV channel
# 		bpy.context.active_object.data.uv_layers.remove(bpy.context.object.data.uv_layers.active)

# 	# Get current index
# 	index = len(bpy.context.object.data.uv_layers)-1
# 	if index >= 0:
# 		bpy.context.object.data.uv_layers.active_index = index
# 		bpy.context.scene.texToolsSettings.uv_channel = str(index)
# 		bpy.context.active_object.data.uv_layers[0].active_render = True
