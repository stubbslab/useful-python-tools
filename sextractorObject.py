import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import math 

def makeGroupedEllipticityPlots(PySexList, file_name = 'test.png', save_dir = '/Users/sasha/Documents/sextractor-2.19.5/test_save_files/', 
                                contour_scaling = 10.0, arrow_scaling = 40.0, x_key_str = 'X_IMAGE', y_key_str = 'Y_IMAGE',
                                axarr = None, show = 1, save = 0, plot_contours = 1, plot_arrows = 1,
                                A_key_str = 'A_IMAGE', B_key_str = 'B_IMAGE', theta_key_str = 'THETA_IMAGE',
                                fwhm_key_str = 'FWHM_IMAGE', elongation_key_str = 'ELONGATION', figsize = [1500.0 / 100.0, 2400.0 / 100.0]):
    f, axarr = plt.subplots(2,2, figsize = figsize)
    #elong_thresh = 1.5
    
    for i in range(2):
        for j in range(2):
            #print 'PySexList[2*i + j].trimmed_dict[elongation_key_str] = ' + str(PySexList[2*i + j].trimmed_dict[elongation_key_str])
            PySexList[2*i + j].makeEllipticityPlot(contour_scaling = contour_scaling, arrow_scaling = arrow_scaling, x_key_str = x_key_str, y_key_str = y_key_str,
                                                    axarr = axarr[i,j], show = 0, save = 0, plot_contours = plot_contours, plot_arrows = plot_arrows,
                                                    A_key_str = A_key_str, B_key_str = B_key_str, theta_key_str = theta_key_str,
                                                    fwhm_key_str = fwhm_key_str, elongation_key_str = elongation_key_str)
            
            axarr[i,j].text(figsize[0] * 0.05 * 100.0, figsize[1] * 0.75 * 100.0, 'Median FWHM = ' + str(np.median(PySexList[2*i + j].trimmed_dict[fwhm_key_str]) ) + str(' (pix)'),
                            color = 'r', size = 25.0)

    f.subplots_adjust(hspace = 0.0, wspace = 0.0)
    axarr[0,0].set_xticks([])
    axarr[0,0].set_yticks([0,500,1000,1500,2000])
    axarr[0,0].set_ylabel('y image coordinate')
    axarr[0,1].set_xticks([])
    axarr[0,1].set_yticks([])
    axarr[1,0].set_xticks([0,400,800,1200])
    axarr[1,0].set_xlabel('x image coordinate')
    axarr[1,0].set_yticks([0,500,1000,1500,2000])
    axarr[1,0].set_ylabel('y image coordinate')
    axarr[1,1].set_xticks([0,400,800,1200])
    axarr[1,1].set_xlabel('x image coordinate')
    axarr[1,1].set_yticks([])

    
    axarr[0,0].text


    if save:
        plt.savefig(save_dir + file_name)
    if show:
        plt.show()


#Sextractor flags are stored as a sum of power-of-two ints.
# There are 8 (ie, Log2(128) + 1) distinct flags, each one stored as a
# 2, 4, 8, 16, 32, 64, or 128 in the sum.  Thus every possible
# flag value corresponds to a particular combination of various flags.
#Here, we want to see if SOME flags of interest are contained in the
# actual flag set.  We do so by pealing off one power of two at a time.  
def checkSexFlag(flags_of_interest, orig_flag_val):
    contains_flags_of_interest = [0 for flag in flags_of_interest]
    sex_flags = [128, 64, 32 ,16, 8, 4, 2, 1]
    flag_val = orig_flag_val 
    for flag in sex_flags:
        if flag_val >= flag:
            if flag in flags_of_interest: contains_flags_of_interest[flags_of_interest.index(flag)] = 1
            flag_val = flag_val - flag

    return contains_flags_of_interest

