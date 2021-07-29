import torch as t
import torchvision as tv
import os
import json
import random
import numpy as np
import glob

import lib

class InpaintDataset(t.utils.data.Dataset):
    MODE_TRAIN = 'train'
    MODE_TEST  = 'test'
    MODE_DEBUG = 'debug'  #very small samples
    MODE_EVAL  = 'eval'
    DEBUG_LEN  = 2
    def __init__(self, data_root, mode=MODE_TRAIN, sample_length=30, frame_lr_transform=None, frame_hr_transform=None, vid_transform=None, refframe_transform=None):
        self.mode = mode
        self.data_root = data_root           #path to the directory containing zip files
        self.sample_length = sample_length   #fix the number of frames for all videos
        self.frame_lr_transform = frame_lr_transform
        self.frame_hr_transform = frame_hr_transform
        self.vid_transform = vid_transform
        self.refframe_transform = refframe_transform
        
        with open(os.path.join(data_root, mode + '.json')) as file:
            self.video_dict = json.load(file)
        self.videoname_list = list(self.video_dict.keys())
        self.framename_dict = {}
        self.load_framename_dict()
        
        if mode == self.MODE_DEBUG: 
            self.video_name_list = self.video_name_list[:self.DEBUG_LEN]
        
    def __len__(self):
        return len(self.videoname_list)
    
    def __getitem__(self, idx):
        try:
            item = self.load_item(idx)
        except:
            print (f'Error loading video named {self.videoname_list[idx]}')
            raise
        return item
    
    def get_zipfile(self, video_name):
        #TODO: locate the zip file containing all frames of the given video
        return os.path.join(self.data_root, 'JPEGImages', video_name + '.zip')
    
    def extract_image_from_zipfile(self, video_name, image_name):
        #TODO: read the given image in the zip file
        zipfile_path = self.get_zipfile(video_name)
        image = lib.ZipReader.get_image(zipfile_path, image_name)
        return image
    
    def load_framename_dict(self):
        #TODO: load all filename into a dictionary structure
        for vidname in self.videoname_list:
            filepath = self.get_zipfile(vidname)
            filename_list = lib.ZipReader.get_filename_list(filepath)
            filename_list.sort()
            self.framename_dict[vidname] = filename_list
        return 
    
    def get_framename_list(self, vidname):
        #TODO: return list of file from vid name
        return self.framename_dict[vidname]
    
    def get_frameidx_from_framename(self, framename):
        return int(framename.replace('.jpg', ''))
    
    def select_frame(self, vid_name, framename_full_list):
        #TODO: choose some random frame from frame_full_list, or choose consecutive, depending on the chance
        framename_list = []
        frameidx_list = []
        frame_lr_list = []
        frame_hr_list = []        
        
        chance = random.random()
        if self.mode != self.MODE_TRAIN:
            chance = 0 #always choose consecutive if mode is not train

        if chance < 0.5: #chance < 0.5, then alway choose consecutive list
            start_point = random.randint(0, max(0, len(framename_full_list) - self.sample_length))
            framename_list = framename_full_list[start_point:start_point+self.sample_length]            
            #print (chance, start_point, framename_full_list[start_point:start_point+self.sample_length])

        else:
            frame_idx_list = list(range(len(framename_full_list)))
            frame_idx_list = random.sample(frame_idx_list, min(self.sample_length, len(framename_full_list)))
            frame_idx_list.sort()
            #frame_idx_list = t.from_numpy(np.array(frame_idx_list))
            framename_list = [framename_full_list[idx] for idx in frame_idx_list]
        frameidx_list = [self.get_frameidx_from_framename(item) for item in framename_list]    
        

        
        #get frame in lr and hr from framename_list
        for framename in framename_list:
            try:
                img = self.extract_image_from_zipfile(vid_name, framename)
            except:
                print ("ERROR while loading {vid_name}, {frame_name}")  
                raise
            #get low resolution ground truth
            if self.frame_lr_transform != None:
                frame_lr_list.append(self.frame_lr_transform(img))            
            if self.frame_hr_transform != None:
                frame_hr_list.append(self.frame_hr_transform(img))
        
        return frame_lr_list, frame_hr_list, framename_list, t.from_numpy(np.array(frameidx_list))
    
    def select_refframe(self, vid_name, framename_full_list):
        #TODO: get reference frame in lr
        refframe_list = []
        refframe_name_list = []
        refframe_idx_list = t.from_numpy(np.array([0, len(framename_full_list) - 1]))
        for frame_idx in refframe_idx_list:
            framename = framename_full_list[frame_idx]
            if self.refframe_transform != None:
                try:
                    img = self.extract_image_from_zipfile(vid_name, framename)
                except:
                    print ("ERROR while loading {vid_name}, {frame_name}")  
                    raise
                refframe_name_list.append(framename)
                refframe_list.append(self.refframe_transform(img))
        refframeidx_list = [self.get_frameidx_from_framename(item) for item in refframe_name_list]
        return refframe_list, refframe_name_list, t.from_numpy(np.array(refframeidx_list))
            
        
    
    def load_item(self, idx):
        #use Zip reader to read all frames into memory
        vid_name = self.videoname_list[idx]
        frame_num = self.video_dict[vid_name]
        framename_full_list = self.get_framename_list(vid_name)
        #framename_full_list = [f'{str(i).zfill(5)}.jpg' for i in range(frame_num)]#full list of all frame of the video
        #select frames from list, equal to sample_length
        
        #framename_list = random.sample(framename_list, self.sample_length)
        #framename_list.sort()
        
        frame_lr_list, frame_hr_list, framename_list, frameidx_list = self.select_frame(vid_name, framename_full_list)
        

                
        refframe_list, refframe_name_list, refframeidx_list = self.select_refframe(vid_name, framename_full_list)
        
        if self.vid_transform != None:
            frame_lr_list   = self.vid_transform(frame_lr_list)
            frame_hr_list   = self.vid_transform(frame_hr_list)
            refframe_list   = self.vid_transform(refframe_list)
            
        #if self.refframe_transform != None:
        #    refframe_list = (self.refframe_transform(frame_list[0]), self.refframe_transform(frame_list[-1]),)
        
        return ((frame_lr_list, frame_hr_list), frameidx_list), (refframe_list, refframeidx_list)