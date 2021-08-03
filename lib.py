#THIS LIBRARY CONTAIN UTILITY FUNCTIONS

import numpy as np
import random
import cv2
from PIL import Image
import zipfile
import io
import torch as t

def get_ssim(vid, vid_fake):
    #TODO: calculate ssim between two video, input shape BxCxHxW
    result = [pytorch_ssim.ssim(vid, vid_fake)]
    return result

class ZipReader(object):
    #TODO: unzip a file
    file_handle_dict = {}
    def __init__(self):
        super(ZipReader, self).__init__();
        
    @staticmethod
    def create_filehandle(path):
        #TODO: return filehandle for the target path, or create new fileandle for the new file
        if path in ZipReader.file_handle_dict:
            return ZipReader.file_handle_dict[path]
        else:
            file_handle = zipfile.ZipFile(path, 'r') #create new handle
            ZipReader.file_handle_dict[path] = file_handle
            return file_handle
        
    @staticmethod
    def get_filename_list(filepath):
        with zipfile.ZipFile(filepath, 'r') as zipObj:
            filename_list = zipObj.namelist() 
            return filename_list
    
    @staticmethod
    def get_image(zippath, image_name):
        zipfile = ZipReader.create_filehandle(zippath)
        data = zipfile.read(image_name)
        im = Image.open(io.BytesIO(data))
        return im
    
class Mask(object):
    #todo: create mask
    def __init__(self, tile_count, mask_size, tilepos_list):
        self.nh, self.nw = tile_count #number of tiles along the height and width
        self.h, self.w = mask_size
        self.tilepos_list = tilepos_list
        self.mask = self.spawn()
    
