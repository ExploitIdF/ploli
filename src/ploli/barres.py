import pandas as pd
import numpy as np
import matplotlib.pyplot
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def liste_lignes_barres(
  df, # x_var,y_var,val
  xlen, #cm
  ylen,
  titre_graph="titre",  
  nom_fich='graph.jpg'  
):
  """
  Variables :
  def liste_lignes_barres(
    df, # x_var,y_var,val
    xlen, #cm
    ylen,
    titre_graph="titre",  
    nom_fich='graph.jpg'  
  ):
  
  
  """
  if len(df.columns)!=3:
    return "Il faut 3 colonnes  !"
  df.columns=['x_var','y_var','val']
  v1_values = df['x_var'].unique()
  v2_values = df['y_var'].unique()
  nb1=len(v1_values)
  nb2=len(v2_values)

  max_per_v2 = (df.groupby('y_var')['val'].max()) #
  max_sum=max_per_v2.sum()
  max_per_v2 =(max_per_v2 + max_sum/3/nb2).reset_index()
  max_per_v2.columns = ['y_var', 'max_val']
  # Normalisation pour hauteur totale de ylen cm
  total_max_height = max_per_v2['max_val'].sum()
  normalization_factor = ylen / total_max_height
  df['val_norm'] = df['val'] * normalization_factor
  max_per_v2['max_val_norm'] = max_per_v2['max_val'] * normalization_factor

  # Création du graphique
  fig, ax = matplotlib.pyplot.subplots(figsize=(xlen/2.54, ylen/2.54))  # conversion cm en inches

  # Position y cumulative pour chaque v2
  y_positions = {}
  current_y = 0
  for idx, row in max_per_v2.iterrows():
      y_positions[row['y_var']] = current_y
      current_y += row['max_val_norm']
  larBande=3
  for i in range(int(nb1/6)+1):
    rect=Rectangle((2*i*larBande,0),larBande,ylen,facecolor='#fdd' )
    ax.add_patch(rect)
  # Tracer les lignes horizontales (hauteur = max(val))
  for v2, y_pos in y_positions.items():
      max_height = max_per_v2[max_per_v2['y_var'] == v2]['max_val_norm'].values[0]
      ax.plot([0, len(v1_values)], [y_pos + max_height, y_pos + max_height],
              '#f00', linewidth=.5, alpha=0.4)

      # Tracer les barres rouges pour chaque x_var
      v2_data = df[df['y_var'] == v2].sort_values('x_var')
      for i, (_, row) in enumerate(v2_data.iterrows()):
          bar_width = 0.8
          rect = Rectangle((i + 0.1, y_pos), bar_width, row['val_norm'],
                          facecolor='red', edgecolor='darkred', alpha=0.7)
          ax.add_patch(rect)

  # Configuration des axes
  ax.set_xlim(0, len(v1_values))
  ax.set_ylim(0, ylen)
  #ax.set_xlabel('Mois', fontsize=10)
  ax.set_title(titre_graph, fontsize=12)

  # Étiquettes v1
  ax.set_xticks(np.arange(len(v1_values)) + 0.5)
  ax.set_xticklabels(v1_values, rotation=45, ha='right', fontsize=8)

  # Ajouter les étiquettes v2 sur l'axe y
  yticks=[]
  for v2, y_pos in y_positions.items():
      max_height = max_per_v2[max_per_v2['y_var'] == v2]['max_val_norm'].values[0]
      yticks.append(y_pos + max_height/4)
  ax.set_yticks(yticks)
  ax.set_yticklabels(v2_values, rotation=10, ha='right', fontsize=8)
  ax.grid(False)
  plt.tight_layout()
  plt.savefig(nom_fich, dpi=300, bbox_inches='tight')
  plt.show()

