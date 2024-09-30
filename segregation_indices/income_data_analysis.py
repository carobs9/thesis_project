import config as cfg
import geopandas as gpd
# for plotting
import seaborn as sns
import matplotlib.pyplot as plt

'''
Great source: https://geographicdata.science/book/notebooks/07_local_autocorrelation.html
'''

# READ DATA ------------------------------------------------------------------------------------------------------

merged = gpd.read_file(cfg.INCOME_DATA / 'geometries_and_income.geojson') 
gdf = merged[['ID', 'geometry'] + cfg.INCOME_VARS_OF_INTEREST] # here I select the variable of interest
gdf = gdf.reset_index(drop=True) # reset the index to calculate the weights with no problems

# PAIRPLOT: CORRELATION AMONG INCOME VARIABLES -----------------------------------------------------------------------------------------------

_ = sns.pairplot(
    gdf[cfg.INCOME_VARS_OF_INTEREST], kind="reg", diag_kind="kde"
)

# PLOTTING INCOME QUANTILES -----------------------------------------------------------------------------------------------

f, axs = plt.subplots(nrows=2, ncols=3, figsize=(14, 14))
# Make the axes accessible with single indexing
axs = axs.flatten()
# Start a loop over all the variables of interest
for i, col in enumerate(cfg.INCOME_VARS_OF_INTEREST):
    # select the axis where the map will go
    ax = axs[i]
    # Plot the map
    gdf.plot(
        column=col,
        ax=ax,
        scheme="Quantiles",
        k=5, # n quantiles
        legend=True,
        legend_kwds={"loc": "lower left"},
        linewidth=0,
        cmap="RdPu",
    )
    # Remove axis clutter
    ax.set_axis_off()
    # Set the axis title to the name of variable being plotted
    ax.set_title(col)
# Display the figure
plt.show()

if cfg.SAVE_FIGURES:
    f.savefig(cfg.FIGURES_PATH / 'income_quantiles.png', dpi=300, bbox_inches='tight')

