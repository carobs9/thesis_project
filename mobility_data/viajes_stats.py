import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import config as cfg

print('Starting')
if cfg.type_of_study == 'month':
    all_viajes = pd.read_csv(cfg.VIAJES_DATA / 'all_viajes_month_0322.csv') # substracting trips in Madrid districts during March 2022
    data_name = 'March 2022'
elif cfg.type_of_study == 'week':
    all_viajes = pd.read_csv('VIAJES/all_viajes_week_0222.csv') # substracting trips in Madrid districts during a 'normal' week
    data_name = 'Normal Week'
else:
    print('No time of study has been set')

df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]

vars_to_plot = ['renta', 'sexo', 'actividad_origen', 'actividad_destino', 'edad', 'distancia']


def plot_and_save_var(df, var_name, palette, save_path):
    """
    Plots the distribution of a variable and saves the figure.

    Parameters:
    - df: DataFrame containing the data.
    - var_name: The name of the variable to plot.
    - palette: Color palette for the plot.
    - save_path: Path to save the figure.
    """
    # Create a new figure for each variable
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plotting the variable
    sns.barplot(
        x=df[var_name].value_counts().index,
        y=df[var_name].value_counts().values,
        palette=palette,
        ax=ax
    )
    ax.set_title(f'{var_name.capitalize()} Distribution\n{data_name}')
    ax.set_xlabel(var_name.capitalize())
    ax.set_ylabel('Count')
    
    # Ensure the directory exists
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the figure
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {save_path}")
    
    # Close the plot to free memory
    plt.close(fig)

print('Plotting and Saving')

# Use a color palette for all plots
palette = sns.color_palette("mako")

# Plot and save filtered dataframe
for var in vars_to_plot:
    save_path = cfg.FIGURES_PATH / f'{var.lower()}_distribution_only_home_origin_{data_name.lower()}.png'
    plot_and_save_var(df, var, palette, save_path)

# Plot and save unfiltered dataframe (including trips with a different origin than home)
for var in vars_to_plot:
    save_path = cfg.FIGURES_PATH / f'{var.lower()}_distribution_{data_name.lower()}.png'
    plot_and_save_var(all_viajes, var, palette, save_path)

print('Done')

