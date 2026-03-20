#Tardis imports
from tardis import run_tardis
from tardis.visualization.tools.sdec_plot import SDECPlotter
from tardis.visualization.tools.liv_plot import LIVPlotter
from tardis.io.atom_data.base import AtomData
from tardis.io.configuration.config_reader import Configuration

#Bug patch, to avoid QtAgg on Wayland Arch Linux, as that crashes
import matplotlib
matplotlib.use("Agg")

#Misc. imports 
import matplotlib.pyplot as plt
from pathlib import Path
import argparse


###
# Import function for the atomic data. Since I am using 
# AtomData.from_hdf(), I assume atom_input is either a path
# to an atomic-data HDF5 file, a name of an atom-data file known
# to TARDIS, or an already loaded Atomdata object
###
def import_atomic(atom_input):

    if isinstance(atom_input, AtomData):
        return atom_input
    
    if atom_input is None:
        raise ValueError("atom_input is empty/None")

    try:
        return AtomData.from_hdf(Path(atom_input))
    except Exception as e:
        raise ValueError(f"Could not load atomic data from {atom_input!r}. Expected a TARDIS HDF5 atomic-data file path or a known atom-data name.") from e


###
# Import function for config yml. I'm adding the same level
# of import protection as for import_atomic(), and while it
# is not bulletproof, it should make it easier to debug
###
def import_config(config_input):
    if isinstance(config_input, Configuration):
        return config_input

    if config_input is None:
        raise ValueError("config_input cannot be None")

    try:
        return Configuration.from_yaml(Path(config_input))
    except Exception as e:
        raise ValueError(f"Could not load TARDIS config from {config_input!r}. Expected a valid TARDIS YAML configuration file.") from e

###
# The spectrum plotter from the quickstart notebook, which I have
# gracefully stolen and repurposed ("reporposed"? idk)
###
def plot_spectrum(sim):
    spectrum = sim.spectrum_solver.spectrum_real_packets
    spectrum_virtual = sim.spectrum_solver.spectrum_virtual_packets
    spectrum_integrated = sim.spectrum_solver.spectrum_integrated

    plt.figure(figsize=(10, 6.5))

    spectrum.plot(label="Normal packets", color = "black", alpha=0.9)
    spectrum_virtual.plot(label="Virtual packets", color="cyan", alpha=0.5)
    spectrum_integrated.plot(label='Formal integral', color="gold")

    plt.xlim(500, 9000)
    plt.title("TARDIS example model spectrum")
    plt.xlabel(r"Wavelength [$\AA$]")
    plt.ylabel(r"Luminosity density [erg/s/$\AA$]")
    plt.legend()

    plt.savefig("Simulated_spectrum.png", dpi=300)

def SDec_plot(sim):
    sdec = SDECPlotter.from_simulation(sim)
    ax = sdec.generate_plot_mpl(packets_mode="virtual", nelements=8)
    ax.figure.savefig("quickstart_sdec.png", dpi=300, bbox_inches="tight")

def LIV_plot(sim):
    liv = LIVPlotter.from_simulation(sim)
    ax = liv.generate_plot_mpl(nelements=8)
    ax.figure.savefig("quickstart_liv.png", dpi=300, bbox_inches="tight")


###
# Simple CLI to make it easier to run as a standalone script. A bit cosmetic
# but it makes it easier to verify that it is working.
###
def main():
    parser = argparse.ArgumentParser(
        description="Simple plotting script for plotting SDec and LIV plots to compliement simulated spectra."
    )
    parser.add_argument("--atomic_data", required=True, help="Input atomic data for the simulation. Accepts PATH, filename and AtomData object.")
    parser.add_argument("--config", required=True, help="Input TARDIS config file for the simulation. Accepts PATH and Configuration object.")
    
    args = parser.parse_args()
    print(args)


    # Run the simulation itself, no widgets as I run the script in terminal
    # when bugtesting
    sim = run_tardis(config=args.config, atom_data=args.atomic_data, virtual_packet_logging=True, show_convergence_plots=False, display_logging_widget=False)
    plot_spectrum(sim)


if __name__ == "__main__":
    main()