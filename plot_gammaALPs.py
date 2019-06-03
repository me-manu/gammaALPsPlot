# --- Imports ---------------------- #
import matplotlib
import matplotlib.pyplot as plt
from optparse import OptionParser
from glob import glob
from numpy import pi
import yaml
from matplotlib.ticker import MultipleLocator, LogLocator, LogFormatter
from matplotlib.ticker import FixedLocator
import argparse
import yaml
import glob
import numpy as np
from matplotlib.patheffects import withStroke
from math import atan, degrees
# ---------------------------------- #
ga        = lambda m,EN : 1./137. * 1./(2.*np.pi) * (EN - 1.92) * m / 0.006e9
f        = lambda m: 92. * 136. / 10.**(m - 6.) * np.sqrt(z) / (1. + z)
ga1        = lambda m: np.log10(1./(137. * 2 * np.pi * f(m)) * 2./3. * (4. + z)/(1. + z)) + 3.
z        = 0.56

effect = dict(path_effects=[withStroke(foreground="k", linewidth=1.)])
effect_w = dict(path_effects=[withStroke(foreground="w", linewidth=1.)])

def determine_angle_slope(line, ax):
    """
    Determine the angle of a slope in picture coordinates in order to annotate a line with text 
    where text is rotated such that it matches the line's slope

    Parameters
    ----------
    line:        a matplotlib line object
    ax: matplotlib axes object

    Returns
    -------
    angle of line in degrees that can be used for matplolib's annotation rotation keyword

    Notes
    -----
    Adapted from https://matplotlib.org/gallery/text_labels_and_annotations/text_rotation_relative_to_line.html
    """
    x, y = line.get_data()

    sp1 = ax.transData.transform_point((x[0],y[0]))
    sp2 = ax.transData.transform_point((x[-1],y[-1]))

    rise = (sp2[1] - sp1[1])
    run = (sp2[0] - sp1[0])

    return degrees(atan(rise/run))

def axion_line(m,EN = 2 * 1.92):
    """
    Calculate the coupling constant for a given mass for QCD axions

    Parameter:
    ----------
    m: axion mass in eV
    EN: model dependent factor, default: 2 * 1.92 (KVSZ axion)

    Return
    ------
    axion-photon coupling in eV^-1
    """
    return ga(m,EN)

def alp_dm_line(m):
    """
    Return ALP DM line

    Parameter
    ---------
    m: ALP mass in eV

    Returns
    -------
    Upper limit for ALP coupling for DM

    Notes
    -----
    See Arias et al. (2012)
    """
    return 10.**(-14 + 0.25 * np.log10(m))

def my_alp_dm_line(m, theta1 = 1, N = 1):
    """
    Return ALP DM line

    Parameter
    ---------
    m: ALP mass in eV

    Returns
    -------
    Upper limit for ALP coupling for DM

    Notes
    -----
    See Arias et al. (2012)
    """
    return 1. / 137. / (5.3e4) / 2. / np.pi * theta1 * N * np.sqrt(m)

def std_alp_dm_line(m):
    """
    Return standard ALP DM line

    Parameter
    ---------
    m: ALP mass in eV

    Returns
    -------
    Upper limit for ALP coupling for DM

    Notes
    -----
    See Arias et al. (2012)
    """
    return 10.**(-7.5 +  0.5 * np.log10(m))

if __name__ == "__main__":
    usage = "usage: %(prog)s --conf [config file]"
    description = "plot limits from yaml file"
    parser = argparse.ArgumentParser(usage=usage,description=description)
    parser.add_argument('--conf', required = True, help = "Yaml config file")
    parser.add_argument('--limit_col', type = float, default = 0.3, help = "between 0 and 1, limit range of color map" )
    parser.add_argument('--overview', type = int, default = 1, help = "If true, don't plot all labels")
    parser.add_argument('--seed', type = int, help = "Random seed for colors")
    parser.add_argument('--highlight', help = "the limit id to highlight with bright color")
    parser.add_argument('--plotstyles', help="file lists of plotstyles",
                        default = 'config/plotstyles.yaml')
    args = parser.parse_args()
    pars = yaml.load(open(args.conf))
    #lim = np.load(pars['data']).flat[0] 
    with open(pars['data'],'r') as f:
        lim = yaml.load(f)

    fig = plt.figure(figsize = pars['figsize'])
    ax = fig.add_subplot(111)
    ax.set_xscale('log')
    ax.set_yscale('log')

    if args.seed is not None:
        np.random.seed(args.seed)

    try:
        cp_lim = plt.get_cmap(pars['cmap_limit'])
    except ValueError:
        cp_lim = lambda x: pars['cmap_limit']
    try:
        cp_sen = plt.get_cmap(pars['cmap_sens'])
    except ValueError:
        cp_sen = lambda x: pars['cmap_sens']
    try:
        cp_hint = plt.get_cmap(pars['cmap_hint'])
    except ValueError:
        cp_hint = lambda x: pars['cmap_hint']
    try:
        cp_cosmo= plt.get_cmap(pars['cmap_cosmo'])
    except ValueError:
        cp_cosmo = lambda x: pars['cmap_cosmo']

    lw = 0.2
    lwplot = 2.
    ls = '-'

