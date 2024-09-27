import config as cfg
import pandas as pd 
import geopandas as gpd
import logging
# for plotting
import seaborn as sns
import contextily as ctx
import matplotlib.pyplot as plt
# for Moran's I
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
from libpysal.weights import lag_spatial

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

# PLOT INCOME QUANTILES FOR EACH INCOME VARIABLE OF INTEREST -----------------------------------------------------

logger.info(f'Plotting income quantiles for {cfg.INCOME_VARS_OF_INTEREST}...')
for var in cfg.INCOME_VARS_OF_INTEREST:
    fig, ax = plt.subplots(figsize=(12, 8))

    gdf.plot( # plot income var. of interest
        column=var,
        cmap="coolwarm",
        scheme="quantiles",
        k=5, # 5 quantiles
        edgecolor="black",
        linewidth=0.5,
        alpha=0.9,
        legend=True,
        legend_kwds={"loc": "upper left"},
        ax=ax
    )
    
    # Add basemap
    ctx.add_basemap(ax, crs=gdf.crs, source=ctx.providers.OpenStreetMap.Mapnik)
    
    # Set title and remove axis
    ax.set_title(f'Quantiles of {var.lower()}', fontsize=15)
    ax.set_axis_off()
    
    # Save each figure
    if cfg.SAVE_FIGURES:
        fig.savefig(cfg.FIGURES_PATH / f'{var.lower()}_quantiles.png', dpi=300, bbox_inches='tight')

logger.info(f'Income quantiles for {cfg.INCOME_VARS_OF_INTEREST} saved!')

# CALCULATE WEIGHTS ---------------------------------------------------------------------------------------------

logger.info('Calculating spatial weights...')
# Create spatial weights based on adjacency (Queen Contiguity)
w = Queen.from_dataframe(gdf) # TODO: Check details on how to do this properly
w.transform = 'r'

# cardinalities frequency figure
pd.Series(w.cardinalities).plot.hist(color="k");
plt.xlabel('Cardinality')
plt.ylabel('Frequency')
plt.title('Histogram of Cardinalities')

# if cfg.SAVE_FIGURES: # FIXME: This was not being saved correctly
    # plt.savefig(cfg.FIGURES_PATH / 'queen_cardinalities_histogram.png', dpi=300, bbox_inches='tight')

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

logger.info(f'Contiguity weights saved!')

# CALCULATE DIFFERENT MORAN'S I STATS FOR EACH VARIABLE OF INTEREST ---------------------------------------------------------------------------------------------

logger.info(f'Calculating Morans I statistics for the different variables of interest: {cfg.INCOME_VARS_OF_INTEREST}...')
results_list = []

for var in cfg.INCOME_VARS_OF_INTEREST:
    # Global Moran's I
    mi = Moran(gdf[var], w)
    
    # Local Moran's I (LISA)
    lisa = Moran_Local(gdf[var], w)
    
    # Append the results to the new DataFrame
    results_list.append({
        'var': var,
        'global_moran_i': mi.I,
        'global_p_value': mi.p_sim,
        'global_z_score': mi.z_norm,
        'local_moran_i_values': lisa.Is.tolist(),   # Convert array to list
        'local_p_values': lisa.p_sim.tolist(),      # Convert array to list
        'local_z_scores': lisa.z_sim.tolist()       # Convert array to list
    })

morans_i_df = pd.DataFrame(results_list) # for each moran statistic of interest, there's an array with 21 values (number of districts)
if cfg.SAVE_FIGURES:
    morans_i_df.to_csv(cfg.OUTPUTS_PATH / 'morans_i_df.csv', index=False)

logger.info(f'Morans I statistics for {cfg.INCOME_VARS_OF_INTEREST} saved as a dataframe!')

# PLOT LOCAL MORAN'S I. TODO: REVIEW THE CODE, IT IS CONFUSING ---------------------------------------------------------------------------------------------

logger.info('Building and plotting Local Morans I...')

# TODO: Add p-values and z-scores to the graphs!
for var in cfg.INCOME_VARS_OF_INTEREST:
    # Get the corresponding Local Moran's I values from the results DataFrame
    local_moran_values = morans_i_df.loc[morans_i_df['var'] == var, 'local_moran_i_values'].values[0]
    
    # Retrieve global statistics for the current variable
    global_p_value = morans_i_df.loc[morans_i_df['var'] == var, 'global_p_value'].values[0]
    global_z_score = morans_i_df.loc[morans_i_df['var'] == var, 'global_z_score'].values[0]
    global_moran_i = morans_i_df.loc[morans_i_df['var'] == var, 'global_moran_i'].values[0]
    
    # Add the Local Moran's I values to the GeoDataFrame
    gdf[f'lisa_{var.replace(" ", "_").lower()}'] = local_moran_values
    
    # Plot the LISA values for the current variable
    fig, ax = plt.subplots(1, figsize=(6, 6))
    gdf.plot(
        column=f'lisa_{var.replace(" ", "_").lower()}',  # Column containing the LISA values
        cmap='coolwarm',        # Use the coolwarm colormap
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
    
    # Save and show the plot
    if cfg.SAVE_FIGURES:
        plt.savefig(cfg.FIGURES_PATH / f'local_moran_map_{var.replace(" ", "_").lower()}.png', dpi=300, bbox_inches='tight')
    
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

labels = gdf['ID'] # set labels = Madrid districts' IDs 

for var in cfg.INCOME_VARS_OF_INTEREST:
    f, ax = plt.subplots(1, figsize=(6, 6))
    sns.regplot(
        x=f"mean_{var}_std",
        y=f"mean_{var}_lag_std",
        ci=None,
        data=gdf,
        line_kws={"color": "r"},
    )

    for i, txt in enumerate(labels):
        ax.annotate(txt, (gdf[f"mean_{var}_std"].iloc[i], gdf[f"mean_{var}_lag_std"].iloc[i]), fontsize=9, ha='right')
        
    ax.axvline(0, c="k", alpha=0.5)
    ax.axhline(0, c="k", alpha=0.5)
    ax.set_title(f"Moran Plot - {var}")

    if cfg.SAVE_FIGURES:
        plt.savefig(cfg.FIGURES_PATH / f'moran_plot_{var.replace(" ", "_").lower()}.png', dpi=300, bbox_inches='tight')

logger.info(f'Morans Plot for {cfg.INCOME_VARS_OF_INTEREST} saved!')
logger.info('Done!')