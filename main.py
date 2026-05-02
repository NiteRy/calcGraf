import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CalculadoraTotal:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Científica 3D - Pro Version")
        self.root.geometry("1250x850")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Variáveis Simbólicas: Agora com Z e Lambda
        self.x, self.y, self.z, self.lamda = sp.symbols('x y z lamda')

        self.setup_derivadas()
        self.setup_integrais()
        self.setup_equacoes()

    def criar_layout(self, tab):
        container = tk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        esq = tk.Frame(container, width=480, padx=15, pady=15)
        esq.pack(side=tk.LEFT, fill=tk.BOTH)
        dir = tk.Frame(container, bg="white")
        dir.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        return esq, dir

    def plot_3d(self, frame, expressao):
        for w in frame.winfo_children(): w.destroy()
        try:
            # Para o gráfico 3D, se houver Z na expressão, fixamos Z=0 para visualizar a superfície x/y
            expr_plot = expressao.subs(self.z, 0) 
            f_num = sp.lambdify((self.x, self.y), expr_plot, 'numpy')
            x_v = np.linspace(-5, 5, 50); y_v = np.linspace(-5, 5, 50)
            X, Y = np.meshgrid(x_v, y_v)
            Z_vals = f_num(X, Y)
            if isinstance(Z_vals, (int, float)): Z_vals = np.full(X.shape, Z_vals)
            
            fig = plt.figure(figsize=(5, 4))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(X, Y, Z_vals, cmap='viridis', edgecolor='none')
            ax.set_title("Visualização (Z fixado em 0 se existir)")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except: pass

    # --- TAB 1: DERIVADAS (X, Y, Z) ---
    def setup_derivadas(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Derivadas & Lagrange (x,y,z)")
        esq, dir = self.criar_layout(tab)

        tk.Label(esq, text="Função f(x, y, z):", font=('Arial', 10, 'bold')).pack()
        ent_f = tk.Entry(esq, width=45); ent_f.insert(0, "x**2 + y**2 + z**2"); ent_f.pack(pady=5)
        
        tk.Label(esq, text="Restrição g(x,y,z)=0 (Opcional):", fg="blue").pack()
        ent_g = tk.Entry(esq, width=45); ent_g.pack(pady=5)

        res = tk.Text(esq, height=25, width=60, font=("Consolas", 9))
        
        def calcular():
            try:
                f = sp.sympify(ent_f.get())
                res.delete(1.0, tk.END)
                
                # Gradiente com 3 variáveis
                grad = [sp.diff(f, v) for v in (self.x, self.y, self.z)]
                res.insert(tk.END, f"GRADIENTE (∇f):\nfx = {grad[0]}\nfy = {grad[1]}\nfz = {grad[2]}\n\n")
                
                # Lagrange
                g_val = ent_g.get().strip()
                if g_val:
                    g = sp.sympify(g_val)
                    L = f - self.lamda * g
                    sols = sp.solve([sp.diff(L, v) for v in (self.x, self.y, self.z)] + [g], 
                                    (self.x, self.y, self.z, self.lamda), dict=True)
                    res.insert(tk.END, f"PONTOS DE LAGRANGE:\n")
                    for s in sols: res.insert(tk.END, f"{s}\n")
                else:
                    res.insert(tk.END, "[Cálculo de Lagrange ignorado]\n")

                self.plot_3d(dir, f)
            except Exception as e: messagebox.showerror("Erro", str(e))

        tk.Button(esq, text="Analisar f(x,y,z)", command=calcular, bg="#2196F3", fg="white").pack(pady=10)
        res.pack()

    # --- TAB 2: INTEGRAIS (X, Y, Z) ---
    def setup_integrais(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Integrais Duplos/Triplos")
        esq, dir = self.criar_layout(tab)

        tk.Label(esq, text="Função f(x,y,z):").pack()
        ent_f = tk.Entry(esq, width=40); ent_f.insert(0, "x*y*z"); ent_f.pack()
        
        tk.Label(esq, text="Limites X (min, max):").pack(); ent_x = tk.Entry(esq); ent_x.insert(0, "0, 1"); ent_x.pack()
        tk.Label(esq, text="Limites Y (Opcional):").pack(); ent_y = tk.Entry(esq); ent_y.pack()
        tk.Label(esq, text="Limites Z (Opcional):").pack(); ent_z = tk.Entry(esq); ent_z.pack()

        res = tk.Text(esq, height=15, width=60, font=("Consolas", 10))

        def calcular():
            try:
                f = sp.sympify(ent_f.get()); res.delete(1.0, tk.END)
                
                # Lógica de integração em cascata
                result = f
                vars_limits = [ (self.x, ent_x), (self.y, ent_y), (self.z, ent_z) ]
                
                for var, entry in vars_limits:
                    val = entry.get().strip()
                    if val:
                        lims = val.split(',')
                        result = sp.integrate(result, (var, sp.sympify(lims[0]), sp.sympify(lims[1])))
                
                res.insert(tk.END, f"RESULTADO: {result}")
                self.plot_3d(dir, f)
            except Exception as e: messagebox.showerror("Erro", str(e))

        tk.Button(esq, text="Integrar", command=calcular, bg="#4CAF50", fg="white").pack(pady=10)
        res.pack()

    # --- TAB 3: EQUAÇÕES SMART ---
    def setup_equacoes(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Equações (Smart Box)")
        f_main = tk.Frame(tab, padx=40, pady=40)
        f_main.pack(fill=tk.BOTH)

        tk.Label(f_main, text="Insere a Equação ou EDO:", font=('Arial', 12, 'bold')).pack(pady=10)
        tk.Label(f_main, text="(Ex Algébrica: x**2-4  |  Ex EDO: f(x).diff(x)-f(x))", fg="gray").pack()
        
        ent_eq = tk.Entry(f_main, width=70, font=("Arial", 12)); ent_eq.pack(pady=10)
        res = tk.Text(f_main, height=15, width=90, font=("Consolas", 11))

        def resolver_smart():
            res.delete(1.0, tk.END)
            txt = ent_eq.get().strip()
            if not txt: return
            
            try:
                # Tenta como EDO primeiro (se contiver f(x))
                if "f(x)" in txt:
                    func_f = sp.Function('f')(self.x)
                    sol = sp.dsolve(eval(txt), func_f)
                    res.insert(tk.END, f"TIPO: Equação Diferencial (EDO)\nSOLUÇÃO: {sol}")
                else:
                    # Resolve como Algébrica
                    sol = sp.solve(sp.sympify(txt), self.x)
                    res.insert(tk.END, f"TIPO: Equação Algébrica\nSOLUÇÕES: {sol}")
            except Exception as e:
                res.insert(tk.END, f"Erro ao processar: {e}")

        tk.Button(f_main, text="Resolver Agora", command=resolver_smart, bg="#FF9800", fg="white", font=("Arial", 10, 'bold')).pack(pady=10)
        res.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraTotal(root)
    root.mainloop()