# --- QCD axion line: 
    ma = np.logspace(-20,9.5,100)
    lineQCD, = ax.plot(ma, axion_line(ma), 
            zorder = -8,#label = 'QCD axion', 
            **pars['lineDict']
            )
    ax.fill_between(ma, axion_line(ma, EN = 1.92*3), y2 = axion_line(ma, EN = 1.92*1.1), 
            color = cp_hint(0.5), 
            zorder = -9
            )
    ax.annotate('QCD axion',
        xy = (pars['axion_m'] * pars.get('axion_left',1.),axion_line(pars['axion_m']) * pars.get('axion_over',0.4)), 
        rotation = determine_angle_slope(lineQCD,ax) +  pars.get('angleQCD',-1),
        ha = 'center', va = 'center',
        size = 'x-small',
        zorder = 6.,
        #**effect
        )

# ---- ALP cold DM lines
    ma = np.logspace(-20.,0.,100)
    line, = ax.plot(ma, my_alp_dm_line(ma, N = 1., theta1 = 1.), 
            zorder = 0.1, **pars['lineDict'] 
            )

    ax.annotate('ALP DM', 
        xy = (pars['alp_dm_m'],my_alp_dm_line(pars['alp_dm_m'],
            N = 1., theta1 = 1.) / pars['alp_dm_under']),
        rotation = determine_angle_slope(line, ax) + pars.get('angleALPDM',0.),
        ha = 'center', va = 'center',
        size = 'x-small',
        zorder = 6.,
        **effect_w
        )
    # add arrows to the line: 
    for m in [2e-12,2e-10,2e-8,2e-6]:
        g = my_alp_dm_line(m, N = 1., theta1 = 1.)
        ax.arrow(m, g, 0., -g/3.,  
            fc=pars['lineDict']['color'], ec=pars['lineDict']['color'],
            width = m * 1e-2, head_width = m / 5., head_length = g  / 5.)

# --- alp dm line for pure dm
    #ax.plot(ma, alp_dm_line(ma), 
            #zorder = 0.2, ls = '--'
            #)
# areas to be filled:
    with open(args.plotstyles) as f:
        plotstyles = yaml.load(f)
# plot fermi hole
    # get the patch of the hole
    patch_hole = ax.fill(10.**lim['fermi-lat2']['log_m'], 10.**lim['fermi-lat2']['log_g'],
            closed = True,
            facecolor = 'None',
            edgecolor = '1.',
            zorder = lim['fermi-lat2']['z'],
            lw = lw,
            ls = ls,
            )
    # plot white in the hole
    ax.fill([10.**lim['fermi-lat2']['log_m'].min(), 10.**lim['fermi-lat2']['log_m'].min(),
                10.**lim['fermi-lat2']['log_m'].max(), 10.**lim['fermi-lat2']['log_m'].max()],
            [10.**lim['fermi-lat2']['log_g'].min(), 10.**lim['fermi-lat2']['log_g'].max(),
                10.**lim['fermi-lat2']['log_g'].max(), 10.**lim['fermi-lat2']['log_g'].min()],
            color = '1.',
            zorder =  lim['fermi-lat2']['z'] + 0.1,
            clip_path = patch_hole[0],
            closed = True)

