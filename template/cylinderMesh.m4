/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.2.0                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.2;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
changecom(//)changequote([,])
define(calc, [esyscmd(perl -e 'printf ($1)')])
define(VCOUNT, 0)
define(vlabel, [[// ]Vertex $1 = VCOUNT define($1, VCOUNT)define([VCOUNT], incr(VCOUNT))])

convertToMeters 1.0;


define(D, 3000) // Diameter 560
define(H, 300) // Height
define(S, 1000) //Width of middle square section 360
define(NPS, 80) // Number of cells in the square section
define(NPD, 25) // Number of cells from square section to perimeter
define(NPZ, 40) // Number of cells from top to bottom
define(G, 5) // Grading of cylinder part
define(GZ,15) // Grading of height

define(PI, 3.14159265)
define(R, calc(D/2))
define(Rsq, calc(0.5*1.15*S))
define(CW, calc(S/2))
define(CX, calc(R*cos((PI/180)*45)))
define(CZ, calc(R*sin((PI/180)*45)))


vertices
(
 ( CW -CW 0.0) vlabel(sesqb)
 (-CW -CW 0.0) vlabel(swsqb)
 (-CW  CW 0.0) vlabel(nwsqb)
 ( CW  CW 0.0) vlabel(nesqb)

 ( CX -CZ 0.0) vlabel(secb)
 (-CX -CZ 0.0) vlabel(swcb)
 (-CX  CZ 0.0) vlabel(nwcb)
 ( CX  CZ 0.0) vlabel(necb)

 ( CW -CW H) vlabel(sesqt)
 (-CW -CW H) vlabel(swsqt)
 (-CW  CW H) vlabel(nwsqt)
 ( CW  CW H) vlabel(nesqt)

 ( CX -CZ H) vlabel(sect)
 (-CX -CZ H) vlabel(swct)
 (-CX  CZ H) vlabel(nwct)
 ( CX  CZ H) vlabel(nect)
);				

blocks
(
 hex ( swsqb sesqb nesqb nwsqb swsqt sesqt nesqt nwsqt) (NPS NPS NPZ) simpleGrading (1 1 GZ)
 hex ( swcb secb sesqb swsqb swct sect sesqt swsqt) (NPS NPD NPZ) simpleGrading (1 calc(1.0/G) GZ)
 hex ( swsqb nwsqb nwcb swcb swsqt nwsqt nwct swct) (NPS NPD NPZ) simpleGrading (1 G GZ)
 hex ( nwsqb nesqb necb nwcb nwsqt nesqt nect nwct) (NPS NPD NPZ) simpleGrading (1 G GZ)
 hex ( nesqb sesqb secb necb nesqt sesqt sect nect) (NPS NPD NPZ) simpleGrading (1 G GZ)
);

edges
(
 arc secb swcb (0.0 -R 0.0)
 arc swcb nwcb (-R 0.0 0.0)
 arc nwcb necb (0.0 R 0.0)
 arc necb secb (R 0.0 0.0)

 arc sesqb swsqb (0.0 -Rsq 0.0)
 arc swsqb nwsqb (-Rsq 0.0 0.0)
 arc nwsqb nesqb (0.0 Rsq 0.0)
 arc nesqb sesqb (Rsq 0.0 0.0)

 arc sect swct (0.0 -R H)
 arc swct nwct (-R 0.0 H)
 arc nwct nect (0.0 R H)
 arc nect sect (R 0.0 H)

 arc sesqt swsqt (0.0 -Rsq H)
 arc swsqt nwsqt (-Rsq 0.0 H)
 arc nwsqt nesqt (0.0 Rsq H)
 arc nesqt sesqt (Rsq 0.0 H)


);

patches
(
 wall terrain
 (
  (sesqb nesqb nwsqb swsqb)
  (sesqb secb necb nesqb)
  (secb sesqb swsqb swcb)
  (swsqb nwsqb nwcb swcb)
  (nesqb necb nwcb nwsqb)
 )

 patch top
 (
  (sesqt nesqt nwsqt swsqt)
  (sesqt sect nect nesqt)
  (sect sesqt swsqt swct)
  (swsqt nwsqt nwct swct)
  (nesqt nect nwct nwsqt)
 )

 patch sides
 (
  (swcb secb sect swct)
  (swcb swct nwct nwcb)
  (nwcb nwct nect necb)
  (necb nect sect secb)
 )

);
