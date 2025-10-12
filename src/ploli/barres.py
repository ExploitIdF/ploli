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
  fig, ax = plt.subplots(figsize=(xlen/2.54, ylen/2.54))  # conversion cm en inches

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