# plot everything else
    for k,v in list(lim.items()):
        if k in plotstyles['sens']:
            fc = cp_sen((np.random.rand(1)[0] - 1.) * args.limit_col + 1.)
            alpha = 0.5
        elif k in plotstyles['hint']:
            fc = cp_hint((np.random.rand(1)[0] - 1.) * args.limit_col + 1.)
            alpha = 0.3
        elif k in plotstyles['cosmo']:
            fc = cp_cosmo((np.random.rand(1)[0] - 1.) * args.limit_col + 1.)
            alpha = 1.
        else:
            fc =  cp_lim((np.random.rand(1)[0] - 1.) * args.limit_col + 1.)
            alpha = 1.

        if k == args.highlight:
            fc = pars.get('highlight', plt.cm.tab10(0.1))
        if not args.overview and not k in pars['skip']:
            ax.annotate(v['label'], xy = v['xylabel'], 
                    color = v['textcolor'],
                    rotation = v['rotation'],
                    fontsize = v.get('textsize','small'),
                    ha = 'center', va = 'center',
                    zorder = v['z'] + 0.1)

        if k in plotstyles['fill'] and not k in pars['skip']:

            for clip_path in [patch_hole[0], None]:
                if k == 'fermi-lat1' and clip_path is not None:
                    continue

                patch = ax.fill(10.**v['log_m'], 10.**v['log_g'],
                    zorder = v['z'] if clip_path is None else \
                        lim['fermi-lat2']['z'] + v['z'] / 10., 
                    closed = True,
                    label = v['label'], 
                    facecolor = fc,
                    edgecolor = '1.',
                    clip_path = clip_path,
                    alpha = alpha, 
                    lw = lw,
                    ls = ls,
                    )

        elif k in plotstyles['fill_between'] and not k in pars['skip']:
            patch = ax.fill_between(10.**v['log_m'],10.**v['log_g'],
                y2 = 1.,
                facecolor = fc,
                alpha = alpha, 
                zorder = v['z'], 
                edgecolor = '1.',
                lw = lw
                )

        elif k in plotstyles['plot'] and not k in pars['skip']:
            patch = ax.plot(10.**v['log_m'],10.**v['log_g'],
                color = fc,
                alpha = alpha, 
                zorder = v['z'], 
                lw = lwplot
                )
        else:
            continue

    v = np.array(pars['bounds']).astype(float)

    ax.tick_params(which = 'both', axis = 'both', direction = 'out')
    expmin =  np.floor(np.log10(v[0]))
    dexp = np.ceil(np.log10(v[1])) - np.floor(np.log10(v[0]))
    expmin_y =  np.floor(np.log10(v[2]))
    dexp_y = np.ceil(np.log10(v[3])) - np.floor(np.log10(v[2]))
    if not args.overview:
        ticks = np.array([])
        step = 1
        for de in range(int(dexp)):
            ticks = np.concatenate((ticks,np.arange(2,10,step) * 10.**(expmin + de)))
        xticks = plt.xticks(10.**np.arange(expmin,expmin +dexp, step))
        ax.xaxis.set_minor_locator(FixedLocator(ticks))
    else:
        step = 2
        xticks = plt.xticks(10.**np.arange(expmin,expmin +dexp, step))
        yticks = plt.yticks(10.**np.arange(expmin_y,expmin_y +dexp_y, step))
        ax.xaxis.set_minor_locator(FixedLocator(10.**np.arange(expmin+1,expmin +dexp, step)))
        ax.yaxis.set_minor_locator(FixedLocator(10.**np.arange(expmin_y+1,expmin_y +dexp_y, step)))
        ax.tick_params(which = 'minor', axis = 'both', labelbottom= False, labelleft = False)

        ax.annotate("LSW", xy = (1e-7,1e-5), fontsize = 'medium',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("Helioscopes", xy = (1e-7,1e-9), fontsize = 'medium',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("Haloscopes", xy = (1e-6,1e-13), fontsize = 'small',
            rotation= 90., 
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("Stellar\nevolution", xy = (1e2,1e-8), fontsize = 'medium',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("Beam dump\nexperiments", xy = (1e6,1e-4), fontsize = 'x-small',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("Cosmological\nprobes", xy = (1e6,1e-13), fontsize = 'medium',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("X-rays / $\gamma$-rays", xy = (1e-11,1e-12), fontsize = 'small',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)
        ax.annotate("WD cooling", xy = (1e0,1e-12), fontsize = 'x-small',
            ha = 'center', va = 'center', color = 'w', zorder = 100,**effect)

    ax.set_xlabel('$m_a$ (eV)', size = 'large')
    ax.set_ylabel('$g_{a\gamma}$ (GeV$^{-1}$)', size = 'large')
    ax.set_xlim(v[0],v[1])
    ax.set_ylim(v[2],v[3])
    #ax.legend(fontsize = 'x-small')
    #plt.show()
    fig.subplots_adjust(left = pars.get('left',0.15),
        bottom = pars.get('left',0.15),
        top = 0.95, right = 0.95)
    fig.savefig('plots/{0:s}.pdf'.format(pars['name']), format = 'pdf')
    fig.savefig('plots/{0:s}.png'.format(pars['name']), format = 'png')
    plt.close("all")
