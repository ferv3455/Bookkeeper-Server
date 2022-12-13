from matplotlib import pyplot as plt
import io


plt.figure()
plt.plot([1, 2])
plt.title("test")
buf = io.BytesIO()
plt.savefig(buf, format='png')
print(buf.read())
buf.close()