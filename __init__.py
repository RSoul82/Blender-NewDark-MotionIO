# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    'name': 'Blender NewDark Motion Import/Export',
    'author': 'Tom N Harris, 2.80/2.9x/3.x update by Robin Collier, with help from FireMage with storing motion flags',
    'version': (1, 1, 0),
    'blender': (4, 1),
    'location': 'File > Import-Export',
    'description': 'Import/Export Dark Engine Motions (or import skeletons via .cal files)',
#    'wiki_url': '',
#    'tracker_url': '',
#    'support': '',
    'category': 'Import-Export'}

# To support reload properly, try to access a package var, if it's there, reload everything
if 'bpy' in locals():
    import importlib
    if 'Import_Motion_Or_Cal' in locals():
        importlib.reload(Import_Motion_Or_Cal)
    if 'Export_Motion' in locals():
        importlib.reload(Export_Motion)

import bpy
import os
import json
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty, IntProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

default_config = {
'supporting_files_dir': 'C:\\Users\\Robin\\Resources\\Dromed\\Motions\\bvh_convert',
'auto_del_temp_bvh': True,
'max_motion_frames': 10000,
'map_file': 'BIPED.MAP',
'creature_type': 0,
'import_cal_file': 'manbase.cal',
'import_map_file': 'BIPED.MAP'
}

config_filename = 'NewDarkMotionIO.cfg'
config_path = bpy.utils.user_resource('CONFIG', path='scripts', create=True)
config_filepath = os.path.join(config_path, config_filename)

def load_config():
    config_file = open(config_filepath, 'r')
    config_from_file = json.load(config_file)
    config_file.close()
    return config_from_file

try:
    config_file = open(config_filepath, 'r')
    config_from_file = json.load(config_file)
    config_file.close()
except IOError:
    config_file = open(config_filepath, 'w')
    json.dump(default_config, config_file, indent=4, sort_keys=True)
    config_file.close()
    load_config()

#Try to get a value from a config file. Return ... if key not founnd.
def tryConfig(key, config_from_file):
    try:
        return config_from_file[key]
    except:
        config_file.close()
        config_from_file[key] = default_config[key] #add missing key with default value
        config_update = open(config_filepath, 'w')
        json.dump(config_from_file, config_update, indent = 4, sort_keys = True)
        config_update.close()
        load_config()
        return config_from_file[key]

def read_cal_files(file_dir):
    cal_file_list = []
    for file in os.listdir(file_dir):
        if file.lower().endswith('.cal'):
            full_path = os.path.join(file_dir,file)
            cal_file_list.append((file, file, full_path))
    return cal_file_list

def read_map_files(file_dir):
    map_file_list = []
    for file in os.listdir(file_dir):
        if file.lower().endswith('.map'):
            full_path = os.path.join(file_dir,file)
            map_file_list.append((file, file, full_path))
    return map_file_list

class FrameFlag(bpy.types.PropertyGroup):
    flag: bpy.props.EnumProperty(
        items=(
            (str(2**0), "Standing", "", 2**0),
            (str(2**1), "LeftFootfall", "", 2**1),
            (str(2**2), "RightFootfall", "", 2**2),
            (str(2**3), "LeftFootUp", "", 2**3),
            (str(2**4), "RightFootUp", "", 2**4),
            (str(2**5), "FireRelease", "", 2**5),
            (str(2**6), "CanInterrupt", "", 2**6),
            (str(2**7), "StartMotionHere", "", 2**7),
            (str(2**8), "EndMotionHere", "", 2**8),
            (str(2**9), "BlankTag1", "", 2**9),
            (str(2**10), "BlankTag2", "", 2**10),
            (str(2**11), "BlankTag3", "", 2**11),
            (str(2**12), "Trigger1", "", 2**12),
            (str(2**13), "MakeWeaponPhysical", "Allow hit or block", 2**13),
            (str(2**14), "MakeWeaponNonPhysical", "(disable the above)", 2**14),
            (str(2**15), "BodyCollapse", "", 2**15),
            (str(2**16), "Trigger5", "", 2**16),
            (str(2**17), "WeaponCharge", "E.g. bow creaking when drawn", 2**17),
            (str(2**18), "RobotSearchSound", "", 2**18),
            (str(2**19), "WeaponSwing", "Unused?", 2**19),
        ),
        options = {"ENUM_FLAG"}
    )

