from cantrips import readInDataFromFitsFile
from cantrips import safeSortOneListByAnother
import numpy as np
import scipy.optimize as optimize
import matplotlib.pyplot as plt
import time 

def gaussFunctToMinimizeOld(fit_vars, data, selection_radius, val_to_remove, show = 0):
    #print ('Hi!' )
    x0, y0, sig, A, shift = fit_vars
    #print ('fit_vars = ' + str(fit_vars))  
    #selection_radius = int(sig * n_fwhm_to_fit)
    #print 'selection_radius = ' + str(selection_radius) 
    #print 'int(x0)-selection_radius = ' + str(int(x0)-selection_radius)
    #print 'int(x0)+selection_radius+1 = ' + str(int(x0)+selection_radius+1)
    #print 'int(y0)-selection_radius = ' + str(int(y0)-selection_radius)
    #print 'int(y0)+selection_radius+1 = ' + str(int(y0)+selection_radius+1)
    #print 'np.shape(data) = ' + str(np.shape(data)) 
    fit_counts = data[int(y0)-selection_radius:int(y0)+selection_radius+1, int(x0)-selection_radius:int(x0)+selection_radius+1]
    x_dist_mesh, y_dist_mesh = np.meshgrid(np.array(range(-selection_radius, selection_radius+1)) - (y0 - int(y0)), np.array(range(-selection_radius, selection_radius+1)) - (x0 - int(x0)))
    #print ('data[int(y0), int(x0)] = ' + str(data[int(y0), int(x0)]))
    #print ('[y0, x0] = ' + str([y0, x0]))
    #print ('x_dist_mesh = ' + str(x_dist_mesh))
    #print ('y_dist_mesh = ' + str(y_dist_mesh))
    #print ('fit_counts = ' + str(fit_counts) )
    sqr_rad_mesh = x_dist_mesh ** 2.0 + y_dist_mesh ** 2.0
    #print 'np.shape(sqr_rad_mesh) = ' + str(np.shape(sqr_rad_mesh))
    #print 'np.shape(fit_counts) = ' + str(np.shape(fit_counts))
    sorted_sqr_rads, sorted_counts = safeSortOneListByAnother(sqr_rad_mesh.flatten(), [sqr_rad_mesh.flatten(), fit_counts.flatten()])
    sqr_rads_in_circle = [sorted_sqr_rads[i] for i in range(len(sorted_sqr_rads)) if sorted_sqr_rads[i] <= selection_radius ** 2.0]
    counts_in_circle = [sorted_counts[i] for i in range(len(sorted_sqr_rads)) if sorted_sqr_rads[i] <= selection_radius ** 2.0]

    rd_noise = 5.0
    raw_sigs = (rd_noise + np.sqrt(np.abs(np.array(counts_in_circle) - shift)))
    size_scaled_sigs = ((raw_sigs * np.sqrt(sqr_rads_in_circle)) + 1.0) / np.mean(np.sqrt(sqr_rads_in_circle))
    size_scaled_sigs = [1.0 for sig in size_scaled_sigs]

    vals_from_fit = A * np.exp(- np.array(sqr_rads_in_circle) / (2.0 * sig ** 2.0) ) + shift
    sum_of_sqrs = sum([((counts_in_circle[i] - vals_from_fit[i]) ** 2.0 / size_scaled_sigs[i])  for i in range(len(counts_in_circle)) ])

    #print ('For fit_vars in ' + str(fit_vars) + ', sum_of_sqrs = ' + str(sum_of_sqrs)  )

    if show:
        plt.scatter(np.sqrt(sqr_rads_in_circle), counts_in_circle)
        plt.errorbar(np.sqrt(sqr_rads_in_circle), counts_in_circle, yerr = size_scaled_sigs, fmt = 'none')
        plt.plot(np.linspace(-np.sqrt(max(sqr_rads_in_circle)), np.sqrt(max(sqr_rads_in_circle)), 500), A * np.exp(- np.array(np.linspace(-np.sqrt(max(sqr_rads_in_circle)), np.sqrt(max(sqr_rads_in_circle)), 500) ** 2.0) / (2.0 * sig ** 2.0) ) + shift, c = 'r')
        plt.show() 

    print ('for fit vars ' + str(fit_vars) + ', returning_val = ' + str(sum_of_sqrs - val_to_remove)  )
    #return mean_sum_of_sqrs - val_to_remove
    return sum_of_sqrs - val_to_remove

