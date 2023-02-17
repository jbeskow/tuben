# Tuben
Tube model of vocal tract - resonance frequency estimation

## What is it?

This program will calculate the formant frequencies of a vocal tract and synthesize static vowels. The vocal tract area function is given by two lists specifying the *lengths* and *cross-sectional areas* of a number of straigt tube segments, from lips to glottis. 

The program can plot the area function and vocal tract transfer function, and synthesize a wav-file with a static vowel. 

The tube-to-formant calculation algorithms are from Liljencrantz & Fant (1975). The two methods described (*determinant* and *phase*) should give very similar results, both are included for completeness. 


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

## References

[*Liljencrants, J., & Fant, G. (1975). Computer program for VT-resonance frequency calculations. STL-QPSR, 16, 15-21.*](https://www.speech.kth.se/prod/publications/files/qpsr/1975/1975_16_4_015-020.pdf)