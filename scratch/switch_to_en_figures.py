import re

with open('d:/project/hamta/create_paper_fa.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('FIG = os.path.join(BASE, "figures_fa")', 'FIG = os.path.join(BASE, "figures")')
c = c.replace('fig1_architecture_fa.png', 'fig1_framework_architecture.png')
c = c.replace('fig2_topology_fa.png', 'fig2_graph_topology_communities.png')
c = c.replace('fig3_guild_heatmap_fa.png', 'fig3_latent_tsne_comparison.png')
c = c.replace('fig4_radar_fa.png', 'fig4_radar_persona_profiles.png')
c = c.replace('fig5_benchmark_fa.png', 'fig5_benchmark_comparison_bar.png')

with open('d:/project/hamta/create_paper_fa.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Switched to English figures in FA paper")
