#BaseNet contain basic functions exists in alny other classes. Nothing fancy. For example, get parameters, init weights
import torch as t
import torchvision as tv
import torch.nn.utils.parametrizations

import numpy as np
import math

import lib


class BaseNet(t.nn.Module):
    def __init__(self):
        super(BaseNet, self).__init__()
    
    def get_info(self):
        if isinstance(self, list): #what does this line even mean?
            print ("self if a list?")
            raise
            self = self[0]
            
        num_params = 0
        for param in self.parameters():
            num_params += param
        print (f'Net name: {type(self).__name__}, Net size: {num_params/1e6} Millions')
    
    def init_weights(self, init_type='normal', gain=0.02):
        def init_func(m):
            classname = m.__class__.__name__
            #print (f'init weight with classname={classname}')
            if classname.find('InstanceNorm2d') != -1:
                if hasattr(m, 'weight') and m.weight is not None:
                    t.nn.init.constant_(m.weight.data, 1.0)
                if hasattr(m, 'bias') and m.bias is not None:
                    t.nn.init.constant_(m.bias.data, 0.0)
            elif hasattr(m, 'weight') and (classname.find('Conv') != -1 or classname.find('Linear') != -1):
                if init_type == 'normal':
                    t.nn.init.normal_(m.weight.data, 0.0, gain)
                elif init_type == 'xavier':
                    t.nn.init.xavier_normal_(m.weight.data, gain=gain)
                elif init_type == 'xavier_uniform':
                    t.nn.init.xavier_uniform_(m.weight.data, gain=1.0)
                elif init_type == 'kaiming':
                    t.nn.init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
                elif init_type == 'orthogonal':
                    t.nn.init.orthogonal_(m.weight.data, gain=gain)
                elif init_type == 'none':  # uses pytorch's default init method
                    m.reset_parameters()
                else:
                    raise NotImplementedError(
                        'initialization method [%s] is not implemented' % init_type)
                if hasattr(m, 'bias') and m.bias is not None:
                    t.nn.init.constant_(m.bias.data, 0.0)
        
        self.apply(init_func) #apply to childrend recursively?
        
        for m in self.children():
            if hasattr(m, 'init_weights'):
                m.init_weights(init_type, gain)
                
            
    def forward(self, masked_frames, masks):
        raise
    
    def infer(self, feat, masks):
        raise         



class SuperResV0(BaseNet): #try to reconstruct the network used by the author of the super-res paper
    def __init__(self, hidden, stack_num, scale_factor, init_weights=True):
        super(SuperResV0, self).__init__()
        self.scale_factor = scale_factor
        self.hidden = hidden
        self.stack_num = stack_num
        
        self.encoder0 = t.nn.Sequential(
            t.nn.Conv2d(3, self.hidden, kernel_size=3, stride=1, padding=1),
            t.nn.LeakyReLU(0.2, inplace=True),
            t.nn.BatchNorm2d(self.hidden),
        )
        
        encoder_blocks = []
        for _ in range(self.stack_num - 1):
            encoder_blocks.append(FeedForward(channels_in=self.hidden, channels_out=self.hidden))
        self.encoders = t.nn.Sequential(*encoder_blocks)       
        
        self.decoders = t.nn.Sequential(
            t.nn.Conv2d(self.hidden, self.hidden, kernel_size=3, stride=1, padding=1, groups=self.hidden),
            t.nn.LeakyReLU(0.2, inplace=True),
            t.nn.Conv2d(self.hidden, self.hidden, kernel_size=1),
            t.nn.ConvTranspose2d(self.hidden, 3,   kernel_size=2, stride=2),
        )        
        
        if init_weights:
            self.init_weights()               
            
    def forward(self, x):
        x = t.nn.functional.interpolate(x, scale_factor=self.scale_factor, mode='bicubic')
        enc_feat = self.encoder0(x)
        enc_feat = enc_feat + self.encoders(enc_feat)
        output = self.decoders(enc_feat)
        output = t.tanh(output)
        return output
    
class SuperRes(SuperResV0):
    def __init__(self, hidden, stack_num, scale_factor, init_weights=True):
        super(SuperRes, self).__init__(hidden, stack_num, scale_factor, init_weights)
        encoder_blocks = []
        for _ in range(self.stack_num - 1):
            encoder_blocks.append(FeedForwardDWSConv(channels_in=self.hidden, channels_out=self.hidden))
        self.encoders = t.nn.Sequential(*encoder_blocks)  

            
