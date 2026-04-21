# GUI and 3D Printing

## Running from source code

`python Tuben_new.py`

## TubeN2.0

<img height="350" src="plots\GUI.png" width="500"/>

### Functions

#### Add
<img height="200" src="plots\1Add.png" width="300"/>

Example [a]:\
1.5,0.5,3.5,0.5,0.5,0.5,0.5,0.5,1,0.5,0.5,0.5,0.5,1,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5\
5,6.5,8,6.5,5,4,3.2,1.6,2.6,2,1.6,1.3,1,0.65,1,1.6,2.6,4,1,1.3,1.6,2.6

Users can either manually enter the lengths and areas or load a .txt file following the same format.\
The Add function also supports inserting new segments into an existing tube.
If a segment is selected with the left mouse button, the new segment(s) will be inserted after the selected one;
otherwise, they will be added to the end of the tube.

#### Remove & Alter
Remove and Alter buttons follow a similar interaction logic as Add,
use mouse to select a segment and click Remove to remove it,
or click Alter to edit the length and area of the segment.

Or the user can use Tab key to go through all the segments in the existing tube and use arrow keys to edit the
length and area of any selected tube segment.

The information of the selected segment will be shown in the Operational Information
window.

<img height="350" src="plots\2Tab.png" width="500"/>

#### Obliviate
Clear everything

#### Illustrate
Illustrate allows the user to generate an image of the tube area function, peak function, and (or) transfer function,
each plot can be generated independently.

<img height="400" src="plots\3Illustration.png" width="340"/>

#### /a/ /i/ /u/
Example vowel configurations for demonstration purposes.

#### 3D File
Generate 3d printable file (.stl) with continuous or detachable form. Manual can be found in the repository.