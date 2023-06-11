# Blender NewDark Motion Import/Export
Allows Blender to import and export Dark Engine (Thief/Thief 2, System Shock 2) motions, including flags.

## Itroduction
This Blender addon allows the user to import and export motions for the Dark Engine games. Motion flags are also supported, meaning various sounds, weapon effects (etc) can be triggered as the motion plays.

## Credits
This addon is based heavily on Telliamed's motion conversion Python scripts in the [Blender Toolkit](https://www.ttlg.com/forums/showthread.php?t=136431)<br>
Much of the code is unchanged. The main differences are the integration into a Blender addon.<br>
For the motion flag support, Firemage deserves credit for providing info about the .mi file structure, and the blenderartists user Gorgious came up with a way of [managing and showing those flags in Blender](https://blenderartists.org/t/unique-set-of-properties-per-frame/1467364/2)<br>
Finally, this addon also makes use of Blenders existing BVH addon.


## Installation
### Blender Files
Go to the [Releases](https://github.com/RSoul82/Blender-NewDark-MotionIO/releases/tag/Release) page and download **Blender-NewDark-MotionIO.zip**<br>
**NO NEED TO UNZIP MANUALLY**

In Blender, go to Edit > Preferences > Addons then Install:<br>
![Install button](/Screenshots/01_install.jpg)<br>
This will install it into the correct folder.

**While you're in the Addons window, make sure the BVH addon is also enabled**

### Motion Files
Find you game's "crf" files and open **Mesh.crf** with a zip program (e.g. 7Zip). Extract all **.cal** and **.map** files to a folder of your choice. These are what the addon refers to as "Supporting Files". Copy the full path of this folder.

### Config file setup
When the addon is installed it will create a config file with some default values. In your file explorer go to %appdata%\Blender Foundation\Blender\ **version number here** \config\scripts and open **NewDarkMotionIO.cfg**

Edit the value of **supporting_files_dir** to point to where you extracted the files mentioned above. Note that you have to use pairs of back-slashes before each folder, and surround the whole thing with double quotes, e.g: "C:\\Users\\SomeGuyIDK\\Dromed\\Motions\\extra files"
