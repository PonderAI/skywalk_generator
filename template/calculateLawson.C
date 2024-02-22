#include "fvCFD.H"

int main(int argc, char *argv[])
{

#include "setRootCase.H"
#include "createTime.H"
#include "createMesh.H"

enum category {SIT, STAND, WALK, BUSINESS, UNACCEPTABLE};

volScalarField COMFORT
(
    IOobject
    (
        "C",
        "0",
        mesh
    ),
    mesh,
    dimensionedScalar("0", dimless, 0)
);


volScalarField SITEXCEED
(
    IOobject
    (
        "SITEXCEED",
        "0",
        mesh
    ),
    mesh,
    dimensionedScalar("0", dimless, 0)
);

volScalarField STANDEXCEED
(
    IOobject
    (
        "STANDEXCEED",
        "0",
        mesh
    ),
    mesh,
    dimensionedScalar("0", dimless, 0)
);

volScalarField WALKEXCEED
(
    IOobject
    (
        "WALKEXCEED",
        "0",
        mesh
    ),
    mesh,
    dimensionedScalar("0", dimless, 0)
);

volScalarField BUSINESSEXCEED
(
    IOobject
    (
        "BUSINESSEXCEED",
        "0",
        mesh
    ),
    mesh,
    dimensionedScalar("0", dimless, 0)
);



const int ndir = 8;
word dirs[ndir] = {"0", "45", "90", "135", "180", "225", "270", "315"};
const int ncat = 5;
const float USIM = 5.0;
const float windbin[ncat] = {0,4.0, 6.0, 8.0, 10.0};
//                  cat dir
const float windfreq[4][8] = 
    { 
        {10.4,11.08,14.1,15.18,13.08,8.02,10.2,11.4},
        {0.48,0.11,0.1,1.53,1.9,0.4,0.38,0.92},
        {0.05,0.01,0.02,0.22,0.27,0.036,0.024,0.1},
        {0.005,0.0008,0.0004,0.02,0.016,0.004,0.004,0.01}
    };


// For each wind direction
for (int idir=0; idir<ndir; idir++) {
    Info<< "Reading velocity magnitude for direction " << dirs[idir] << endl;

    // Load CFD result
    volScalarField magU
    (
        IOobject
        (
            "mag(U)",
            dirs[idir],
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

    // For each cell
    forAll(mesh.C(), celli) 
    { 
        float freq; float low; float high; float mid; float scale_factor; float ulocal;
        // For each wind category
        for (int icat=0; icat<ncat-1; icat++) 
        {
            // Get the overall frequency
            freq = windfreq[icat][idir];

            // Calculate locally scaled velocity
            low = windbin[icat];
            high = windbin[icat+1];
            mid = high; //0.5*(low + high);
            scale_factor = mid/USIM; // TODO test å bruke upper limit istedet for midten

            ulocal = magU[celli]*scale_factor;

            // Accumulate frequencies
            if (ulocal >= 4.0) 
                SITEXCEED[celli] += freq;
            if (ulocal >= 6.0)
                STANDEXCEED[celli] += freq;
            if (ulocal >= 8.0)
                WALKEXCEED[celli] += freq;
            if (ulocal >= 10.0)
                BUSINESSEXCEED[celli] += freq;

        }
    } 
}


// Determine comfort in each cell
forAll(mesh.C(), celli) 
{
    if (BUSINESSEXCEED[celli] > 5.0) {
        COMFORT[celli] = UNACCEPTABLE;
    } else if (WALKEXCEED[celli] > 5.0) {
        COMFORT[celli] = BUSINESS;
    } else if (STANDEXCEED[celli] > 5.0) {
        COMFORT[celli] = WALK;
    } else if (SITEXCEED[celli] > 5.0) {
        COMFORT[celli] = STAND;
    } else {
        COMFORT[celli] = SIT;
    }
}

SITEXCEED.write();
STANDEXCEED.write();
WALKEXCEED.write();
BUSINESSEXCEED.write();
COMFORT.write();
/*  Info<< "Reading field u\n" << endl; */

/* volScalarField u */
/* ( */
/*     IOobject */
/*     ( */
/*         "u", */
/*         runTime.timeName(), */
/*         mesh, */
/*         IOobject::MUST_READ, */
/*         IOobject::AUTO_WRITE */
/*     ), */
/*     mesh */
/* ); */

/* forAll(mesh.C(), celli) */ 
/* { */ 
/*     scalar x = mesh.C()[celli].component(0); */ 
/*     scalar y = mesh.C()[celli].component(1); */ 
/* } */ 

Info<< "Done." << endl;

}