def plot_grouped_bars(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    val_col: str,
    xlen: float,
    ylen: float,
    titre_graph: str = "Titre du graphique",
    nom_fich: str = 'graph.jpg',
    padding: float = 0.1,
    barCol: str="#d33"
):
    """
    Génère et sauvegarde un graphique de barres groupées et empilées verticalement.

    Chaque valeur unique de `y_col` crée un "étage" vertical. À chaque étage,
    les barres représentent les valeurs de `val_col` pour chaque `x_col`.

    Args:
        df (pd.DataFrame): DataFrame contenant les données.
        x_col (str): Nom de la colonne pour l'axe des X (catégories).
        y_col (str): Nom de la colonne pour grouper les barres verticalement.
        val_col (str): Nom de la colonne pour la hauteur des barres (valeurs numériques).
        xlen (float): Largeur souhaitée du graphique en cm.
        ylen (float): Hauteur souhaitée du graphique en cm.
        titre_graph (str, optional): Titre du graphique.
        nom_fich (str, optional): Nom du fichier de sortie.
        padding (float, optional): Espace relatif entre les groupes (ex: 0.1 pour 10%).
        barCol: str,optional) ="#d33" Couleur des barres
    """
    # --- 1. Validation et préparation des données ---
    required_cols = [x_col, y_col, val_col]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Les colonnes {required_cols} doivent être dans le DataFrame.")

    # Copie pour éviter de modifier le DataFrame original
    df_plot = df[required_cols].copy()
    df_plot.columns = ['x_var', 'y_var', 'val'] # Noms génériques pour la suite

    x_categories = df_plot['x_var'].unique()
    y_categories = df_plot['y_var'].unique()
    
    # --- 2. Calcul des hauteurs et normalisation ---
    # Hauteur max pour chaque groupe (étage)
    max_per_group = df_plot.groupby('y_var',sort=False)['val'].max()
    
    # Ajout d'un espacement (padding) entre les groupes
    # L'espacement est proportionnel à la hauteur totale des données
    total_data_height = max_per_group.sum()
    padding_value = total_data_height * padding / (len(y_categories) - 1) if len(y_categories) > 1 else 0
    
    group_heights = (max_per_group + padding_value).to_frame(name='padded_height')
    group_heights.loc[group_heights.index[-1], 'padded_height'] -= padding_value # Pas de padding après le dernier
    
    # Normalisation pour que la hauteur totale corresponde à `ylen`
    total_padded_height = group_heights['padded_height'].sum()
    norm_factor = ylen / total_padded_height

    df_plot['val_norm'] = df_plot['val'] * norm_factor
    group_heights['padded_height_norm'] = group_heights['padded_height'] * norm_factor
    group_heights['data_height_norm'] = max_per_group * norm_factor

    # Calculer la position y de départ pour chaque groupe
    group_heights['y_pos'] = group_heights['padded_height_norm'].cumsum().shift(fill_value=0)

    # --- 3. Création du graphique ---
    fig, ax = plt.subplots(figsize=(xlen / 2.54, ylen / 2.54)) # Conversion cm vers inches

    # Bandes de fond colorées pour la lisibilité
    band_width = 6
    for i in range(int(np.ceil(len(x_categories) / band_width))):
        rect = Rectangle((i * band_width, 0), band_width/2, ylen, facecolor='#f0f0f0', zorder=0)
        ax.add_patch(rect)

    # --- 4. Tracer les barres et les lignes ---
    for group_name, group_info in group_heights.iterrows():
        y_pos_start = group_info['y_pos']
        data_top = y_pos_start + group_info['data_height_norm']
        
        # Ligne de séparation au-dessus de chaque groupe
        ax.axhline(y=group_info['padded_height_norm'] + y_pos_start, color='gray', linewidth=0.5, linestyle='--')
        
        # Données spécifiques à ce groupe
        group_data = df_plot[df_plot['y_var'] == group_name].copy()
        
        # Créer un mapping de la catégorie x à sa position numérique
        x_pos_map = {category: i for i, category in enumerate(x_categories)}
        group_data['x_pos'] = group_data['x_var'].map(x_pos_map)

        # Tracer les barres
        ax.bar(group_data['x_pos'], group_data['val_norm'], bottom=y_pos_start, 
               width=0.8, color=barCol, alpha=0.8, zorder=2)

    # --- 5. Configuration finale des axes et de la mise en page ---
    ax.set_xlim(-0.5, len(x_categories) - 0.5)
    ax.set_ylim(0, ylen)
    
    # Étiquettes de l'axe X
    ax.set_xticks(range(len(x_categories)))
    ax.set_xticklabels(x_categories, rotation=45, ha='right', fontsize=8)

    # Étiquettes de l'axe Y pour chaque groupe
    ax.set_yticks(group_heights['y_pos'] + group_heights['data_height_norm'] / 2)
    ax.set_yticklabels(group_heights.index, rotation=0, ha='right', fontsize=9)
    ax.tick_params(axis='y', length=0) # Masquer les petites barres de l'axe Y

    ax.set_title(titre_graph, fontsize=14, pad=10)
    ax.grid(False)
    
    # Supprimer les bordures du graphique pour un look plus propre
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    plt.savefig(nom_fich, dpi=300, bbox_inches='tight')
    plt.show()

# --- Exemple d'utilisation ---
if __name__ == '__main__':
    # Création d'un jeu de données de test
    data = {
        'Mois': ['Jan', 'Fev', 'Mar'] * 3,
        'Produit': ['A'] * 3 + ['B'] * 3 + ['C'] * 3,
        'Ventes': [100, 120, 150, 80, 90, 85, 200, 210, 240]
    }
    df_exemple = pd.DataFrame(data)

    # Appel de la fonction

    plot_grouped_bars(
        df=cmdMois.join(catPrixCode['cat'],on='catCode')[['moisC' ,'cat','val']],
        x_col='moisC',
        y_col='cat',
        val_col='val',
        xlen=17, # 15cm de large
        ylen=20, # 10cm de haut
        titre_graph="Ventes ",
        nom_fich='output.png',
        padding=0.1 # 20% d'espace entre les groupes
    )



