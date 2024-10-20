import config as cfg
import pandas as pd 
import geopandas as gpd
import matplotlib.pyplot as plt

# All the addition of the Gini Index to the income data is done under preprocessing.py. Here, I only analyze the Gini Index values

income = gpd.read_file('/Users/caro/Desktop/thesis_project/segregation_indices/data/processed/geometries_and_income.geojson')

fig, ax = plt.subplots(1, figsize=(6, 6))
income.plot(
        column='Gini Index',  # Column containing the LISA values
        cmap='RdPu',        # Use the RdPu colormap
        legend=True,            # Show legend
        ax=ax                   # Axis to plot on
    )
    
    # Set the title with global statistics
ax.set_title('Gini Index Distribution'
    )

    # Remove axis labels
ax.set_axis_off()

if cfg.SAVE_FIGURES:
        plt.savefig(cfg.FIGURES_PATH / f'gini_index_distribution.png', dpi=300, bbox_inches='tight')