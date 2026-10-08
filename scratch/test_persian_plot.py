import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

def test1(text): return text
def test2(text): return arabic_reshaper.reshape(text)
def test3(text): return get_display(text)
def test4(text): return get_display(arabic_reshaper.reshape(text))

text = "سلام دنیا"

fig, axs = plt.subplots(4, 1, figsize=(4, 4))
axs[0].text(0.5, 0.5, test1(text), fontname="Tahoma", size=20, ha='center')
axs[0].set_title("Raw")
axs[1].text(0.5, 0.5, test2(text), fontname="Tahoma", size=20, ha='center')
axs[1].set_title("Reshaper only")
axs[2].text(0.5, 0.5, test3(text), fontname="Tahoma", size=20, ha='center')
axs[2].set_title("Bidi only")
axs[3].text(0.5, 0.5, test4(text), fontname="Tahoma", size=20, ha='center')
axs[3].set_title("Both")

for ax in axs:
    ax.axis('off')

plt.tight_layout()
plt.savefig('d:/project/hamta/scratch/test_fa.png')
print("Saved test_fa.png")