class SyncFrameFlags(bpy.types.Operator):
    bl_idname = "scene.frame_flags_sync"
    bl_label = "Sync Frame Flags"
    
    def execute(self, context):
        scene = context.scene
        max_frames = tryConfig('max_motion_frames', config_from_file)
        while len(scene.flags) < max_frames:
            scene.flags.add()
        return {"FINISHED"}
        
class MoveFlagsToNextFrame(bpy.types.Operator):
    bl_idname = "scene.frame_flags_move_next"
    bl_label = "Swap Next >>"
    bl_description = "Swap the flags in this frame with the flags from the next frame"
    
    def execute(self, context):
        scene = context.scene
        temp_flag = scene.flags[scene.frame_current].flag
        scene.flags[scene.frame_current].flag = scene.flags[scene.frame_current + 1].flag
        scene.flags[scene.frame_current + 1].flag = temp_flag
        
        return {"FINISHED"}
        
class MoveFlagsToPrevFrame(bpy.types.Operator):
    bl_idname = "scene.frame_flags_move_prev"
    bl_label = "<< Swap Prev"
    bl_description = "Swap the flags in this frame with the flags from the previous frame"
    
    def execute(self, context):
        scene = context.scene
        if scene.frame_current > 1:
            temp_flag = scene.flags[scene.frame_current].flag
            scene.flags[scene.frame_current].flag = scene.flags[scene.frame_current - 1].flag
            scene.flags[scene.frame_current - 1].flag = temp_flag
        else:
            self.report({'INFO'}, "Cannot swap below frame 1")
        
        return {"FINISHED"}
        
class ClearFlags(bpy.types.Operator):
    bl_idname = "scene.frame_flags_clear"
    bl_label = "Clear This"
    bl_description = "Remove all flags from this frame"
    
    def execute(self, context):
        scene = context.scene
        scene.flags[scene.frame_current].flag = set()
        
        return {"FINISHED"}

class ClearFlagsFromAll(bpy.types.Operator):
    bl_idname = "scene.frame_flags_clear_all"
    bl_label = "Clear All"
    bl_description = "Remove all flags from All frames"
    
    def execute(self, context):
        scene = context.scene
        i = 1
        for i in range(len(scene.flags)):
            scene.flags[i].flag = set()
        return {"FINISHED"}
    
class SceneFrameFlagPanel(bpy.types.Panel):
    bl_idname = 'SCENE_PT_dark_engine_motion_io'
    bl_label = "Frame Flags"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene
        max_frames = tryConfig('max_motion_frames', config_from_file)
        layout = self.layout
        column = layout.column(align=True)
        if len(scene.flags) < max_frames:
            column.operator("scene.frame_flags_sync")
        else:
            column.prop(scene, "frame_current")
            column.props_enum(scene.flags[scene.frame_current], "flag")
            swap_buttons = self.layout.row()
            swap_buttons.operator("scene.frame_flags_move_prev")
            swap_buttons.operator("scene.frame_flags_move_next")
            clear_row = self.layout.row()
            clear_row.operator("scene.frame_flags_clear")
            clear_row.operator("scene.frame_flags_clear_all")
            
class MotionTypePanel(bpy.types.Panel):
    bl_idname = 'SCENE_MTYPE_PT_dark_engine_motion_io'
    bl_label = 'Creature Type'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene, 'map_file')
        col.prop(context.scene, 'creature_type')
        col.operator('file.open_motion_config', icon = 'SETTINGS')
        
class OpenConfigFile(bpy.types.Operator):
    """Open the config file to change the default values for this addon. Blender must be closed and restarted for the changes to take effect. Be careful with the file structure"""
    bl_idname = 'file.open_motion_config'
    bl_label = 'Open Config File'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        os.startfile(config_filepath)
        return {'FINISHED'}

