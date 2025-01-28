import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
from collections import defaultdict
import string

class ColumnaBase:
    def __init__(self, parent_frame, titulo, fuente):
        self.datos = []
        self.frame = ttk.LabelFrame(parent_frame, text=titulo, style='TitleFrame.TLabelframe')
        self.frame.pack(side=tk.LEFT, padx=5, expand=True)
        
        style = ttk.Style()
        style.configure("Custom.Treeview", font=('Helvetica', 16), rowheight=25)
        style.configure("Custom.Treeview.Heading", font=('Helvetica', 16, 'bold'))
        
        # Modificar la altura del frame para mostrar más elementos
        self.frame.configure(height=400)  # Aumentar altura del frame
        
        self.tree = ttk.Treeview(self.frame, columns=(titulo,), show='', style="Custom.Treeview")
        self.tree.column(titulo, width=150, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind('<Button-1>', lambda e: 'break')
            
    def limpiar(self):
        self.datos.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)    
            
    def actualizar(self, nuevos_datos):
        self.limpiar()
        self.datos = nuevos_datos
        # Ajustar la altura del Treeview para mostrar todos los elementos
        self.tree.configure(height=max(len(nuevos_datos), 10))  # Mínimo 10 filas visibles
        max_width = max((len(str(dato)) for dato in nuevos_datos), default=5) * 15
        self.tree.column(self.tree["columns"][0], width=max(max_width, 150))  # Mínimo 150px de ancho
        for dato in self.datos:
            self.tree.insert('', 'end', values=(dato,))


class ColumnaQ(ColumnaBase):
    def __init__(self, parent_frame, fuente):
        super().__init__(parent_frame, "Q", fuente)

class ColumnaZ(ColumnaBase):
    def __init__(self, parent_frame, fuente):
        super().__init__(parent_frame, "Z", fuente)

class ColumnaA(ColumnaBase):
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
        estado_sumidero = frozenset()

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

        if estado_sumidero in estados_afd:
            for x in self.alfabeto:
                if x != 'e':
                    self.afd[(estado_sumidero, x)] = estado_sumidero

        return self.afd

    def obtener_estados_finales_afd(self):
        estados_finales_afd = []
        for estado_afd in set(estado for estado, _ in self.afd.keys()):
            if any(estado in self.estados_finales for estado in estado_afd):
                estados_finales_afd.append(estado_afd)
        return estados_finales_afd

    
