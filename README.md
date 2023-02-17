# tuben
Tube model of vocal tract - resonance frequency estimation

## What is it?

Vocal tract tube-to-formant calculation for synthesis of static vowels.
The vocal tract, modelled as a series of cylindrical tube segments, is given by two lists specifying the *length* and *cross-sectional area* of each tube segment, from lips to glottis. 

The program can plot the area function and vocal tract transfer function, and synthesize wav-file with a static vowel. 

The tube-to-formant calculation algorithms are described in

*Liljencrants, J., & Fant, G. (1975). Computer program for VT-resonance frequency calculations. STL-QPSR, 16, 15-21.*

The two methods `determinant` and `phase` should give very similar results, both are included for completeness. 


## Usage
`python tuben.py [-h] [-l LENGTHS] [-a AREAS] [-m METHOD] [-n MAXNRFORMANTS] [-p] [-o OUTPUT]
             [--synt-f0 SYNT_F0] [--synt-dur SYNT_DUR] [-fs SAMPLERATE] [-c C]`

## Examples

Some vowel sounds

`a:`

    python tuben.py --lengths 2,6,6,2 --areas 2,5,0.2,2 -o aa.wav

`o:`
    
    python tuben.py --lengths 2,6,6,2 --areas 0.1,5,1,2 -o oo.wav

`i:` - with plotting

    python tuben.py --lengths 2,6,6,2 --areas 2,0.2,5,2 -o ii.wav --plot


![Example plot](images/plot.png)