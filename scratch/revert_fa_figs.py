with open('d:/project/hamta/create_paper_fa.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('FIG = os.path.join(BASE, "figures")', 'FIG = os.path.join(BASE, "figures_fa")')
c = c.replace('fig1_framework_architecture.png', 'fig1_architecture_fa.png')
c = c.replace('fig2_graph_topology_communities.png', 'fig2_topology_fa.png')
c = c.replace('fig3_latent_tsne_comparison.png', 'fig3_guild_heatmap_fa.png')
c = c.replace('fig4_radar_persona_profiles.png', 'fig4_radar_fa.png')
c = c.replace('fig5_benchmark_comparison_bar.png', 'fig5_benchmark_fa.png')

with open('d:/project/hamta/create_paper_fa.py', 'w', encoding='utf-8') as f:
    f.write(c)
