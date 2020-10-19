import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import cantrips as can

class FitsObject:

    """
    A python object that reads in a fits data file, either an image or a table.  Written
        to make handling fits data more intuitive - the hdu/hdul stuff is all masked.
        The user can just query the object for the data or the header.  
    """

    def showImage(self, n_mosaic_rows = 2, logscale = 1):
        if logscale:
            disp_data = np.log10(self.data)
        else:
            disp_data = self.data
        if self.fits_data_type != 'image':
            print ('This FitsObject contains fits data of type: "' + fits_data_type + '" - I cannot display that.')
        else:
            if self.n_mosaic_extensions <=1:
                plt.imshow(disp_data)
            else:
                f, axarr = plt.subplots(n_mosaic_rows, np.ceil(self.n_mosaic_extensions / 2))
                for i in range(self.n_mosaic_extensions):
                    axarr[i //2, i % 2].imshow(disp_data[i])

        plt.show()

        return 1

    def saveFitsDataToFile(self, save_file_name, save_dir = None, overwrite = True):
        if save_dir == None:
            save_dir = self.load_dir
        if self.n_mosaic_extensions <= 1:
            if self.fits_data_type == 'image':
                col_names = []
            else:
                col_names = self.data.columns
            can.saveDataToFitsFile(self.data, save_file_name, save_dir, header = self.header, overwrite = overwrite, n_mosaic_extensions = self.n_mosaic_extensions, data_type = self.fits_data_type, col_names = col_names)

        return 1


    def __init__(self, fits_file, load_dir = '', fits_data_type = 'image', n_mosaic_extensions = 0):
        if fits_data_type in ['i','I','img','IMG','Img','image','IMAGE','Image']:
            fits_data_type = 'image'
        self.fits_file = fits_file
        self.target_dir = load_dir
        self.fits_data_type = fits_data_type
        self.n_mosaic_extensions = n_mosaic_extensions

        self.data, self.header = can.readInDataFromFitsFile(self.fits_file, self.target_dir, n_mosaic_image_extensions = self.n_mosaic_extensions, data_type = self.fits_data_type )

        if n_mosaic_extensions <=1:
            self.data = np.transpose(self.data)
        else:
            self.data = [np.transpose(self.data[i]) for i in range(len(n_mosaic_extensions))]