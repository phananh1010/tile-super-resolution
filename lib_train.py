import numpy as np
import torch as t
import time

import lib

def parsedat(dat, frame_idx, device, half=False):
    (frame_lr_list, frame_hr_list), frameidx_list, tilepos = dat
    #input frames has shape: BxTXCX
    if half==True:
        frame_lr_list = frame_lr_list.half()
        frame_hr_list = frame_hr_list.half()    
    if frame_idx == -1:
        frame_lr = frame_lr_list.to(device)
        frame_hr = frame_hr_list.to(device)
    frame_lr = frame_lr_list[:, frame_idx, :, :, :].to(device)#only get the rist frame, not the whole video
    frame_hr = frame_hr_list[:, frame_idx, :, :, :].to(device)
    frameidx_list = frameidx_list.to(device)
    
    return frame_lr, frame_hr, frameidx_list, (tilepos[0].numpy(), tilepos[1].numpy())