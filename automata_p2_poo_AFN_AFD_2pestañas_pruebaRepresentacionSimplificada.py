import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
from collections import defaultdict
import string

class ColumnaBase:
    """Clase base para las columnas Q, Z y A"""
    def __init__(self, parent_frame, titulo, fuente):
        self.datos = []
        self.frame = ttk.LabelFrame(parent_frame, text=titulo, style='TitleFrame.TLabelframe')
        self.frame.pack(side=tk.LEFT, padx=5, expand=True)
        
        # Crear un estilo personalizado
        style = ttk.Style()
        style.configure("Custom.Treeview", font=('Helvetica', 24), rowheight=40)
        style.configure("Custom.Treeview.Heading", font=('Helvetica', 24, 'bold'))
        style.configure('TitleFrame.TLabelframe', font=('Helvetica', 24, 'bold'))
        style.configure('TitleFrame.TLabelframe.Label', font=('Helvetica', 24, 'bold'))
        
        self.tree = ttk.Treeview(self.frame, columns=(titulo,), show='tree', height=5, style="Custom.Treeview")
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column(titulo, width=200, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def limpiar(self):
        """Limpia todos los datos de la columna"""
        self.datos.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def actualizar(self, nuevos_datos):
        """Actualiza los datos y la visualización de la columna"""
        self.limpiar()
        self.datos = nuevos_datos
        for dato in self.datos:
            self.tree.insert('', 'end', values=(dato,))

class ColumnaQ(ColumnaBase):
    """Clase específica para la columna Q"""
    def __init__(self, parent_frame, fuente):
        super().__init__(parent_frame, "Q", fuente)

class ColumnaZ(ColumnaBase):
    """Clase específica para la columna Z"""
    def __init__(self, parent_frame, fuente):
        super().__init__(parent_frame, "Z", fuente)

class ColumnaA(ColumnaBase):
    """Clase específica para la columna A"""
    def __init__(self, parent_frame, fuente):
        super().__init__(parent_frame, "A", fuente)

class AFNtoAFD:
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales
        self.afd = {}

    def cerradura_e(self, estados):
        pila = list(estados)
        cerradura = set(estados)
        while pila:
            estado = pila.pop()
            if ('e', estado) in self.transiciones:
                for destino in self.transiciones[('e', estado)]:
                    if destino not in cerradura:
                        cerradura.add(destino)
                        pila.append(destino)
        return frozenset(cerradura)

    def mueve(self, estados, simbolo):
        resultado = set()
        for estado in estados:
            if (simbolo, estado) in self.transiciones:
                resultado.update(self.transiciones[(simbolo, estado)])
        return resultado

    def convertir(self):
        T0 = self.cerradura_e({self.estado_inicial})
        estados_sin_marcar = [T0]
        estados_afd = [T0]
        estado_sumidero = frozenset()  # Estado sumidero

        while estados_sin_marcar:
            T = estados_sin_marcar.pop(0)
            for x in self.alfabeto:
                if x != 'e':
                    U = self.cerradura_e(self.mueve(T, x))
                    if not U:
                        U = estado_sumidero
                    if U not in estados_afd:
                        estados_afd.append(U)
                        if U != estado_sumidero:
                            estados_sin_marcar.append(U)
                    self.afd[(T, x)] = U

        # Agregar transiciones para el estado sumidero
        if estado_sumidero in estados_afd:
            for x in self.alfabeto:
                if x != 'e':
                    self.afd[(estado_sumidero, x)] = estado_sumidero

        return self.afd

    def obtener_estados_finales_afd(self):
        estados_finales_afd = []
        for estado in self.afd.keys():
            if isinstance(estado, frozenset) and any(e in self.estados_finales for e in estado):
                estados_finales_afd.append(estado)
        return estados_finales_afd

class Matriz:
    """Clase para manejar la matriz W"""
    def __init__(self, parent_frame, fuente):
        self.datos = {}
        self.estados_finales = set()
        self.frame = ttk.LabelFrame(parent_frame, text="Matriz W", style='TitleFrame.TLabelframe')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear un estilo personalizado
        style = ttk.Style()
        style.configure("Custom.Treeview", font=('Helvetica', 24), rowheight=40)
        style.configure("Custom.Treeview.Heading", font=('Helvetica', 24, 'bold'))
        style.configure('TitleFrame.TLabelframe', font=('Helvetica', 24, 'bold'))
        style.configure('TitleFrame.TLabelframe.Label', font=('Helvetica', 24, 'bold'))
        
        # Crear Notebook para las pestañas
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear frames para AFN y AFD
        self.frame_afn = ttk.Frame(self.notebook)
        self.frame_afd = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_afn, text="AFN")
        self.notebook.add(self.frame_afd, text="AFD")
        
        # Crear Treeviews para AFN y AFD
        self.tree_afn = self._create_treeview(self.frame_afn)
        self.tree_afd = self._create_treeview(self.frame_afd)
        
    def _create_treeview(self, parent):
        tree = ttk.Treeview(parent, show='headings', style="Custom.Treeview")
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        
        return tree
        
    def limpiar(self):
        """Limpia todos los datos de la matriz"""
        self.datos.clear()
        for tree in [self.tree_afn, self.tree_afd]:
            for item in tree.get_children():
                tree.delete(item)
            
    def actualizar(self, nuevos_datos, estados_finales):
        """Actualiza los datos y la visualización de la matriz"""
        self.limpiar()
        self.datos = nuevos_datos
        self.estados_finales = set(estados_finales)
        
        # Actualizar AFN
        self._actualizar_afn()
        
        # Convertir AFN a AFD y actualizar
        self._actualizar_afd()

        
    def _actualizar_afn(self):
        estados = sorted(set(estado for estado, _ in self.datos.keys()))
        simbolos = sorted(set(simbolo for _, simbolo in self.datos.keys()))
        
        # Configurar columnas para AFN
        self.tree_afn["columns"] = ["Estado"] + simbolos
        self.tree_afn.column("Estado", width=200, anchor="center")
        self.tree_afn.heading("Estado", text="Estado")
        for simbolo in simbolos:
            self.tree_afn.column(simbolo, width=100, anchor="center")
            self.tree_afn.heading(simbolo, text=simbolo)
        
        # Insertar datos AFN
        for estado in estados:
            valores = [estado]
            for simbolo in simbolos:
                destinos = self.datos.get((estado, simbolo), "")
                valores.append(destinos)
            self.tree_afn.insert("", "end", values=valores)

    def _mapear_estados(self, estados_afd):
        """Mapea los estados del AFD a letras (para números/vacío) o números (para letras)"""
        mapeo = {}
        letras = list(string.ascii_uppercase)
        numeros = list(range(1, len(estados_afd) + 1))
        
        # Determinar el tipo de estados que tenemos
        estados_tipo_letra = True
        for estado in estados_afd:
            # Convertir el estado a una cadena para manejar el conjunto vacío
            estado_str = ','.join(sorted(estado)) if estado else '0'
            # Si encontramos algún número o el estado vacío, usaremos letras
            if any(c.isdigit() for c in estado_str) or estado_str == '0':
                estados_tipo_letra = False
                break
            # Si encontramos algo que no sea letra, usaremos números
            if any(not c.isalpha() for c in estado_str if c.strip()):
                estados_tipo_letra = False
                break
        
        # Ordenar estados para mantener consistencia
        estados_ordenados = sorted(estados_afd, key=lambda x: ','.join(sorted(x)) if x else '0')
        
        # Asignar mapeo según el tipo de estados
        for i, estado in enumerate(estados_ordenados):
            if estados_tipo_letra:
                # Si son todos letras, usar números
                mapeo[estado] = str(numeros[i])
            else:
                # Si hay números o estado vacío, usar letras
                mapeo[estado] = letras[i] if i < len(letras) else f'Z{i - len(letras) + 1}'
        
        return mapeo
        
    def _actualizar_afd(self):
        # Convertir AFN a AFD
        estados = set()
        alfabeto = set()
        transiciones = {}
        estado_inicial = None

        for (estado, simbolo), destinos in self.datos.items():
            estados.add(estado)
            if simbolo != 'e':
                alfabeto.add(simbolo)
            if estado_inicial is None:
                estado_inicial = estado
            # Convertir la cadena de destinos en un conjunto
            transiciones[(simbolo, estado)] = set(destinos.split(', '))

        afn_to_afd = AFNtoAFD(estados, alfabeto, transiciones, estado_inicial, self.estados_finales)
        afd = afn_to_afd.convertir()
        estados_finales_afd = afn_to_afd.obtener_estados_finales_afd()

        # Obtener todos los estados del AFD, incluyendo los destinos
        estados_afd = set()
        for (origen, _), destino in afd.items():
            estados_afd.add(origen)
            estados_afd.add(destino)

        # Asegurar que el estado inicial esté incluido
        estado_inicial_afd = afn_to_afd.cerradura_e({estado_inicial})
        estados_afd.add(estado_inicial_afd)

        # Ordenar los estados para una visualización consistente
        estados_afd = sorted(estados_afd, key=lambda x: ','.join(sorted(x)) if x else '0')
        simbolos = sorted(alfabeto - {'e'})

        # Mapear estados a letras o números
        mapeo_estados = self._mapear_estados(estados_afd)

        # Configurar columnas para AFD
        columnas = ["Composicion", "Estado"] + simbolos
        self.tree_afd["columns"] = columnas
        
        # Configurar columna Composicion
        self.tree_afd.column("Composicion", width=250, anchor="center")
        self.tree_afd.heading("Composicion", text="Composicion")
        
        # Configurar columna Estado
        self.tree_afd.column("Estado", width=100, anchor="center")
        self.tree_afd.heading("Estado", text="Estado")
        
        # Configurar columnas de símbolos
        for simbolo in simbolos:
            self.tree_afd.column(simbolo, width=100, anchor="center")
            self.tree_afd.heading(simbolo, text=simbolo)

        # Insertar datos AFD
        estados_mostrados = set()
        for estado in estados_afd:
            if estado not in estados_mostrados:  # Evitar duplicados
                # Preparar la representación de la composición
                composicion = '{' + ', '.join(sorted(estado)) + '}' if estado else '∅'
                
                # Solo mostrar estados que tienen transiciones o son el estado inicial
                tiene_transiciones = False
                valores = [composicion, mapeo_estados[estado]]
                
                for simbolo in simbolos:
                    destino = afd.get((estado, simbolo), None)
                    if destino is not None:
                        tiene_transiciones = True
                        valores.append(mapeo_estados[destino])
                    else:
                        valores.append('')
                
                # Mostrar el estado si tiene transiciones o es el estado inicial
                if tiene_transiciones or estado == estado_inicial_afd:
                    self.tree_afd.insert("", "end", values=valores)
                    estados_mostrados.add(estado)

        # Print debug information
        print("AFD states mapping:", mapeo_estados)
        print("AFD transitions:", {(mapeo_estados[k[0]], k[1]): mapeo_estados[v] for k, v in afd.items()})
        print("AFD final states:", [mapeo_estados[estado] for estado in estados_finales_afd])

