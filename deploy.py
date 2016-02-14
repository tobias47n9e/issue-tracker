import os
import shutil
import getpass

files = ["issue_tracker.plugin",
	 "issue_tracker.py"]

usr = getpass.getuser()

print("Copying files to:\n" +
      "/home/{}/.local/share/gnome-builder/plugins/".format(usr))
print(files)

for fl in files:
    dst_path = "/home/{}/.local/share/gnome-builder/plugins/{}".format(usr, fl)
    shutil.copyfile("issue_tracker/{}".format(fl), dst_path)

