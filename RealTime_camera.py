import time
from wlm import *
import serial
import csv
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import sys
import os
from typing import Optional
from vimba import *
import matplotlib.gridspec as gridspec


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')
    if usage:
        print_usage()
    sys.exit(return_code)

def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)
    for arg in args:
        if arg in ('/h', '-h'):
            print_usage()
            sys.exit(0)
    if argc > 1:
        abort(reason="Invalid number of arguments. Abort.", return_code=2, usage=True)
    return None if argc == 0 else args[0]

def get_camera(camera_id: Optional[str]) -> Camera:
    with Vimba.get_instance() as vimba:
        if camera_id:
            try:
                return vimba.get_camera_by_id(camera_id)
            except VimbaCameraError:
                abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))
        else:
            cams = vimba.get_all_cameras()
            if not cams:
                abort('No Cameras accessible. Abort.')
            return cams[0]

def setup_camera(cam: Camera):
    with cam:
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            cam.GVSPAdjustPacketSize.run()

            while not cam.GVSPAdjustPacketSize.is_done():
                pass

        except (AttributeError, VimbaFeatureError):
            pass

cam_id = parse_args()
camera_folder_path = r'C:\Users\zhoul\OneDrive\Desktop\GUI_camera\Image'
os.makedirs(camera_folder_path, exist_ok=True)


plt.ion() #turn on interactive mode

# with Vimba.get_instance():
#     #i = 0
#     with get_camera(cam_id) as cam:
#         setup_camera(cam)
#     #    for i in range(5):
#         fig = plt.figure(figsize=(6, 4))
#         frame = next(cam.get_frame_generator(limit=100, timeout_ms=3000))
#         # Convert the frame to an image array
#         #image_array = np.copy(frame.as_numpy_ndarray())
#         #image_array_2D = image_array[:,:,0]
#         # Save the image array as a file in the folder
#         #image_file_name = f'image_AuPR_{i}.csv'
#         plt.clf()
#         plt.imshow(frame.as_numpy_ndarray())
#         plt.show()
#         plt.pause(0.1)
#         #np.savetxt(f'{camera_folder_path}/{image_file_name}', image_array_2D.astype(int), fmt='%i', delimiter=',')                 
#         #print(i)


# with Vimba.get_instance() as vimba:
#     cams = vimba.get_all_cameras()
#     with cams[0] as cam:
#         # Aquire single frame synchronously
#         #frame = cam.get_frame()
#         # Aquire 10 frames synchronously
#         for frame in cam.get_frame_generator(limit=5):
#             print(frame)
#             #print(cam.get_frame_generator)
#             plt.clf() #clear the current figure
#             plt.imshow(frame.as_numpy_ndarray())
#             plt.show()
#             plt.pause(0.1)
#             pass


with Vimba.get_instance() as vimba:
    cams = vimba.get_all_cameras()
    i = 0
    #fig, axs = plt.subplots(3)
    # Create a gridspec object with 1 row and 3 columns
    fig = plt.figure(figsize=(15,5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1])
    #fig = plt.figure()
    # Assign each subplot to a cell in the gridspec
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1])
    ax2 = plt.subplot(gs[2])

    with cams[0] as cam:
        while (True):
            # Aquire single frame synchronously
            frame = cam.get_frame()
            # Convert the frame to an image array
            image_array = np.copy(frame.as_numpy_ndarray())
            image_array_2D = image_array[:,:,0]
            #get the shape of array
            row, column = image_array_2D.shape
            mid_row = row//2
            mid_col = column//2
            row_info = image_array_2D[mid_row]
            column_info = image_array_2D[mid_col]

            #Save the image array as a file in the folder
            image_file_name = f'image_{i}.csv'
            #np.savetxt(f'{camera_folder_path}/{image_file_name}', 
            #           image_array_2D.astype(int), fmt='%i', delimiter=',')                 
            #print(i)
            #plt.clf() #clear the current figure
            ax0.cla()
            ax1.cla()
            ax2.cla()
            #axs[0].imshow(frame.as_numpy_ndarray())
            ax0.imshow(image_array_2D)
            ax1.plot(row_info, label="mid-row info")
            ax1.set_ylim([0,12])
            ax2.plot(column_info, label="mid-col info")
            #ax1.legend()
            #plt.imshow(frame.as_numpy_ndarray())
            ax2.set_ylim([0,12])
            fig.tight_layout(pad=3.0)
            plt.show()
            plt.pause(0.01)
            #i = i+1
            #pass


plt.ioff() #turn off interactive mode