####################################
class FeedForward(t.nn.Module):
    def __init__(self, channels_in, channels_out):
        super(FeedForward, self).__init__()
        self.conv = t.nn.Sequential(
            t.nn.Conv2d(channels_in, channels_out, kernel_size=3, stride=1, padding=1),
            t.nn.LeakyReLU(0.2, inplace=True),
            t.nn.BatchNorm2d(channels_out),
        )
        
    def forward(self, x):
        x = x + self.conv(x)
        return x
    
class FeedForwardDWSConv(t.nn.Module):
    def __init__(self, channels_in, channels_out):
#         from https://discuss.pytorch.org/t/how-to-modify-a-conv2d-to-depthwise-separable-convolution/15843/6
#         self.depthwise = nn.Conv2d(nin, nin, kernel_size=3, padding=1, groups=nin)
#         self.pointwise = nn.Conv2d(nin, nout, kernel_size=1)        
        super(FeedForwardDWSConv, self).__init__()
        self.conv = t.nn.Sequential(
            t.nn.Conv2d(channels_in, channels_out, kernel_size=3, stride=1, padding=1, groups=channels_in),
            t.nn.LeakyReLU(0.2, inplace=True),
            t.nn.BatchNorm2d(channels_out),
            t.nn.Conv2d(channels_in, channels_out, kernel_size=1),
            t.nn.LeakyReLU(0.2, inplace=True),
            t.nn.BatchNorm2d(channels_out),            
        )
    def forward(self, x):
        x = x + self.conv(x)
        return x
######Discriminator code#############

        
class Discriminator(BaseNet):
    def __init__(self, in_channels=3, use_sigmoid=False, use_spectral_norm=True, init_weights=True):
        super(DiscriminatorV0, self).__init__()
        self.use_sigmoid = use_sigmoid
        nf = 64
        sptrnorm = t.nn.utils.spectral_norm
        self.conv = t.nn.Sequential(
            sptrnorm(t.nn.Conv3d(in_channels=in_channels, out_channels=nf*1, kernel_size=(3, 5, 5), stride=(1, 2, 2),
                                    padding=1, bias=False)),
            # nn.InstanceNorm2d(64, track_running_stats=False),
            t.nn.LeakyReLU(0.2, inplace=True),
            sptrnorm(t.nn.Conv3d(nf*1, nf*2, kernel_size=(3, 5, 5), stride=(1, 2, 2),
                                    padding=(1, 2, 2), bias=False)),
            # nn.InstanceNorm2d(128, track_running_stats=False),
            t.nn.LeakyReLU(0.2, inplace=True),
            sptrnorm(t.nn.Conv3d(nf * 2, nf * 4, kernel_size=(3, 5, 5), stride=(1, 2, 2),
                                    padding=(1, 2, 2), bias=False)),
            # nn.InstanceNorm2d(256, track_running_stats=False),
            t.nn.LeakyReLU(0.2, inplace=True),
            sptrnorm(t.nn.Conv3d(nf * 4, nf * 4, kernel_size=(3, 5, 5), stride=(1, 2, 2),
                                    padding=(1, 2, 2), bias=False)),
            # nn.InstanceNorm2d(256, track_running_stats=False),
            t.nn.LeakyReLU(0.2, inplace=True),
            sptrnorm(t.nn.Conv3d(nf * 4, nf * 4, kernel_size=(3, 5, 5), stride=(1, 2, 2),
                                    padding=(1, 2, 2), bias=False)),
            # nn.InstanceNorm2d(256, track_running_stats=False),
            t.nn.LeakyReLU(0.2, inplace=True),
            t.nn.Conv3d(nf * 4, nf * 4, kernel_size=(3, 5, 5),
                      stride=(1, 2, 2), padding=(1, 2, 2))
        )

        if init_weights:
            self.init_weights()

    def forward(self, xs):
        # T, C, H, W = xs.shape
        xs_t = t.transpose(xs, 1, 2)
        #xs_t = xs_t.unsqueeze(0)  # B, C, T, H, W
        feat = self.conv(xs_t)
        if self.use_sigmoid:
            feat = torch.sigmoid(feat)
        out = torch.transpose(feat, 1, 2)  # B, T, C, H, W
        return out        