class Masking(object):
    #todo: apply Mask object to a video tensor
    
    @staticmethod
    def spawn(tile_count, mask_size, tilepos_list):
        #TODO: create a tile map from size and tile position
        h, w = mask_size
        nh, nw = tile_count
        dh, dw = h // nh, w // nw
        mask = np.zeros((h, w)).astype(int)
        for ph, pw in tilepos_list:
            mask[ph*dh:(ph+1)*dh, pw*dw:(pw+1)*dw] = 1   
        return t.Tensor(mask).type(t.FloatTensor)#mask#np.expand_dims(mask, -1)
    
    @staticmethod
    def spawn_random(tile_count, mask_size, upperbound_ratio=.4, lowerbound_ratio=.2, roll_chance=0.0):
        nh, nw = tile_count
        
        #chose the number of holes
        f_idx = lambda x: (x//nh, x%nw)
        hole_num = random.randint(int(nh * nw * lowerbound_ratio), int(nh * nw * upperbound_ratio))
        hole_list = [(i,j) for i in range(nh) for j in range(nw)]
        hole_list = random.sample(hole_list, hole_num)
        mask = Masking.spawn(tile_count, mask_size, hole_list)
        if random.random() < roll_chance:
            mask = t.roll(mask, int(random.random() * mask.shape[0]), dims=0)
            mask = t.roll(mask, int(random.random() * mask.shape[1]), dims=1)
        
        return mask, hole_list
    
    @staticmethod
    def spawn_batch_random(batch_size, tile_count, mask_size, upperbound_ratio=.4, lowerbound_ratio=.2, roll_chance=0.0):
        mask_list = []
        hole_list_list  = []
        for idx in range(batch_size):
            mask, hole_list = Masking.spawn_random(tile_count, mask_size, upperbound_ratio, lowerbound_ratio, roll_chance)
            mask_list.append(mask)
            hole_list_list.append(hole_list)
        return t.stack(mask_list), hole_list
    
    @staticmethod
    def expand(mask):
        #TODO: expand mask of shape mb, mh, mw to mb, mt, mc, mh, mw
        mb, mh, mw = mask.shape  #mh and mw are suppose to be equal to xh, xw
        mask = mask.view(mb, 1, 1, mh, mw)
        return mask
    
    @staticmethod
    def apply(x, mask):
        #TODO: apply the mask to an input. assumed dimensions BxTxCxHxW
        #      will ERASE data in masked areas
        xb, xt, xc, xh, xw = x.shape
        mask = Masking.expand(mask)
        
        x_fill = mask * x.mean() #fill the mask with mean values
        x = x * (1. - mask) + x_fill
        
        return x    
    
    @staticmethod
    def apply_inverse(x, mask):
        #TODO: apply mask to the input, but only holes have data
        xb, xt, xc, xh, xw = x.shape
        mask = Masking.expand(mask)
        x = x * mask
        return x
    
    @staticmethod
    def combine(x_true, mask, x_fake):
        #TODO: fill x_true outside holes, fill x_fake inside holes
        x_combined = Masking.apply(x_true, mask) + Masking.apply_inverse(x_fake, mask)
        return x_combined
    
##########Transforming classes for video data###############3
    
class ToTensor(object):
    #TODO: convert a list of PIL images into tensor
    def __init__(self):
        return
    
    def __call__(self, img_list):
        dat = np.array([np.array(img) for img in img_list])
        dat = dat.transpose((0, 3, 1, 2))#list of array has shape TxHxWxC
        return t.Tensor(dat)
    
class Normalize(object):
    #TODO: normalize a video tensor by individual channel
    def __init__(self, target_mean_list, target_std_list):
        self.target_mean_list = t.Tensor(target_mean_list).view(1, -1, 1, 1)
        self.target_std_list  = t.Tensor(target_std_list) .view(1, -1, 1, 1)
    
    def __call__(self, img_list):
        #TODO; normalze the input tensor of dimension TxCxHxW
        #mean_list = img_list.mean(dim=(0, 2, 3)).view(1, -1, 1, 1)
        #std_list  = img_list.std (dim=(0, 2, 3)).view(1, -1, 1, 1)
        img_list = (img_list/255 - self.target_mean_list)/self.target_std_list
        #img_list = (img_list - mean_list)/std_list
        #img_list = img_list * self.target_std_list + self.target_mean_list
        return img_list
    
class ToImage(object):
    #convert tensor back to image, accept one image of size CxHxW
    def __init__(self, target_mean_list, target_std_list):
        self.target_mean_list = t.Tensor(target_mean_list).view( -1, 1, 1)
        self.target_std_list  = t.Tensor(target_std_list) .view( -1, 1, 1)
        
    def __call__(self, x):
        #TODO: convert input tensor into an image, assuming shape CxHxW
        x = (x * self.target_std_list + self.target_mean_list) * 255
        #x = (x - x.min())/(x.max() - x.min()) * 255
        x = x.type(t.IntTensor)
        x = x.numpy().transpose(1, 2, 0)
        return x
    
class ToVideo(ToImage):
    #convert tensor block to videos, an extended version of ToImage, video size TxCxHxW
    def __init__(self, target_mean_list, target_std_list):
        self.target_mean_list = t.Tensor(target_mean_list).view( 1, -1, 1, 1)
        self.target_std_list  = t.Tensor(target_std_list) .view( 1 ,-1, 1, 1)
        
    def __call__(self, x):
        #TODO: convert input tensor into an image, assuming shape TxCxHxW
        x = (x * self.target_std_list + self.target_mean_list) * 255
        #x = (x - x.min())/(x.max() - x.min()) * 255
        x = x.type(t.IntTensor)
        x = x.numpy().transpose(0, 2, 3, 1)
        return x

class Resize(object):
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor
    
    def __call__(self, x):
        x = t.nn.functional.interpolate(x, scale_factor=self.scale_factor, mode='bilinear', align_corners=True, recompute_scale_factor=True)
        return x
    
class Salting(object):
    #TODO: randomly add 0 and max into the image
    
    def __init__(self, nl=5, nh=5, seed=42, chance=.5):
        self.nl = nl
        self.nh = nh
        np.random.seed(seed)
        self.chance = chance
        
    def rand_pos(self, w, h):
        pw = int(np.random.rand() * w)
        ph = int(np.random.rand() * h)
        return pw, ph
    
    def rand_salt(self, img, val):
        #TODO: random a position, and set the value val to the img
        #img: PIL object
        w, h = img.size
        pw, ph = self.rand_pos(w, h)
        img.putpixel((pw, ph), val)
    
    def __call__(self, x):
        #todo: set random position values (0, 0, 0) and (255, 255, 255)
        if np.random.rand() > self.chance:
            return x
        
        for _ in range(self.nl):
            self.rand_salt(x, (0, 0, 0))
            
        for _ in range(self.nh):
            self.rand_salt(x, (255, 255, 255))
        
        return x
          

class VidTensorConverter(object):
    #TODO: convert data workable for 2dconv into input data for 3dconv
    #input shape: B*T, C, H, W  --> B, C, T, H, W
    
    #t_size = -1
    
    def __init__(self):
        self.t_size = -1
        self.isValid = False
        #ConvertVidTensors.t_size = t_size
        
    def set_tsize(self, t_size):
        self.t_size = t_size
        self.isValid = True
        
    def check(self, x):
        if x.shape[1] != self.t_size:
            print ("ERROR: incompatible shape:")
            raise        
        
        if self.isValid == False:
            print ("ERROR: must call set_tsize method before using")
            raise
    
    def to3DTensor(self, x):
        self.check(x)
        #TODO: convert from B, T, C, H, W to B, C, T, H, W
        xb, xt, xc, xh, xw = x.shape
        x = t.transpose(x, 1, 2).contiguous()
        return x
    
    def to2DTensor(self, x):
        #TODO: convert from B, T, C, H, W to B*T, C, H, W
        self.check(x)
        xb, xt, xc, xh, xw = x.shape
        x = x.contiguous().view(xb*xt, xc, xh, xw)
        return x
    
    def from3DTensor(self, x):
        #TODO: convert from B, C, T, H, W to B, T, C, H, W
        x = t.transpose(x, 1, 2).contiguous()
        self.check(x)
        return x
    
    def from2DTensor(self, x):
        #TODO: convert from B*T, C, H, W, to B, T, C, H, W
        xbxt, xc, xh, xw = x.shape
        xt = self.t_size
        if xbxt % xt > 0:
            print ("WARNING:potential incompatible size")
            raise
        xb = xbxt // xt
        x = x.view(xb, xt, xc, xh, xw)
        return x
    
#############Most essentials tensor function for testing & training##########3

class AdversaryLoss(object):
    #TODO: implement the temporal patch GAN loss
    MODELTYPE_DISCRIMINATOR = 'discriminator'
    MODELTYPE_GENERATOR = 'generator'
    DATATYPE_REAL = 'real'
    DATATYPE_FAKE = 'fake'
    criterion = t.nn.ReLU()
    
    def __call__(self, x, model_type, data_type):
        if model_type == AdversaryLoss.MODELTYPE_DISCRIMINATOR:
            if data_type == AdversaryLoss.DATATYPE_REAL:
                return self.criterion(1 - x).mean()
            elif data_type == AdversaryLoss.DATATYPE_FAKE:
                return self.criterion(1 + x).mean()
            else:
                raise
        else:
            return -x.mean() 
