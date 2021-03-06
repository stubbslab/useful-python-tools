import healpixTableLookup as healtl
import SashasAstronomyTools as atools
import subprocess
import AstronomicalParameterArchive
import os
import cantrips as c

class AstrometrySolver:

    def solveField(self, sorted_stellar_positions_fits_file, target_dir, ra, dec, image_height, image_width,
                   scale_low = 0.01, scale_high = 0.2, scale_units = '"arscecperpix"', rm_healpix_file = 0,
                   objects_file_suffix = '.xyls', wcs_solution_suffix = '.wcs', suffixes_of_files_to_remove = ['-indx.xyls', '.corr','.rdls', '.match', '.solved', '-objs.png', '.axy']):
        healpix_mapper = healtl.HealpixLookupTable()
        #deg_to_rad = self.astro_arch.getDegToRad()
        if type(ra) == str:
            ra = atools.getDegreeFromSkyCoordStr(ra, hour_angle = 1) #* deg_to_rad
        if type(dec) == str:
            dec = atools.getDegreeFromSkyCoordStr(dec, hour_angle = 0) #* deg_to_rad
        print ('[ra, dec] = ' + str([ra, dec] ))

        healpix_map = healpix_mapper.getAstrometryHealpix(ra, dec)
        print ('healpix_map = ' + str(healpix_map))

        #Download healpix map and move to correct directory
        print (' '.join(['solve-field', target_dir + sorted_stellar_positions_fits_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ]))
        #wcs_solve_stream = os.popen(' '.join(['solve-field', target_dir + sorted_stellar_positions_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ]))
        print ("['solve-field', target_dir + sorted_stellar_positions_fits_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ] = " + str(['solve-field', target_dir + sorted_stellar_positions_fits_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ]))
        print ("' '.join(['solve-field', target_dir + sorted_stellar_positions_fits_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ]) = " + str(' '.join(['solve-field', target_dir + sorted_stellar_positions_fits_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ])))
        wcs_solve_output = os.system(' '.join(['solve-field', target_dir + sorted_stellar_positions_fits_file, '--width', str(image_width),  '--height', str(image_height), '--overwrite',  '--scale-low',  str(scale_low),  '--scale-high', str(scale_high),  '--scale-units', scale_units ]))
        #output = wcs_solve_stream.read()
        print ('wcs_solve_output = ' + str(wcs_solve_output))

        image_root = sorted_stellar_positions_fits_file[0:-len(objects_file_suffix)]
        wcs_solution_file = image_root + wcs_solution_suffix

        for suffix_to_rm in suffixes_of_files_to_remove:
            try:
                os.remove(target_dir + image_root + suffix_to_rm)
            except(FileNotFoundError):
                print ('Could not find astrometry file ' + image_root + suffix_to_rm + ' to remove.')

        return wcs_solution_file

    def updateFitsHeaderWithSolvedField(self, wcs_solution_fits_file, original_image_file, new_image_file, target_dir, verbose = 0):
        #target_dir, target_wcs_fits_file, target_image_file, wcs_prefix = sys.argv[1:]

        wcs_data, wcs_header = c.readInDataFromFitsFile(wcs_solution_fits_file, target_dir)
        image_data, image_header = c.readInDataFromFitsFile(original_image_file, target_dir)

        keywords_to_copy = ['WCSAXES', 'CTYPE1','CTYPE2','EQUINOX','LONPOLE','LATPOLE','CRVAL1',
                            'CRVAL2','CRPIX1','CRPIX2','CUNIT1','CUNIT2','CD1_1','CD1_2','CD2_1','CD2_2',
                            'IMAGEW','IMAGEH',
                            'A_ORDER','A_0_0', 'A_0_1','A_0_2','A_0_3', 'A_1_0','A_1_1','A_1_2', 'A_2_0', 'A_2_1', 'A_3_0',
                            'B_ORDER','B_0_0', 'B_0_1','B_0_2','B_0_3', 'B_1_0','B_1_1','B_1_2', 'B_2_0', 'B_2_1', 'B_3_0',
                            'AP_ORDER','AP_0_0','AP_0_1','AP_0_2','AP_0_3', 'AP_1_0','AP_1_1','AP_1_2', 'AP_2_0', 'AP_2_1', 'AP_3_0',
                            'BP_ORDER','BP_0_0','BP_0_1','BP_0_2','BP_0_3', 'BP_1_0','BP_1_1','BP_1_2', 'BP_2_0', 'BP_2_1', 'BP_3_0',]

        image_header['COMMENT'] = 'WCS information generated by nova.astronometry.net'
        image_header['COMMENT'] = 'See file ' + wcs_solution_fits_file + ' for details.'
        for key in keywords_to_copy:
            try:
                image_header[key] = wcs_header[key]
            except(KeyError):
                if verbose: print('header keyword ' + str(key) + ' not found in wcs file ' + wcs_solution_fits_file)

        c.saveDataToFitsFile(image_data.transpose(), new_image_file, target_dir, header = image_header)

        return new_image_file

    def __init__(self):
        self.astro_arch = AstronomicalParameterArchive.AstronomicalParameterArchive()
