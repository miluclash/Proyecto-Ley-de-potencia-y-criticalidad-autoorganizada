#Logica pura de DJANGO 
import numpy as np

def step(grid,p,f):
    """Simula un paso de la propagación del fuego en el bosque.
    Args:
        grid (np.array): Matriz que representa el estado del bosque (0: vacío, 1: árbol, 2: fuego).
        p (float): Probabilidad de crecimiento de un árbol en un espacio vacío.
        f (float): Probabilidad de que un árbol prenda fuego por un rayo, incluso sin vecinos en llamas.
    Returns:
        np.array: Matriz que representa el estado del bosque después del paso.
    """
    N = grid.shape[0]
    next_grid = grid.copy()
    num = np.random.random((N, N))
    vecino_fuego = (
    np.pad(grid[:-1, :] == 2, ((1,0),(0,0))) |  # arriba
    np.pad(grid[1:, :]  == 2, ((0,1),(0,0))) |  # abajo
    np.pad(grid[:, :-1] == 2, ((0,0),(1,0))) |  # izquierda
    np.pad(grid[:, 1:]  == 2, ((0,0),(0,1)))    # derecha
    )
    
    
    next_grid[(grid ==2)]=0 # el fuego se apaga
    next_grid[(grid==1)&vecino_fuego]=2 # el fuego se propaga a los arboles vecinos
    next_grid[(grid==0)& (num<p)]=1 # los espacios vacios pueden crecer arboles con probabilidad p
    next_grid[(grid==1)& (~vecino_fuego)&(num<f)]=2 # los arboles pueden prenderse fuego por un rayo con probabilidad f aunque no tengan vecinos en llamas
    return next_grid

def create_grid(N):
    """Crea una matriz de N x N con árboles distribuidos aleatoriamente.
    Args:
        N (int): Tamaño de la matriz (N x N).
    Returns:
        np.array: Matriz que representa el estado inicial del bosque (0: vacío, 1: árbol).
    """
    return np.zeros((N, N), dtype=int) #El grid se genera con 0 arboles, el crecimiento de los mismos se simula en el paso siguiente.

def get_stats(grid):
    """Calcula las estadísticas del estado actual del bosque.
    Args:
        grid (np.array): Matriz que representa el estado del bosque (0: vacío, 1: árbol, 2: fuego).
    Returns:
        dict: Diccionario con el conteo de árboles, fuego y espacios vacíos.
    """
    #El enunciado pide densidad (proporción entre 0 y 1), no conteo absoluto. ¿Cómo lo convertirías?
    total = grid.size
    return {
        'empty': np.sum(grid == 0) / total,
        'tree': np.sum(grid == 1) / total,
        'fire': np.sum(grid == 2) / total
    }

