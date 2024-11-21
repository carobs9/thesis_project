import config as cfg
import pandas as pd 
import geopandas as gpd
import logging
import numpy as np
# for plotting
import seaborn as sns
import contextily as ctx
import matplotlib.pyplot as plt
# for Moran's I
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
from libpysal.weights import lag_spatial
from splot.esda import moran_scatterplot, plot_moran

'''
I am calculating Moran's I for mean household rent data (and possibly more types of data, 
like walknig time to amenities or something like that) 
to see if the distribution of rent in the districts of Madrid is dispersed randomly or if there is any clustering.

To calculate Moran's I, I use the PYSAL library to first calculate the weights 
(in this case, Queen, but I need to justify why and do some more research on this).
Then, I apply the Moran's I equation by using a built-in method: mi_income = Moran(merged['Total'], w)

Great source: https://geographicdata.science/book/notebooks/07_local_autocorrelation.html
'''

# Configure general logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Capture all messages from DEBUG and above

# Create a file handler for logging DEBUG and above messages to a file
file_handler = logging.FileHandler('logs/morans_i.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add the handler to the logger
logger.addHandler(file_handler)


logger.info(f'In this script, I plot income quantiles and calculate different Morans I statistics in the city of Madrid for income data from 2021.')
logger.info(f'The variables for which income quantiles and Morans I statistics are calculared are: {cfg.INCOME_VARS_OF_INTEREST}')
logger.info(f'Figures path: {cfg.FIGURES_PATH}')

# READ DATA ------------------------------------------------------------------------------------------------------

logger.info('Reading the data...')
merged = gpd.read_file(cfg.INCOME_DATA / 'geometries_and_income.geojson') # TODO: Fix path
gdf = merged[['ID', 'geometry'] + cfg.INCOME_VARS_OF_INTEREST] # here I select the variable of interest
gdf = gdf.reset_index(drop=True) # reset the index to calculate the weights with no problems
district_mapping = pd.read_csv('/Users/caro/Desktop/thesis_project/data_overview/outputs/districts_and_population.csv')


# CALCULATE WEIGHTS ---------------------------------------------------------------------------------------------

logger.info('Calculating spatial weights...')
# Create spatial weights based on adjacency (Queen Contiguity)
w = Queen.from_dataframe(gdf) # TODO: Check details on how to do this properly
w.transform = 'r' # FIXME: What is this step? is it needed?

# cardinalities frequency figure
pd.Series(w.cardinalities).plot.hist(color="k");
plt.xlabel('Cardinality')
plt.ylabel('Frequency')
plt.title('Histogram of Cardinalities')

if cfg.SAVE_FIGURES: # FIXME: This was not being saved correctly
    plt.savefig(cfg.FIGURES_PATH / 'queen_cardinalities_histogram.png', dpi=300, bbox_inches='tight')

plt.show()

# visual weights figure
f, ax = plt.subplots(1, figsize=(8, 8))
ax = gdf.plot(
    edgecolor="white",     # Edge color
    linewidth=0.5,         
    alpha=0.75,            # Transparency
    ax=ax                  # Axis to plot on
)
# plot weights
w.plot(
    gdf,
    ax=ax,
    edge_kws=dict(linewidth=0.5, color="orangered"),node_kws=dict(marker="*")
)
ax.set_title(f'Queen Contiguity Weights')
ax.set_axis_off()

if cfg.SAVE_FIGURES:
    plt.savefig(cfg.FIGURES_PATH / 'queen_contiguity_weights.png', dpi=300, bbox_inches='tight')

plt.show()

logger.info(f'Contiguity weights saved!')

# CALCULATE GLOBAL MORAN'S I STATS FOR EACH VARIABLE OF INTEREST ---------------------------------------------------------------------------------------------

logger.info(f'Calculating Global Morans I statistics for the different variables of interest: {cfg.INCOME_VARS_OF_INTEREST}...')
np.random.seed(123456)

# Calculate Moran's I for each variable
global_mi = [
    Moran(gdf[variable], w) for variable in cfg.INCOME_VARS_OF_INTEREST
]
# Structure results as a list of tuples
mi_results = [
    (variable, res.I, res.p_sim, res.z_sim)
    for variable, res in zip(cfg.INCOME_VARS_OF_INTEREST, global_mi)
]

global_moran = pd.DataFrame(
    mi_results, columns=["Variable", "Global Morans I", "P-value", "Z-Score"]
).set_index("Variable")

global_moran = global_moran.round(3) # rounding to 2 decimal points

if cfg.SAVE_FIGURES:
    global_moran.to_csv(cfg.OUTPUTS_PATH / 'global_morans_i_df.csv', index=True)


# CALCULATE LOCAL MORAN'S I STATS FOR EACH VARIABLE OF INTEREST ---------------------------------------------------------------------------------------------

local_mi = [
    Moran_Local(gdf[variable], w) for variable in cfg.INCOME_VARS_OF_INTEREST
]

mi_results_local = [
    (variable, res.Is, res.p_sim, res.z_sim, res.q)
    for variable, res in zip(cfg.INCOME_VARS_OF_INTEREST, local_mi)
]

local_moran = pd.DataFrame(
    mi_results_local, columns=["Variable", "Local Morans I","P-value", "Z-Score", "Quadrant"]
).set_index("Variable")

local_moran = local_moran.round(3) # rounding to 2 decimal points

if cfg.SAVE_FIGURES:
    local_moran.to_csv(cfg.OUTPUTS_PATH / 'local_morans_i_df.csv', index=True)


logger.info(f'Local Morans I statistics for {cfg.INCOME_VARS_OF_INTEREST} saved as a dataframe!')


# PLOT LOCAL MORAN'S I. TODO: REVIEW THE CODE, IT IS CONFUSING ---------------------------------------------------------------------------------------------

logger.info('Building and plotting Local Morans I...')

for var in cfg.INCOME_VARS_OF_INTEREST:
    # Get the corresponding Local Moran's I values from the results DataFrame
    local_moran_values = local_moran.loc[local_moran.index == var, 'Local Morans I'].values[0]
    
    # Retrieve global statistics for the current variable
    global_p_value = global_moran.loc[global_moran.index == var, 'P-value'].values[0]
    global_z_score = global_moran.loc[global_moran.index == var, 'Z-Score'].values[0]
    global_moran_i = global_moran.loc[global_moran.index == var, 'Global Morans I'].values[0]
    
    # Add the Local Moran's I values to the GeoDataFrame
    gdf[f'lisa_{var.replace(" ", "_").lower()}'] = local_moran_values
    
    # Plot the LISA values for the current variable
    fig, ax = plt.subplots(1, figsize=(6, 6))
    gdf.plot(
        column=f'lisa_{var.replace(" ", "_").lower()}',  # Column containing the LISA values
        cmap='RdPu',        # Use the RdPu colormap
        legend=True,            # Show legend
        ax=ax                   # Axis to plot on
    )
    
    # Set the title with global statistics
    ax.set_title(
        f"Local Moran's I: {var}\n"
        f"Global Moran's I: {global_moran_i:.4f}, "
        f"p-value: {global_p_value:.4f}, "
        f"z-score: {global_z_score:.4f}",
        fontsize=12
    )
    
    # Optional: Add the global statistics as text on the plot
    textstr = (f"Global Moran's I: {global_moran_i:.4f}\n"
               f"p-value: {global_p_value:.4f}\n"
               f"z-score: {global_z_score:.4f}")
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    # Remove axis labels
    ax.set_axis_off()
    
    if cfg.SAVE_FIGURES:
        plt.savefig(cfg.FIGURES_PATH / f'local_moran_map_{var.replace(" ", "_").lower()}.png', dpi=300, bbox_inches='tight')
    
    plt.show()
    
    # Remove the LISA column to avoid conflicts in the next iteration
    gdf.drop(columns=[f'lisa_{var.replace(" ", "_").lower()}'], inplace=True)

logger.info(f'Local Morans I maps for {cfg.INCOME_VARS_OF_INTEREST} saved!')

# BUILD MORAN'S PLOT ---------------------------------------------------------------------------------------------

logger.info('Building and plotting Morans Plot...')
for var in cfg.INCOME_VARS_OF_INTEREST:
    gdf[f"mean_{var}_std"] = gdf[var] - gdf[var].mean() # calculate mean for each income var. of interest
    gdf[f"mean_{var}_lag_std"] = lag_spatial( # calculate lag for each var. of interest
        w, gdf[f"mean_{var}_std"]
    )
    # Normalize by standard deviation to get deviations in terms of standard deviations
    gdf[f"mean_{var}_z"] = gdf[f"mean_{var}_std"] / gdf[f"mean_{var}_std"].std()
    gdf[f"mean_{var}_lag_z"] = gdf[f"mean_{var}_lag_std"] / gdf[f"mean_{var}_lag_std"].std()

labels = district_mapping.set_index('ID')['name_2'].to_dict()
gdf['label'] = gdf['ID'].map(labels)

for var in cfg.INCOME_VARS_OF_INTEREST:
    f, ax = plt.subplots(1, figsize=(6, 6))
    sns.regplot(
        x=f"mean_{var}_z",
        y=f"mean_{var}_lag_z",
        ci=None,
        data=gdf,
        line_kws={"color": "r"},
    )

    for i, txt in gdf['label'].items():
        ax.annotate(txt, (gdf[f"mean_{var}_z"].iloc[i], gdf[f"mean_{var}_lag_z"].iloc[i]), fontsize=9, ha='right')
        
    ax.axvline(0, c="k", alpha=0.5)
    ax.axhline(0, c="k", alpha=0.5)
    ax.set_title(f"Moran Plot - {var}")

    if cfg.SAVE_FIGURES:
        plt.savefig(cfg.FIGURES_PATH / f'labeled_moran_plot_{var.replace(" ", "_").lower()}.png', dpi=300, bbox_inches='tight')

    plt.show()

for var in cfg.INCOME_VARS_OF_INTEREST:
    f, ax = plt.subplots(1, figsize=(6, 6))
    sns.regplot(
        x=f"mean_{var}_z",
        y=f"mean_{var}_lag_z",
        ci=None,
        data=gdf,
        line_kws={"color": "r"},
    )
        
    ax.axvline(0, c="k", alpha=0.5)
    ax.axhline(0, c="k", alpha=0.5)
    ax.set_title(f"Moran Plot - {var}")

    if cfg.SAVE_FIGURES:
        plt.savefig(cfg.FIGURES_PATH / f'moran_plot_{var.replace(" ", "_").lower()}.png', dpi=300, bbox_inches='tight')

    plt.show()

logger.info(f'Morans Plot for {cfg.INCOME_VARS_OF_INTEREST} saved!')

# BUILD EXTRA MORAN'S PLOT ---------------------------------------------------------------------------------------------

for var, mi in zip(cfg.INCOME_VARS_OF_INTEREST, global_mi):
    # Create a new plot for each Moran's I
    f, ax = plt.subplots(1, figsize=(6, 6))
    
    # Plot the Moran's I scatterplot
    moran_scatterplot(
        mi,  # Pass the current Moran's I
        aspect_equal=True,
        ax=ax  # Pass the current axis
    )

    ax.set_xlabel(f"Attribute: {var}", fontsize=12)
    
    # Save the figure if required
    if cfg.SAVE_FIGURES:
        save_path = cfg.FIGURES_PATH / f'final_moran_plot_{var.replace(" ", "_").lower()}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f'Moran\'s Plot for {var} saved at {save_path}')
    
    # Show the plot if needed (optional)
    plt.show()

for var, mi in zip(cfg.INCOME_VARS_OF_INTEREST, global_mi):
    f, ax = plt.subplots(1, figsize=(6, 6))

    plot_moran(
        mi,
        zstandard=True)
        # Save the figure if required

    if cfg.SAVE_FIGURES:
        save_path = cfg.FIGURES_PATH / f'moran_distrib_{var.replace(" ", "_").lower()}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f'Moran\'s Distrib for {var} saved at {save_path}')

    plt.show()


logger.info('Done!')