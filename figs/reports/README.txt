This folder report the experiment results for each model prototype

Description for each figures in this folder:
paris_8_1.jpg                                       :     original image frame
frame0_stiched.png                                  :     the author's model, stack_num=8, hidden=128, notan
frame0_modellight_stiched_notan.png                 :     the author's model, stack_num=5, hidden=64, input 24x24, notan
frame0_modellight_48x48_scalefactor2_stiched.png    :     the author's model, stack_num=5, hidden=64, input 48x48, no tan
frame0_modellight_numstack5_hidden64_48x48_scalefactor2_withtan_DWS_stiched.png
                                                    :     use depthwise separable structure to save some memory
                                                    frame0_modellight_numstack8_hidden128_48x48_scalefactor2_withtan_DWS_stiched.png
                                                    :     same as the line above, but numstack=8, hidden=128
                                                    frame0_modellight_numstack8_hidden128_48x48_scalefactor2_withtan_DWS_l1_epoch7008_stiched.png
                                                    :     same with the line above, with 7008 epochs
                                                    
                                                    frame0_modellight_numstack8_hidden128_48x48_scalefactor2_withtan_DWS_l1_epoch7008_saltingstiched.png
                                                    :     same with above, but add black & white (600/48x48). Image does not have distinguishing tiles, but quality is bad