def gaussFunctToMinimize(fit_vars, data, selection_radius, expected_fwhm_in_pix, val_to_remove, show = 0):
    x0, y0 = fit_vars

    centroid = [x0, y0]
    print ('centroid = ' + str(centroid) )

    data_to_find_max = data[int(centroid[1])-selection_radius:int(centroid[1])+selection_radius+1,
                            int(centroid[0])-selection_radius:int(centroid[0])+selection_radius+1]
    x_dists_mesh, y_dists_mesh = np.meshgrid(np.array(range(-selection_radius, selection_radius+1)),
                                             np.array(range(-selection_radius, selection_radius+1)))
    radius_sqr_mesh = x_dists_mesh ** 2.0 + y_dists_mesh ** 2.0
    radii_sqr = radius_sqr_mesh.flatten()
    data_to_find_max = data_to_find_max.flatten() 
    #point_of_max = np.unravel_index(data_to_find_max.argmax(), data_to_find_max.shape)
    max_val = np.max(data_to_find_max) 
    #x0_guess = point_of_max[0] + int(seed_point[1])-selection_radius
    #y0_guess = point_of_max[1] + int(seed_point[0])-selection_radius
    background_guess = np.median(data_to_find_max)
    init_guess = [expected_fwhm_in_pix, max_val - background_guess, background_guess]
    bounds = [(expected_fwhm_in_pix * 0.05, 0.0, 0.0),
              (selection_radius, np.inf, max_val)]

    raw_sigs = (5.0 + np.sqrt(np.abs(np.array(data_to_find_max) - background_guess)))
    size_scaled_sigs = raw_sigs * (np.sqrt(radii_sqr) + 1) / np.mean(np.sqrt(radii_sqr))

    print ('init_guess = ' + str(init_guess) )
    fit_funct = lambda rs_sqrd, sig, A, shift: A * np.exp(-np.array(rs_sqrd / (2.0 * sig ** 2.0))) + shift  
    best_fit = optimize.curve_fit (fit_funct, radii_sqr, data_to_find_max, p0 = init_guess, bounds = bounds, sigma = size_scaled_sigs)[0]
    #selection_radius = int(sig * n_fwhm_to_fit)
    #print 'selection_radius = ' + str(selection_radius) 
    #print 'int(x0)-selection_radius = ' + str(int(x0)-selection_radius)
    #print 'int(x0)+selection_radius+1 = ' + str(int(x0)+selection_radius+1)
    #print 'int(y0)-selection_radius = ' + str(int(y0)-selection_radius)
    #print 'int(y0)+selection_radius+1 = ' + str(int(y0)+selection_radius+1)
    #print 'np.shape(data) = ' + str(np.shape(data)) 
    fit_counts = data[int(x0)-selection_radius:int(x0)+selection_radius+1, int(y0)-selection_radius:int(y0)+selection_radius+1]
    x_dist_mesh, y_dist_mesh = np.meshgrid(np.array(range(-selection_radius, selection_radius+1)) - (x0 - int(x0)), np.array(range(-selection_radius, selection_radius+1)) - (y0 - int(y0)))
    sqr_rad_mesh = x_dist_mesh ** 2.0 + y_dist_mesh ** 2.0
    #print 'np.shape(sqr_rad_mesh) = ' + str(np.shape(sqr_rad_mesh))
    #print 'np.shape(fit_counts) = ' + str(np.shape(fit_counts))
    sorted_sqr_rads, sorted_counts = safeSortOneListByAnother(sqr_rad_mesh.flatten(), [sqr_rad_mesh.flatten(), fit_counts.flatten()])
    sqr_rads_in_circle = [sorted_sqr_rads[i] for i in range(len(sorted_sqr_rads)) if sorted_sqr_rads[i] <= selection_radius ** 2.0]
    counts_in_circle = [sorted_counts[i] for i in range(len(sorted_sqr_rads)) if sorted_sqr_rads[i] <= selection_radius ** 2.0]

    vals_from_fit = fit_funct(radii_sqr, *best_fit) 
    sum_of_sqrs = sum([(counts_in_circle[i] - vals_from_fit[i]) ** 2.0 for i in range(len(counts_in_circle)) ])
    print ('centroid + best_fit = ' + str(list(centroid) + list(best_fit))) 
    print ('sum_of_sqrs = ' + str(sum_of_sqrs) ) 
    print ('return_val = ' + str(sum_of_sqrs - val_to_remove) )

    #print ('For fit_vars in ' + str(fit_vars) + ', sum_of_sqrs = ' + str(sum_of_sqrs)  )

    if show:
        print ( 'here 1' ) 
        plt.scatter(np.sqrt(radii_sqr), data_to_find_max)
        plt.plot(np.sqrt(radii_sqr), fit_funct(radii_sqr, *best_fit), c = 'r')
        plt.show() 

    #return mean_sum_of_sqrs - val_to_remove

    return ((centroid[0] - 1509.1) ** 2.0 + (centroid[1] - 2171.5) ** 2.0)
    #return (sum_of_sqrs - val_to_remove) 

