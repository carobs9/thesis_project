import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import config as cfg

print('Starting')
if cfg.type_of_study == 'month':
    all_viajes = pd.read_csv(cfg.VIAJES_DATA / 'all_viajes_month_0322.csv', thousands='.',decimal=',')  # Subtracting trips in Madrid districts during March 2022
    data_name = 'March 2022'
elif cfg.type_of_study == 'week':
    all_viajes = pd.read_csv(cfg.VIAJES_DATA / 'viajes_week_0322.csv', thousands='.',decimal=',')  # Subtracting trips in Madrid districts during a 'normal' week
    data_name = 'Normal Week'
elif cfg.type_of_study == 'two_weeks':
    all_viajes = pd.read_csv(cfg.VIAJES_DATA / 'viajes_two_week_0322.csv', thousands='.',decimal=',')  # Subtracting trips in Madrid districts during 2 weeks
    data_name = 'Two Weeks'
else:
    raise ValueError('No time of study has been set')

# Filter for trips originating at home
df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]

vars_to_plot = ['renta', 'sexo', 'actividad_origen', 'actividad_destino', 'edad', 'distancia']


def plot_and_save_var(df, var_name, palette, save_path):
    """
    Plots the distribution of viajes for a variable and saves the figure.

    Parameters:
    - df: DataFrame containing the data.
    - var_name: The name of the variable to plot.
    - palette: Color palette for the plot.
    - save_path: Path to save the figure.
    """
    # Group by the variable and sum viajes
    grouped = df.groupby(var_name)['viajes'].sum().reset_index()
    grouped = grouped.sort_values(by='viajes', ascending=False)

    # Create a new figure for each variable
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plotting the variable
    sns.barplot(
        x=grouped[var_name],
        y=grouped['viajes'],
        palette=palette,
        ax=ax
    )
    ax.set_title(f'{var_name.capitalize()} Distribution (viajes)\n{data_name}')
    ax.set_xlabel(var_name.capitalize())
    ax.set_ylabel('Sum of Viajes')
    
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

# Plot and save filtered dataframe (only home-origin trips)
for var in vars_to_plot:
    save_path = cfg.FIGURES_PATH / f'{var.lower()}_distribution_only_home_origin_{data_name.lower()}.png'
    plot_and_save_var(df, var, palette, save_path)

# Plot and save unfiltered dataframe (including trips with a different origin than home)
for var in vars_to_plot:
    save_path = cfg.FIGURES_PATH / f'{var.lower()}_distribution_{data_name.lower()}.png'
    plot_and_save_var(all_viajes, var, palette, save_path)

print('Done')