class AutomataGUI:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Laboratorio Automata                         Anthony Fabian Ramirez Orellana carne: 9490-22-958")
        self.root.geometry("1200x800")
        self.root.configure(bg="#b5b5b5")
        
        self.fuente_global = ('Helvetica', 24)
        
        self._crear_componentes()
        
    def _crear_componentes(self):
        """Crea todos los componentes de la interfaz"""
        # Cuadro de arrastre (reducido)
        self.cuadro_arrastre = tk.Label(self.root, text="Arrastre aquí:", relief="solid",
                                       font=self.fuente_global, width=20, height=1, bg="#b5b5b5")
        self.cuadro_arrastre.pack(pady=5)
        
        # Cuadro de texto (reducido)
        self.cuadro_texto = tk.Text(self.root, height=4, width=40, font=self.fuente_global)
        self.cuadro_texto.pack(pady=5)
        
        # Frame principal
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame para columnas
        self.frame_columnas = ttk.Frame(self.frame_principal)
        self.frame_columnas.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Crear objetos de columnas
        self.columna_q = ColumnaQ(self.frame_columnas, self.fuente_global)
        self.columna_z = ColumnaZ(self.frame_columnas, self.fuente_global)
        self.columna_a = ColumnaA(self.frame_columnas, self.fuente_global)
        
        # Crear objeto matriz
        self.matriz = Matriz(self.frame_principal, self.fuente_global)
        
        # Configurar arrastrar y soltar
        self.cuadro_arrastre.drop_target_register(DND_FILES)
        self.cuadro_arrastre.dnd_bind('<<Drop>>', self._procesar_archivo)
        
    def _procesar_archivo(self, event):
        """Procesa el archivo arrastrado"""
        archivo = event.data.strip("{}")
        
        if not os.path.isfile(archivo):
            print("Error: no se encontró el archivo")
            return
            
        with open(archivo, 'r') as f:
            lines = f.readlines()
            
        # Limpiar el cuadro de texto
        self.cuadro_texto.delete("1.0", tk.END)
        for line in lines:
            self.cuadro_texto.insert(tk.END, line)
            
        # Procesar cada línea
        datos_q = []
        datos_z = []
        datos_a = []
        datos_w = {}
        
        for line in lines:
            if line.startswith("Q="):
                datos_q = [val.lstrip("{").strip() for val in line.strip()[2:-1].split(",")]
            elif line.startswith("Z="):
                datos_z = [val.lstrip("{").rstrip("}").strip() for val in line.strip()[2:-1].split(",")]
            elif line.startswith("A="):
                datos_a = [val.lstrip("{").strip() for val in line.strip()[2:-1].split(",")]
            elif line.startswith("w="):
                w_values = line.strip()[2:-1].split(";")
                for item in w_values:
                    estado_inicio, elemento, estado_destino = item.strip()[1:-1].split(",")
                    estado_inicio = estado_inicio.lstrip("{").lstrip("(").strip()
                    elemento = elemento.strip()
                    estado_destino = estado_destino.rstrip("}").rstrip(")").strip()
                    
                    # Agregar a datos_w
                    key = (estado_inicio, elemento)
                    if key not in datos_w:
                        datos_w[key] = set()
                    datos_w[key].add(estado_destino)
        
        # Convertir los conjuntos a cadenas en datos_w
        for key in datos_w:
            datos_w[key] = ', '.join(datos_w[key])

        # Print debug information
        print("Parsed Q:", datos_q)
        print("Parsed Z:", datos_z)
        print("Parsed A:", datos_a)
        print("Parsed W:", datos_w)

        # Actualizar componentes
        self.columna_q.actualizar(datos_q)
        self.columna_z.actualizar(datos_z)
        self.columna_a.actualizar(datos_a)
        self.matriz.actualizar(datos_w, datos_a)  # Pasar datos_a como estados finales
        
    def ejecutar(self):
        self.root.mainloop()

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    app = AutomataGUI()
    app.ejecutar()