def determineCenterOfObject(guess_x, guess_y, selection_rad, data, n_iterations, max_iterations):
 
    guess_x = int(guess_x)
    guess_y = int(guess_y)
    selection_rad = int(selection_rad)

    print ('[guess_x, guess_y] = ' + str([guess_x, guess_y])) 

    #print 'val_at_guess_point = ' + str(data[guess_x, guess_y])
    x_dist_mesh, y_dist_mesh = np.meshgrid(range(0, np.shape(data)[1]), range(0, np.shape(data)[0]))
    #print 'x_dist_mesh = ' + str(x_dist_mesh)
    #print 'y_dist_mesh = ' + str(y_dist_mesh)
    #print 'guess_x = ' + str(guess_x)
    #print 'guess_y = ' + str(guess_y)
    #print 'np.shape(data) = ' + str(np.shape(data)) 
    x_dist_mesh = x_dist_mesh[max(0, guess_y - selection_rad):min(np.shape(data)[0], guess_y + selection_rad + 1),
                           max(0, guess_x - selection_rad):min(np.shape(data)[1], guess_x + selection_rad + 1)]
    y_dist_mesh = y_dist_mesh[max(0, guess_y - selection_rad):min(np.shape(data)[0], guess_y + selection_rad + 1),
                              max(0, guess_x - selection_rad):min(np.shape(data)[1], guess_x + selection_rad + 1)]

    line_numbers = range(max(0, guess_y - selection_rad), min(np.shape(data)[0], guess_y + selection_rad + 1))
    col_numbers = range(max(0, guess_x - selection_rad), min(np.shape(data)[1], guess_x + selection_rad + 1))

    data_to_measure = data[max(0, guess_y - selection_rad):min(np.shape(data)[0], guess_y + selection_rad + 1),
                           max(0, guess_x - selection_rad):min(np.shape(data)[1], guess_x + selection_rad + 1)]

    line_profile = np.sum(data_to_measure, axis = 1)
    col_profile = np.sum(data_to_measure, axis = 0)

    line_mean = np.mean(line_profile)
    col_mean = np.mean(col_profile)

    line_centroid = (np.sum(np.array(line_numbers) * np.array([count if count >= line_mean else 0.0 for count in line_profile]))
                     / np.sum(np.array([count for count in line_profile if count >= line_mean]) ) )
    col_centroid = (np.sum(np.array(col_numbers) * np.array([count if count >= col_mean else 0.0 for count in col_profile]))
                    / np.sum(np.array([count for count in col_profile if count >= col_mean]) ) )

    if n_iterations < max_iterations and col_centroid != guess_x and line_centroid != guess_y:
        #print '[col_centroid, line_centroid] = ' + str([col_centroid, line_centroid])
        return determineCenterOfObject(col_centroid, line_centroid, selection_rad, data, n_iterations + 1, max_iterations)
    else:
        return [col_centroid, line_centroid]

    