class ImportMotionOrCal(bpy.types.Operator, ImportHelper):
    '''Import from Motion or Cal file (.mi/.cal)'''
    bl_idname = 'import_scene.motion'
    bl_label = 'Import Motion or .Cal file'
    filename_ext = '.mi'
    filter_glob: StringProperty(default='*.mi;*.cal', options={'HIDDEN'})
    bl_options = {'PRESET'}

    support_file_str = tryConfig('supporting_files_dir', config_from_file)
    support_file_dir: StringProperty(
                                     name = 'Supporting Files Location', 
                                     default = support_file_str, 
                                     description='Folder containing .cal, .map files etc'
                                     )

    cal_file: EnumProperty(
                           name='Cal File',
                           items = read_cal_files(support_file_str),
                           default=tryConfig('import_cal_file', config_from_file),
                           )
    
    map_file: EnumProperty(
                           name='Map File',
                           items = read_map_files(support_file_str),
                           default=tryConfig('import_map_file', config_from_file),
                           )
                           
    del_bvh: BoolProperty(
                          name = 'Delete Temp .bvh File',
                          default = tryConfig('auto_del_temp_bvh', config_from_file),
                          description = 'Delete the tempoary .bvh file which is created during the import process'
                          )
                          
    def execute(self, context):
        from . import Import_Motion_Or_Cal
        keywords = self.as_keywords(ignore=('','filter_glob'))
        return Import_Motion_Or_Cal.load(self, context, **keywords)
       
creature_types = (
                 ("0x7FFFF", "human", ""),
                 ("0xFFFFF", "human with sword", ""),
                 ("0x3FFFF", "droid", ""),
                 ("0xFF", "spidbot", ""),
                 ("0x1FFFFFFF", "arachnid", ""),
                 ("0xE", "plyrarm", ""),
                 ("0x3FFFFF", "bugbeast", ""),
                 ("0x1FFFFF", "crayman", ""),
                 ("0x7F", "sweel", ""),
                 ("0x7", "overlord", ""),
                 )

support_file_str = tryConfig('supporting_files_dir', config_from_file)

class ExportMotion(bpy.types.Operator, ExportHelper):
    '''Export to Motion file (.mi)'''
    bl_idname = 'export_scene.motion'
    bl_label = 'Export Motion file'
    filename_ext = '.mi'
    filter_glob: StringProperty(default='*.mi', options={'HIDDEN'})
    bl_options = {'PRESET'}
    
    support_file_dir: StringProperty(
                                     name = 'Supporting Files Location', 
                                     default = support_file_str, 
                                     description='Folder containing .cal, .map files etc'
                                     )
    
    del_bvh: BoolProperty(
                          name = 'Delete Temp .bvh File',
                          default = tryConfig('auto_del_temp_bvh', config_from_file),
                          description = 'Delete the tempoary .bvh file which is created during the export process'
                          )
    
    def execute(self, context):
        from . import Export_Motion
        keywords = self.as_keywords(ignore=('check_existing','filter_glob'))
        keywords['map_file'] = context.scene.map_file
        keywords['crettype'] = context.scene.creature_type
        return Export_Motion.save(self, context, **keywords)
        
    
# Add to a menu
def menu_func_import(self, context):
    self.layout.operator(ImportMotionOrCal.bl_idname, text='Motion or Skeleton (.mi, .cal) (NewDark Motion IO)')

def menu_func_export(self, context):
    self.layout.operator(ExportMotion.bl_idname, text='Motion file (.mi) (NewDark Motion IO)')

classes = (
            ImportMotionOrCal,
            FrameFlag,
            SyncFrameFlags,
            SceneFrameFlagPanel,
            MoveFlagsToNextFrame,
            MoveFlagsToPrevFrame,
            ClearFlags,
            ClearFlagsFromAll,
            ExportMotion,
            MotionTypePanel,
            OpenConfigFile,
            )

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.Scene.flags = bpy.props.CollectionProperty(type=FrameFlag)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    bpy.types.Scene.map_file = EnumProperty(name = 'Map File', items = read_map_files(support_file_str), description = 'File assigning joint names to IDs', default = tryConfig('export_map_file', config_from_file))
    bpy.types.Scene.creature_type = EnumProperty(name = 'Creature Type', items = creature_types, description = 'Type of bone/joinr structure to use', default = tryConfig('creature_type', config_from_file))

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()
