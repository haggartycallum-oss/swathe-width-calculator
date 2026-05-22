# import libraries
import numpy as np
import matplotlib as mpl
import scipy as sp
import matplotlib.pyplot as plt  #loaded in a sub module 


def checkDishLimits(az,el,maxDishAngle):
    compAngle = np.arccos((np.cos(el))*(np.cos(az)))
    withinLimits = compAngle<= maxDishAngle
    return withinLimits

#define scan parameters
ramp_period_full   = 380e-6                    #seconds
ramp_period_active = 310e-6                    #seconds
wavelength         = 0.003                     #metres
velocity           = 240                       #m/s
imageWidth         = np.array([246,512])       #pixels
Range              = np.arange(1750, 3050, 50) #metres
altitude           = 950                       #metres
beamWidth          = np.deg2rad(1.2)           #rad

#define servo requirements
maxDishAngle       = np.deg2rad(30) #rad
servoRateLimit     = 4              #rad/s

#define target (MLRS) ans subsequent Johnson's criteria
extent             = 6.97 #metres
J_crit_recog       = 12   #pixels
J_crit_detect      = 2    #pixels

CRR_recog          = extent/J_crit_recog               #m/pix
CRR_detect         = extent/J_crit_detect              #m/pix
CRR                = np.array([CRR_recog, CRR_detect]) #m/pix

#initialise parameters for array
Swathe_Width = np.zeros((len(Range),3,2))
Squint_angle = np.zeros((len(Range),3,2))
beam_Height  = np.zeros((len(Range),3,2))
maxangle     = np.zeros((len(Range),3,2))
SwathEnd     = np.zeros((len(Range),3,2))
SwathStart   = np.zeros((len(Range),3,2))
for nJcrit in range(2):
    for iImageWidth, Img in enumerate(imageWidth):
        imageIntegrationTime = Img * ramp_period_full
        coverageRate = beamWidth / imageIntegrationTime
        for iRange, r in enumerate(Range):
            #use trig to calculate look down and squint angles
            LD_angle = np.arcsin(altitude/r)
            Sq_angle = np.arcsin((wavelength*r)/(2*velocity*ramp_period_full*Img*CRR[nJcrit]*np.cos(LD_angle)))

            verticalRange = r*np.cos(Sq_angle)

            #calculate max time to scan from velocity and beam footprint height
            beamBottom = 1000*np.tan(0.5*np.pi-LD_angle - 0.5*beamWidth)
            beamTop    = 1000*np.tan(0.5*np.pi-LD_angle + 0.5*beamWidth)
            beamHeight = beamTop - beamBottom

            #calculate time taken to travel forward in one beam hight
            scanTime = (beamHeight/velocity)/2

            #from the max beam speed and time determine the max sweep angle
            max_sweep_angle = scanTime*coverageRate
            if checkDishLimits(max_sweep_angle+Sq_angle, LD_angle,maxDishAngle):
                #if within dish limits calculate swathe width as normal calculate R2 (range at edge of swathe)
                R2 = np.hypot(verticalRange,r*np.sin(Sq_angle + max_sweep_angle))

                Swathe_Width[iRange,iImageWidth,nJcrit] = R2*np.sin(Sq_angle + max_sweep_angle) - Range[iRange]*np.sin(Sq_angle) + 2*r*np.sin(beamWidth/2)
                SwathEnd[iRange,iImageWidth,nJcrit] =R2*np.sin(Sq_angle + max_sweep_angle)+ 2*Range[iRange]*np.sin(beamWidth/2)
                SwathStart[iRange,iImageWidth,nJcrit] = Range[iRange]*np.sin(Sq_angle)
            elif checkDishLimits(Sq_angle,  LD_angle, maxDishAngle):
                
                #else calculate swath width based on dish limits -
                #calculate new max sweep angle
                max_sweep_angle = np.arccos(np.cos(maxDishAngle)/np.cos(LD_angle)) - Sq_angle
                #calculate R2 (range at edge of swathe)
                R2 = np.hypot(verticalRange,Range[iRange]*np.sin(Sq_angle))

                Swathe_Width[iRange,iImageWidth,nJcrit] = R2*np.sin(Sq_angle + max_sweep_angle) - Range[iRange]*np.sin(Sq_angle) + 2*Range[iRange]*np.sin(beamWidth/2);
                SwathEnd[iRange,iImageWidth,nJcrit] =R2*np.sin(Sq_angle + max_sweep_angle)+ 2*Range[iRange]*np.sin(beamWidth/2)
                SwathStart[iRange,iImageWidth,nJcrit] = Range[iRange]*np.sin(Sq_angle)
            else:

                #if the squint angle puts us outside dish limits set to 0
                
                Swathe_Width[iRange,iImageWidth,nJcrit] =0
                SwathEnd[iRange,iImageWidth,nJcrit] =0
                SwathStart[iRange,iImageWidth,nJcrit] = 0
#plot results
print(Swathe_Width)

import matplotlib.pyplot as plt

# define labels for the 4 combinations
labels = [
    f'W={imageWidth[0]}px, Detect',
    f'W={imageWidth[0]}px, Recog',
    f'W={imageWidth[1]}px, Detect',
    f'W={imageWidth[1]}px, Recog',
]
colours = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']

# --- Figure 1: Swathe Width vs Range ---
fig1, ax1 = plt.subplots()
for iImageWidth in range(len(imageWidth)):
    for nJcrit in range(2):
        idx = iImageWidth * 2 + nJcrit
        ax1.plot(Range, Swathe_Width[:, iImageWidth, nJcrit],
                 color=colours[idx], label=labels[idx])

ax1.set_xlabel('Range (m)')
ax1.set_ylabel('Swathe Width (m)')
ax1.set_title('Swathe Width vs Range')
ax1.legend()
ax1.grid(True)

# --- Figure 2: Swath Start and End vs Range ---
fig2, ax2 = plt.subplots()
for iImageWidth in range(len(imageWidth)):
    for nJcrit in range(2):
        idx = iImageWidth * 2 + nJcrit
        ax2.plot(Range, SwathStart[:, iImageWidth, nJcrit],
                 color=colours[idx], linestyle='--', label=f'{labels[idx]} start')
        ax2.plot(Range, SwathEnd[:, iImageWidth, nJcrit],
                 color=colours[idx], linestyle='-', label=f'{labels[idx]} end')

ax2.set_xlabel('Range (m)')
ax2.set_ylabel('Cross-range position (m)')
ax2.set_title('Swath Start and End vs Range')
ax2.legend()
ax2.grid(True)

plt.show()

            

            