class MatrizDividida:
    def __init__(self, parent_frame_afn, parent_frame_afd, fuente):
        self.datos = {}
        self.estados_finales = set()
        self.estados_afd_finales = set()
        
        self.frame_afn = ttk.Frame(parent_frame_afn)
        self.frame_afn.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.frame_afd = ttk.Frame(parent_frame_afd)
        self.frame_afd.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        style = ttk.Style()
        style.configure("MatrixTreeview.Treeview", font=('Helvetica', 12), rowheight=25)  # Estilo específico para matrices
        
        self.tree_afn = ttk.Treeview(self.frame_afn, show='headings', style="MatrixTreeview.Treeview")
        self.tree_afn.pack(fill="both", expand=True)
        
        self.tree_afd = ttk.Treeview(self.frame_afd, show='headings', style="MatrixTreeview.Treeview")
        self.tree_afd.pack(fill="both", expand=True)
        
        self.mapeo_estados = {}
        self.mapeo_estados_inverso = {}

    def guardar_estado_final(self, estado_final_afd):
        self.estados_afd_finales.add(estado_final_afd)

    
    def obtener_estados_finales_afd(self):
        return self.estados_afd_finales


    def _create_treeview(self, parent):
        tree = ttk.Treeview(parent, show='headings', style="Custom.Treeview")
        tree.pack(fill="both", expand=True)
        return tree
  
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Configurar altura fija del Treeview
        tree.configure(height=8)
        
        return tree
        
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
        self.datos.clear()
        for tree in [self.tree_afn, self.tree_afd]:
            for item in tree.get_children():
                tree.delete(item)

            
    def actualizar(self, nuevos_datos, estados_finales):
        self.limpiar()
        self.datos = nuevos_datos
        self.estados_finales = set(estados_finales)
        
        self._actualizar_afn()
        estados_afd, simbolos_afd, estados_finales_afd = self._actualizar_afd()
        
        if hasattr(self, 'parent'):
            self.parent.columna_q_afd.actualizar(estados_afd)
            self.parent.columna_z_afd.actualizar(simbolos_afd)
            self.parent.columna_a_afd.actualizar(estados_finales_afd)


    def _actualizar_afn(self):
        estados = sorted(set(estado for estado, _ in self.datos.keys()))
        simbolos = sorted(set(simbolo for _, simbolo in self.datos.keys()))
        
        self.tree_afn["columns"] = ["Estado"] + simbolos
        
        estado_width = max((len(str(estado)) for estado in estados), default=5) * 12
        self.tree_afn.column("Estado", width=estado_width, anchor="center")
        self.tree_afn.heading("Estado", text="Estado")
        
        for simbolo in simbolos:
            max_width = max((len(str(self.datos.get((estado, simbolo), ""))) 
                           for estado in estados), default=5) * 12
            self.tree_afn.column(simbolo, width=max_width, anchor="center")
            self.tree_afn.heading(simbolo, text=simbolo)
        
        self.tree_afn.configure(height=len(estados))
        
        for estado in estados:
            valores = [estado]
            for simbolo in simbolos:
                destinos = self.datos.get((estado, simbolo), "")
                valores.append(destinos)
            self.tree_afn.insert("", "end", values=valores)



    def _mapear_estados(self, estados_afd):
        mapeo = {}
        letras = list(string.ascii_uppercase)
        numeros = list(range(1, len(estados_afd) + 1))
        
        estados_tipo_letra = True
        for estado in estados_afd:
            estado_str = ','.join(sorted(estado)) if estado else '0'
            if any(c.isdigit() for c in estado_str) or estado_str == '0':
                estados_tipo_letra = False
                break
            if any(not c.isalpha() for c in estado_str if c.strip()):
                estados_tipo_letra = False
                break
        
        estados_ordenados = sorted(estados_afd, key=lambda x: ','.join(sorted(x)) if x else '0')
        
        for i, estado in enumerate(estados_ordenados):
            if estados_tipo_letra:
                mapeo[estado] = str(numeros[i])
            else:
                mapeo[estado] = letras[i] if i < len(letras) else f'Z{i - len(letras) + 1}'
        
        return mapeo
        
    def _actualizar_afd(self):
        # Obtener estados, alfabeto y transiciones del AFN
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
            # Convertir destinos de string a conjunto
            transiciones[(simbolo, estado)] = set(destinos.split(', ') if destinos else [])

        # Convertir AFN a AFD
        afn_to_afd = AFNtoAFD(estados, alfabeto, transiciones, estado_inicial, self.estados_finales)
        afd = afn_to_afd.convertir()
        estados_finales_afd = afn_to_afd.obtener_estados_finales_afd()

        # Obtener todos los estados del AFD
        estados_afd = set()
        for (origen, _), destino in afd.items():
            estados_afd.add(origen)
            estados_afd.add(destino)

        estado_inicial_afd = afn_to_afd.cerradura_e({estado_inicial})
        estados_afd.add(estado_inicial_afd)
        estados_afd = sorted(estados_afd, key=lambda x: ','.join(sorted(x)) if x else '0')
        simbolos = sorted(alfabeto - {'e'})

        # Mapear estados
        self.mapeo_estados = self._mapear_estados(estados_afd)
        self.mapeo_estados_inverso = {v: k for k, v in self.mapeo_estados.items()}

        # Configurar columnas del AFD
        columnas = ["Composicion", "Estado"] + simbolos
        self.tree_afd["columns"] = columnas

        # Configurar anchos de columna
        comp_width = max((len('{' + ', '.join(sorted(estado)) + '}' if estado else '∅') 
                         for estado in estados_afd), default=10) * 12
        self.tree_afd.column("Composicion", width=comp_width, anchor="center")
        self.tree_afd.heading("Composicion", text="Composicion")

        estado_width = max((len(str(self.mapeo_estados[estado])) 
                          for estado in estados_afd), default=5) * 12
        self.tree_afd.column("Estado", width=estado_width, anchor="center")
        self.tree_afd.heading("Estado", text="Estado")

        for simbolo in simbolos:
            self.tree_afd.column(simbolo, width=100, anchor="center")
            self.tree_afd.heading(simbolo, text=simbolo)

        # Insertar datos en el AFD
        estados_mostrados = set()
        for estado in estados_afd:
            if estado not in estados_mostrados:
                composicion = '{' + ', '.join(sorted(estado)) + '}' if estado else '∅'
                valores = [composicion, self.mapeo_estados[estado]]
                
                for simbolo in simbolos:
                    destino = afd.get((estado, simbolo), None)
                    valores.append(self.mapeo_estados[destino] if destino is not None else '')
                
                self.tree_afd.insert("", "end", values=valores)
                estados_mostrados.add(estado)

        # Ajustar altura del AFD
        self.tree_afd.configure(height=len(estados_mostrados))

        # Preparar datos para las columnas del AFD
        estados_afd_mapped = [self.mapeo_estados[estado] for estado in estados_afd]
        estados_finales_afd_mapped = []
        for estado in estados_finales_afd:
            if estado in estados_mostrados:
                estado_mapeado = self.mapeo_estados[estado]
                estados_finales_afd_mapped.append(estado_mapeado)
                self.guardar_estado_final(estado_mapeado)

        return estados_afd_mapped, simbolos, sorted(estados_finales_afd_mapped)

    