def computeRadialData(image_file, data_dir, seed_point, expected_fwhm_in_pix,
                      n_fwhm_to_peak = 2, n_fwhm_to_fit = 5, fit_funct = 'gauss', tol = 0.001,
                      max_centroid_iterations = 5, rdnoise = 5.0):
    
    if fit_funct in ['gauss', 'gaussian', 'normal']:
        #fit_funct = gaussFunctToMinimize
        fit_funct = lambda rs_sqrd, sig, A, shift: A * np.exp(-np.array(rs_sqrd / (2.0 * sig ** 2.0))) + shift 

    selection_radius = int(n_fwhm_to_fit * expected_fwhm_in_pix)
    data, header = readInDataFromFitsFile(image_file, data_dir)
    print ('image_file = ' + str(image_file))
    centroid = determineCenterOfObject(seed_point[0], seed_point[1], selection_radius, data, 0, max_centroid_iterations)
    print ('Found centroid = ' + str(centroid)) 

    data_to_find_max = data[int(centroid[1])-selection_radius:int(centroid[1])+selection_radius+1,
                            int(centroid[0])-selection_radius:int(centroid[0])+selection_radius+1]
    x_dists_mesh, y_dists_mesh = np.meshgrid(np.array(range(-selection_radius, selection_radius+1)),
                                             np.array(range(-selection_radius, selection_radius+1)))
    radius_sqr_mesh = x_dists_mesh ** 2.0 + y_dists_mesh ** 2.0
    radii_sqr = radius_sqr_mesh.flatten()
    point_of_max = np.unravel_index(data_to_find_max.argmax(), data_to_find_max.shape)
    data_to_find_max = data_to_find_max.flatten() 
    max_val = np.max(data_to_find_max) 
    x0_guess = point_of_max[0] + int(centroid[1])-selection_radius
    y0_guess = point_of_max[1] + int(centroid[0])-selection_radius
    print ('[x0_guess, y0_guess] = ' + str([x0_guess, y0_guess]) )
    background_guess = np.median(data_to_find_max)
    init_guess = [expected_fwhm_in_pix, max_val - background_guess, background_guess]

    bounds = [(y0_guess - expected_fwhm_in_pix * n_fwhm_to_fit, y0_guess + expected_fwhm_in_pix * n_fwhm_to_fit),
              (x0_guess - expected_fwhm_in_pix * n_fwhm_to_fit, x0_guess + expected_fwhm_in_pix * n_fwhm_to_fit),
              (expected_fwhm_in_pix * 0.05, expected_fwhm_in_pix * n_fwhm_to_fit),
              (0.0, np.inf), 
              (0.0, max_val)]
    #bounds = [(expected_fwhm_in_pix * 0.05, 0.0, 0.0),
    #          (expected_fwhm_in_pix * n_fwhm_to_fit, np.inf, max_val)]
    #print ('init_guess = ' + str(init_guess))
    #print ('bounds = ' + str(bounds) )
    start = time.time()
    #init_sum_of_sqrs = gaussFunctToMinimize(centroid, data, 0.0, show = 1)
    init_sum_of_sqrs = gaussFunctToMinimizeOld(list([y0_guess, x0_guess]) + list(init_guess), data, selection_radius, 0.0, show = 1) 
    print ('init_sum_of_sqrs = ' + str(init_sum_of_sqrs)) 
    
    #older style where I allowed the position of the star center to be varied during the fit.  It was a bit more advance, but could be made to work.
    # Left here, just in case I end up needing it sometime/somewhere. 
    #best_fit = optimize.minimize(gaussFunctToMinimize, centroid + init_guess, args = (data, selection_radius, expected_fwhm_in_pix, init_sum_of_sqrs), tol = tol, bounds = bounds, method = 'L-BFGS-B')['x']
    print ('bounds = ' + str(bounds))
    print ('list([y0_guess, x0_guess]) + list(init_guess) = ' + str(list([y0_guess, x0_guess]) + list(init_guess)))
    print (('Here 1'))
    optimize.minimize(gaussFunctToMinimizeOld, list([y0_guess, x0_guess]) + list(init_guess), args = (data, selection_radius, init_sum_of_sqrs), tol = tol, bounds = bounds, method = 'L-BFGS-B')['x']
    best_fit = optimize.minimize(gaussFunctToMinimizeOld, list([y0_guess, x0_guess]) + list(init_guess), args = (data, selection_radius, init_sum_of_sqrs), tol = tol, bounds = bounds, method = 'L-BFGS-B')['x']
    print ('Here 2')
    
    
    final_sum_of_sqrs = gaussFunctToMinimizeOld(best_fit, data, selection_radius, 0.0, show = 1)
    print ('for best_fit = ' + str(best_fit) + ', sum_of_sqrs = ' + str(final_sum_of_sqrs) )
    
    #print ('init_guess = ' + str(init_guess)
    #print ('bounds = ' + str(bounds)
    #We determine the unce
    raw_sigs = (5.0 + np.sqrt(np.abs(np.array(data_to_find_max) - background_guess)))
    size_scaled_sigs = raw_sigs * (np.sqrt(radii_sqr) + 1) / np.mean(np.sqrt(radii_sqr))
    #print 'np.shape(size_scaled_sigs) = ' + str(np.shape(size_scaled_sigs))
    #print 'size_scaled_sigs = ' + str(size_scaled_sigs)
    #print 'np.min(size_scaled_sigs) = ' + str(np.min(size_scaled_sigs))
    #best_fit = optimize.curve_fit (fit_funct, radii_sqr, data_to_find_max, p0 = init_guess, bounds = bounds, sigma = size_scaled_sigs)[0]
    end = time.time()
    print ('Took ' + str(end - start) + 's to optimize.' ) 
    print ('best_fit = ' + str(best_fit) )
    #plt.scatter(np.sqrt(radii_sqr), data_to_find_max)
    #plt.errorbar(np.sqrt(radii_sqr), data_to_find_max, yerr = size_scaled_sigs, fmt = 'none')
    #plt.plot(np.linspace(0.0, max(np.sqrt(radii_sqr)), 201), fit_funct(np.linspace(0.0, max(np.sqrt(radii_sqr)), 201) ** 2.0, *init_guess), c = 'b')
    #plt.plot(np.linspace(0.0, max(np.sqrt(radii_sqr)), 201), fit_funct(np.linspace(0.0, max(np.sqrt(radii_sqr)), 201) ** 2.0, *best_fit), c = 'r')
    #plt.show() 
    end = time.time()
    #print ('Took ' + str(end - start) + 's')
    #print ('best_fit = ' + str(best_fit)) 

    #gaussFunctToMinimize(best_fit, data, selection_radius, show = 1)
    sig = best_fit[2]
    fwhm = 2.0 * np.sqrt(np.log(2) * 2) * sig
    print ('fwhm = ' + str(fwhm) )  
    
    return fwhm 
