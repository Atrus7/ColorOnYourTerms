import sys
import re
import xml.etree.ElementTree as ET
import subprocess
from subprocess import call
import applescript
import string

COLOR_NAME = "Solarized Dark"
PATH_TO_SCRIPT = "/Users/Chris/Desktop/Desktop Directory/Programming/iTerm2/"
PATH_TO_PLIST = PATH_TO_SCRIPT + "com.googlecode.iterm2.plist"
PROFILE_NUMBER = -1
apple_script_to_run = ''''''
#convert iTerm prefs into an xml so we can operate on it
cmd = "plutil -convert xml1 -o - " + PATH_TO_PLIST + " > "+ PATH_TO_SCRIPT + "readable_prefs.xml"
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
process.communicate()[0], "-actual"

tree = ET.parse(PATH_TO_SCRIPT + 'readable_prefs.xml')
root = tree.getroot()
root = root[0]

def check_children(passed_root, text):
  for child in passed_root:
    if(child.text == text):
      return True
  return False

def get_colors(preset_name):
  global tree
  color_root = tree.getroot()[0]
  i=0
  for child in color_root:
    if(child.text=='Custom Color Presets'):
      color_root = color_root[i+1]
    i+=1  
  j=0
  for child in color_root:
    if(child.text== preset_name):
      color_root = color_root[j+1]
      return color_root
    j+=1
  print "ERROR: Didn't find that preset"
  return None

def print_color(Color_Name, component_name, value):
  global PATH_TO_PLIST
  global PROFILE_NUMBER
  cmd = "/usr/libexec/PlistBuddy -c \"Print 'New Bookmarks':" + str(PROFILE_NUMBER) + ":'" + Color_Name + "':'" + component_name + "' " "\" \"" + PATH_TO_PLIST + "\""
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
  print process.communicate()[0], "-actual"
def preamble():
    global apple_script_to_run
    apple_script_to_run += ('''
tell application "iTerm_Nightly"
	tell current window
		tell current session''')



def closer():
    global apple_script_to_run
    apple_script_to_run += ('''
		end tell
	end tell
end tell''')

def change_color(Color_Name, value):
    global apple_script_to_run
    apple_script_to_run += ('''
			set ''' + Color_Name + ' to '  '{' + str(value[0] * 65535)  + ',' + str(value[1] * 65535)  + ', ' + str(value[2] * 65535)  + ''', 0 }
''')

def apple_dis_script():
  global apple_script_to_run
  # print apple_script_to_run
  a_script = applescript.AppleScript(apple_script_to_run)
  a_script.run()

def set_shell_var():
  global COLOR_NAME
  cmd = "export VIM_CS=\"" + COLOR_NAME + "\""
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
  process.communicate()[0], "-actual"


def main():
  global COLOR_NAME
  if len(sys.argv) > 1:
    COLOR_NAME = sys.argv[1]

  color_presets = get_colors(COLOR_NAME)
  rgb_colors = [0,0,0]
  j=0
#from iterm plist
  ANSI_array = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "bright black", "bright red", "bright green", "bright yellow", "bright blue", "bright magenta", "bright cyan", "bright white"]
  for colors in color_presets:
    if colors.text != None:
      if colors.text.find("Color") != -1:
        color_str = color_presets[j].text #Ex: "Ansi Color"
        m = re.search('[0-1][0-7]|[0-9]', color_str)
        if m != None:
            index = int(m.group(0))
            color_str = string.replace(color_str, m.group(0), ANSI_array[index])

        color_type = color_presets[j+1] #Ex: Ansi Color Dict
        for component_str in color_type:
          if component_str.text.find("Component") != -1:
            component_name = component_str.text
          else:
            value = component_str.text
            rgb_colors[2] = rgb_colors[1]
            rgb_colors[1] = rgb_colors[0]
            rgb_colors[0] = float(component_str.text)
        preamble()
        change_color(color_str, rgb_colors)
        closer()
        apple_dis_script()

    j+=1
  set_shell_var()
  print "Done"

if __name__ == '__main__':
  main()