class PySex:

    def trimObjectList(self, cut_by_mag = 1, mag_cuts = [-np.inf, np.inf], 
                             cut_by_flags = 1, flag_cuts = 'all',
                             trim_by_pixel_val = 1, pixel_range = [0, 60000],
                             cut_by_elong = 1, elong_thresh = np.inf,
                             cut_by_star_gal = 1, star_gal_thresh = 0.0,
                             cut_by_low_spread_funct = 0, low_spread_funct_thresh = -0.01):
        
        sex_flags = [1,2,4,8,16,32,64,128]
        if flag_cuts in ['all']:
            flag_cuts = sex_flags[:]
        if flag_cuts in ['none']:
            flag_cuts = [] 
        trimmed_dict = {}
        mags = self.full_dict[self.mag_key_str ]
        flags = self.full_dict[self.flag_key_str ]
        peak_vals = self.full_dict[self.peak_key_str]
        backgrounds = self.full_dict[self.background_key_str]
        elongations = self.full_dict[self.elongation_key_str]
        star_gal_vals = self.full_dict[self.star_gal_key_str]
        if cut_by_low_spread_funct: 
            spread_functs = self.full_dict[self.spread_funct_key_str]
        
        #print 'peak_vals[-25:-15] = ' + str(peak_vals[-25:-15]) 
        n_objects = len(flags) 
        for key in self.full_dict.keys():
            #print [[(not(cut_by_mag) or mags[i] < mag_cut), (not(cut_by_flags) or not(sum(checkSexFlag(flag_cuts, flags[i])))), (not(trim_by_pixel_val) or peak_vals[i] > pixel_range[0] and peak_vals[i] < pixel_range[1])] for i in range(n_objects)][-25:-15]
            trimmed_dict[key] = [self.full_dict[key][i] for i in range(n_objects) if (not(cut_by_mag) or (mags[i] > mag_cuts[0] and mags[i] < mag_cuts[1])
                                                                                      and (not(cut_by_flags) or not(sum(checkSexFlag(flag_cuts, flags[i]))))
                                                                                      and (not(trim_by_pixel_val) or peak_vals[i] + backgrounds[i] > pixel_range[0] and peak_vals[i] + backgrounds[i] < pixel_range[1])
                                                                                      and (not(cut_by_elong) or elongations[i] < elong_thresh ))
                                                                                      and (not(cut_by_star_gal) or star_gal_vals[i] >= star_gal_thresh)
                                                                                      and (not(cut_by_low_spread_funct) or spread_functs[i] < low_spread_funct_thresh)]
                                                                                      
        self.trimmed_dict = trimmed_dict

        return 1 
            

    def makeEllipticityPlot(self, contour_scaling = 10.0, arrow_scaling = 40.0, x_key_str = 'X_IMAGE', y_key_str = 'Y_IMAGE',
                             axarr = None, show = 1, save = 0,
                             plot_contours = 1, plot_arrows = 1, 
                             A_key_str = 'A_IMAGE', B_key_str = 'B_IMAGE', theta_key_str = 'THETA_IMAGE',
                             fwhm_key_str = 'FWHM_IMAGE', elongation_key_str = 'ELONGATION',
                             x_peak_str = 'XPEAK_IMAGE', y_peak_str = 'YPEAK_IMAGE', figsize = [1500.0 / 100.0, 2400.0 / 100.0]):

        #print 'self.trimmed_dict[fwhm_key_str] = '  + str(self.trimmed_dict[fwhm_key_str])
        #sqrt_elongation = np.sqrt(self.trimmed_dict[fwhm_key_str])
        #for i in range(len(self.trimmed_dict[fwhm_key_str])):
        #    elem = self.trimmed_dict[fwhm_key_str][i] 
        #    print 'working on ' + str(i) + 'th element: ' + str(elem)
        #    print 'math.sqrt(elem) = ' + str(math.sqrt(elem)) 
        #print '[math.sqrt(abs(elem)) for elem in self.trimmed_dict[fwhm_key_str]] = ' + str([math.sqrt(abs(elem)) for elem in self.trimmed_dict[fwhm_key_str]])
        if axarr is None: 
            fig, axarr = plt.subplots(figsize = figsize)
        if plot_contours: 
            ells = [Ellipse(xy=(self.trimmed_dict[x_key_str][i], self.trimmed_dict[y_key_str][i]),
                            width = contour_scaling * self.trimmed_dict[fwhm_key_str][i] * math.sqrt(abs(self.trimmed_dict[elongation_key_str][i])),
                            height = contour_scaling * self.trimmed_dict[fwhm_key_str][i] * 1.0 / math.sqrt(abs(self.trimmed_dict[elongation_key_str][i])),
                            angle = self.trimmed_dict[theta_key_str][i], facecolor = 'none', edgecolor = 'b')
                      for i in range(len(self.trimmed_dict[x_key_str])) if abs(self.trimmed_dict[fwhm_key_str][i]) > 0.0]
            #print [self.trimmed_dict[x_key_str][i] for i in range(len(self.trimmed_dict[x_key_str]))]
            #print self.trimmed_dict[x_key_str]
            for e in ells:
                axarr.add_artist(e)
                e.set_clip_box(axarr.bbox)
        if plot_arrows: 
            axarr.quiver(self.trimmed_dict[x_key_str], self.trimmed_dict[y_key_str],
                         (np.array(self.trimmed_dict[elongation_key_str]) - 1.0) * np.cos(np.array(self.trimmed_dict[theta_key_str]) * math.pi / 180.0 ) * arrow_scaling,
                         (np.array(self.trimmed_dict[elongation_key_str]) - 1.0) * np.sin(np.array(self.trimmed_dict[theta_key_str]) * math.pi / 180.0 ) * arrow_scaling, angles = 'xy', units = 'xy')

        axarr.set_xlim(min(self.trimmed_dict[x_key_str]), max(self.trimmed_dict[x_key_str]))
        axarr.set_ylim(min(self.trimmed_dict[y_key_str]), max(self.trimmed_dict[y_key_str]))
        if show: 
            plt.show()
        

    def generateRegionFile(self, file_name = 'test.reg', region_type = 'ellipse', x_key_str = 'X_IMAGE', y_key_str = 'Y_IMAGE', color = 'green', 
                                 A_key_str = 'A_IMAGE', B_key_str = 'B_IMAGE', theta_key_str = 'THETA_IMAGE', fwhm_str = 'FWHM_IMAGE',
                                 elongation_key_str = 'ELONGATION'):
        file_lines = ['# Region file format: DS9 version 4.1',
                      'global color='+ color  + ' dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1',
                      'image']
        if region_type.lower() in ['ellipse', 'el', 'ell']:
            region_start = 'ellipse'
            #region_keys = [x_key_str, y_key_str, A_key_str, B_key_str, theta_key_str]
            region_keys = [x_key_str, y_key_str, fwhm_str, elongation_key_str, theta_key_str]
            for i in range(len(self.trimmed_dict[self.sex_keys[0]])):
                file_lines = file_lines + [region_start + '(' + ','.join([str(self.trimmed_dict[x_key_str][i]), str(self.trimmed_dict[y_key_str][i]),
                                                                          str(self.trimmed_dict[fwhm_str][i] * math.sqrt(self.trimmed_dict[elongation_key_str][i])),
                                                                          str(self.trimmed_dict[fwhm_str][i] / math.sqrt(self.trimmed_dict[elongation_key_str][i])),
                                                                          str(self.trimmed_dict[theta_key_str][i]) ])  + ')']
        elif region_type.lower() in ['circle', 'circ']:
            region_start = 'circle'
            region_keys = [x_key_str, y_key_str, fwhm_str]
            for i in range(len(self.trimmed_dict[self.sex_keys[0]])):
                file_lines = file_lines + [region_start + '(' + ','.join([str(self.trimmed_dict[key][i]) for key in region_keys])  + ')']

        #print 'region_start = ' + region_start 
        #for i in range(len(self.trimmed_dict[self.sex_keys[0]])):
        #    file_lines = file_lines + [region_start + '(' + ','.join([str(self.trimmed_dict[key][i]) for key in region_keys])  + ')']


        with open(file_name, 'w') as f:
            for line in file_lines:
                #print line 
                f.write("%s\n" % line)
                
        #print 'file_lines = ' + str(file_lines)
        return 1 
    
    def __init__(self, sextractor_file = 'test.cat', mag_cut = np.inf, mag_key_str = 'MAG_ISO', flag_key_str = 'FLAGS', peak_key_str = 'FLUX_MAX',
                 background_key_str = 'BACKGROUND', elongation_key_str = 'ELONGATION', star_gal_key_str = 'CLASS_STAR', spread_funct_key_str = 'SPREAD_MODEL'): 
                       #property_dic = {'NUMBER':0, 'FLUX_ISO':1, 'FLUXERR_ISO':2, 'MAG_ISO':3, 'MAGERR_ISO':4,
                                                     #                'X_IMAGE':5, 'Y_IMAGE':6, 'A_IMAGE':7, 'B_IMAGE':8, 'THETA_IMAGE':9} ):
        
        sex_lines = open(sextractor_file).readlines()
        property_dict = {}

        self.mag_key_str = mag_key_str
        self.flag_key_str = flag_key_str
        self.peak_key_str = peak_key_str
        self.background_key_str = background_key_str
        self.elongation_key_str = elongation_key_str
        self.star_gal_key_str = star_gal_key_str
        self.spread_funct_key_str = spread_funct_key_str

        outputs = []
        outputs_dict = {} 
        for line in sex_lines:
            line = [elem for elem in line.split(' ') if len(elem) > 0]
            if line[0] in ['#']:
                property_dict[line[2]] = int(line[1]) 
                outputs = outputs + [[]]
            else:
                if len(outputs) == 0:  outputs = [[] for elem in range(len(property_dict))]
                for j in range(len(outputs)):
                    outputs[j] = outputs[j] + [line[j]]
                    if j == len(outputs) - 1: outputs[j][-1] = float(outputs[j][-1][0:-1])
                    else: outputs[j][-1] = float(outputs[j][-1])
 

        self.sex_keys = property_dict.keys() 
        for key in self.sex_keys:
            outputs_dict[key] = outputs[property_dict[key] - 1]
        outputs_dict[flag_key_str] = [int(elem) for elem in outputs_dict[flag_key_str]] 
        #print 'property_dict = '+ str(property_dict)

        self.full_dict = outputs_dict
        self.trimmed_dict = self.full_dict 

        #self.trimmed_dictt = {}
        #print self.full_dict[mag_key_str]
        #for key in self.sex_keys:
        #    if self.mag_key_str in self.sex_keys:
        #        self.trimmed_dictt[key] = [self.full_dict[key][i] for i in range(len(self.outputs_dict[key])) if self.outputs_dict[self.mag_key_str][i] < mag_cut]
        #    else:
        #        self.trimmed_dictt[key] = self.outputs_dict[key][:]

        