class AutomataGUI:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Laboratorio Automata                         Anthony Fabian Ramirez Orellana carne: 9490-22-958")
        self.root.configure(bg="#b5b5b5")
        
        self.fuente_global = ('Helvetica', 16)
        
        # Nuevo: Almacenar datos del autómata
        self.datos_automata = {
            'estados_q': [],
            'simbolos_z': [],
            'estados_finales_a': [],
            'transiciones_w': {},
            'estados_finales_afd': set()
        }
        
        self._crear_componentes()
        
    def _crear_componentes(self):
        """Crea todos los componentes de la interfaz"""
        # Cuadro de arrastre
        self.cuadro_arrastre = tk.Label(self.root, text="Arrastre aquí:", relief="solid",
                                       font=self.fuente_global, width=20, height=2, bg="#b5b5b5")
        self.cuadro_arrastre.pack(pady=5)
        
        # Cuadro de texto
        self.cuadro_texto = tk.Text(self.root, height=6, width=80, font=self.fuente_global)
        self.cuadro_texto.pack(pady=5)
        
        # Frame principal que contendrá los dos lados
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Frame izquierdo para AFN que se expande
        self.frame_izquierdo = ttk.LabelFrame(self.frame_principal, text="AFN", style='Title.TLabelframe')
        self.frame_izquierdo.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Frame derecho para AFD que se expande
        self.frame_derecho = ttk.LabelFrame(self.frame_principal, text="AFD", style='Title.TLabelframe')
        self.frame_derecho.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Configurar estilos
        style = ttk.Style()
        style.configure("Custom.Treeview", font=('Helvetica', 16), rowheight=10)
        style.configure("Custom.Treeview.Heading", font=('Helvetica', 16, 'bold'))
        style.configure('Title.TLabelframe', font=('Helvetica', 16, 'bold'))
        style.configure('Title.TLabelframe.Label', font=('Helvetica', 16, 'bold'))
        style.configure('TitleFrame.TLabelframe', font=('Helvetica', 16, 'bold'))
        style.configure('TitleFrame.TLabelframe.Label', font=('Helvetica', 16, 'bold'))
        
        # Frames para columnas con altura aumentada
        self.frame_columnas_afn = ttk.Frame(self.frame_izquierdo, height=200)  # Aumentar altura
        self.frame_columnas_afn.pack(fill=tk.X, padx=5, pady=5)
        self.frame_columnas_afn.pack_propagate(False)
        
        self.frame_columnas_afd = ttk.Frame(self.frame_derecho, height=200)  # Aumentar altura
        self.frame_columnas_afd.pack(fill=tk.X, padx=5, pady=5)
        self.frame_columnas_afd.pack_propagate(False)
        
        # Crear columnas AFN y AFD
        self.columna_q_afn = ColumnaQ(self.frame_columnas_afn, self.fuente_global)
        self.columna_z_afn = ColumnaZ(self.frame_columnas_afn, self.fuente_global)
        self.columna_a_afn = ColumnaA(self.frame_columnas_afn, self.fuente_global)
        
        self.columna_q_afd = ColumnaQ(self.frame_columnas_afd, self.fuente_global)
        self.columna_z_afd = ColumnaZ(self.frame_columnas_afd, self.fuente_global)
        self.columna_a_afd = ColumnaA(self.frame_columnas_afd, self.fuente_global)
        
        # Crear matriz
        self.matriz = MatrizDividida(self.frame_izquierdo, self.frame_derecho, self.fuente_global)
        self.matriz.parent = self
        
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
        self.datos_automata = {
            'estados_q': [],
            'simbolos_z': [],
            'estados_finales_a': [],
            'transiciones_w': {},
            'estados_finales_afd': set()
        }
        
        for line in lines:
            if line.startswith("Q="):
                self.datos_automata['estados_q'] = [val.lstrip("{").strip() for val in line.strip()[2:-1].split(",")]
            elif line.startswith("Z="):
                self.datos_automata['simbolos_z'] = [val.lstrip("{").rstrip("}").strip() for val in line.strip()[2:-1].split(",")]
            elif line.startswith("A="):
                self.datos_automata['estados_finales_a'] = [val.lstrip("{").strip() for val in line.strip()[2:-1].split(",")]
            elif line.startswith("w="):
                w_values = line.strip()[2:-1].split(";")
                for item in w_values:
                    estado_inicio, elemento, estado_destino = item.strip()[1:-1].split(",")
                    estado_inicio = estado_inicio.lstrip("{").lstrip("(").strip()
                    elemento = elemento.strip()
                    estado_destino = estado_destino.rstrip("}").rstrip(")").strip()
                    
                    key = (estado_inicio, elemento)
                    if key not in self.datos_automata['transiciones_w']:
                        self.datos_automata['transiciones_w'][key] = set()
                    self.datos_automata['transiciones_w'][key].add(estado_destino)

        # Convertir los conjuntos a cadenas en transiciones_w
        self.datos_automata['transiciones_w'] = {
            k: ', '.join(v) for k, v in self.datos_automata['transiciones_w'].items()
        }

        # Actualizar componentes
        self._actualizar_interfaz()


    def _actualizar_interfaz(self):
        """Actualiza todos los componentes de la interfaz con los datos actuales"""
        # Actualizar columnas AFN
        self.columna_q_afn.actualizar(self.datos_automata['estados_q'])
        self.columna_z_afn.actualizar(self.datos_automata['simbolos_z'])
        self.columna_a_afn.actualizar(self.datos_automata['estados_finales_a'])
        
        # Actualizar matriz y obtener estados finales AFD
        self.matriz.actualizar(self.datos_automata['transiciones_w'], self.datos_automata['estados_finales_a'])
        
        # Obtener estados finales del AFD después de la conversión
        self.datos_automata['estados_finales_afd'] = self.matriz.obtener_estados_finales_afd()
        
        # Actualizar columna A del AFD con los estados finales convertidos
        self.columna_a_afd.actualizar(sorted(self.datos_automata['estados_finales_a']))

    def ejecutar(self):
        self.root.mainloop()

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    app = AutomataGUI()
    app.ejecutar()
