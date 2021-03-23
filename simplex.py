import numpy as np

class EndException(Exception):
    pass

def get_ineqs() -> tuple:
    obj_f = input("Podaj funkcję celu: ")
    ineqs = []
    ineqs.append(input("Podaj nierówność: "))
    return (obj_f, ineqs)

def ineqs_to_array():
    base = [] # indeksy zmiennych, które są aktualnie w bazie
    arr = np.array() # tablica simplex
    var_names = []
    # parser
    return base, arr, var_names

def compute_last_row(arr):
    for col in range(1, arr.shape[1]-1): # wszystkie kolumny oprócz pomocniczej
        products = arr[1:-1, 0] * arr[1:-1, col]
        arr[-1, col] =  products.sum() - arr[0,col]

    products = arr[1:-1, 0] * arr[1:-1, -1]
    arr[-1, -1] =  products.sum()


def find_pivot(arr) -> tuple:
    if(arr[-1, 1:-2].min() >= 0):
        raise EndException("Rozwiązanie optymalne")
    else:
        pivot_col = arr[-1, 1:-2].argmin() + 1 # add one for 0. column

        # compute ratios
        min_ratio = np.inf
        min_ratio_row = None

        for row in range(1, arr.shape[0]-1): # rows in inner array
            if arr[row, pivot_col] > 0:
                if (r := (arr[row, -1]/arr[row, pivot_col])) < min_ratio:
                    min_ratio = r
                    min_ratio_row = row

        if min_ratio_row == None:
                raise EndException("Rozwiązanie nieograniczone (wartość funkcji celu może być dowolnie duża)")

        return (min_ratio_row, pivot_col)

def change_base(base, arr, pivot):
    base[pivot[0]-1] = pivot[1]
    arr[pivot[0], 0] = arr[0, pivot[1]]


def recompute_array(arr, pivot):
    pivot_val = arr[pivot]
    for row in range(1, arr.shape[0]-1):
        if row != pivot[0]:
            for col in range(1, arr.shape[1]):
                if col != pivot[1]:
                    arr[row, col] = arr[row, col] - ((arr[pivot[0], col] * arr[row, pivot[1]]) / pivot_val)

    for row in range(1, arr.shape[0]): # powinny wyjść same 0
        if row != pivot[0]:
            arr[row, pivot[1]] = 0
            # arr[row, pivot[1]] = arr[row, pivot[1]] - ((arr[pivot[0], pivot[1]] * arr[row, pivot[1]]) / pivot_val)

    for col in range(1, arr.shape[1]):
        arr[pivot[0], col] /= pivot_val



if __name__ == '__main__':
    np.set_printoptions(nanstr="", suppress=True, linewidth=200, precision=4)
    # get_ineqs()
    # base, arr, var_names = ineqs_to_array()

    names = []

    # PRZYKŁAD 1
    arr = np.array([[np.nan,1,3,0,0,0],[0,-1,1,1,0,1],[0,1,1,0,1,5], [np.nan]*6]) # 0. wiersz - f. celu, ostatni - pomocniczy 0. kolumna - przepisane z funkcji celu wart zmiennych w bazie
    base = [3,4]       # zmienne numerowane od 1

    # PRZYKŁAD Z WYKŁADU
    # arr = np.array([[np.nan,11,10,0,0,0,0, np.nan],[0,2,1,1,0,0,0,40],[0,7,9,0,1,0,0,300], [0,16,8,0,0,1,0,500], [0,15,12,0,0,0,1,700], [np.nan]*8])
    # base = [3,4,5,6]

    # PRZYKŁAD 2
    # arr = np.array([[np.nan, 1,1,0,0,np.nan], [0,1,1,1,0,4], [0,-1,1,0,1,2], [np.nan]*6])
    # base = [3, 4]

    # PRZYKŁAD 3
    # arr = np.array([[np.nan, 3,1,0,0,0,np.nan], [0,-4,3,1,0,0,6], [0,-1,3,0,1,0,15], [0,1,-4,0,0,1,4],[np.nan]*7])
    # base = [3, 4, 5]


    while True:
        try:
            compute_last_row(arr)
            print(names, arr, sep="\n")
            pivot = find_pivot(arr)
            print("Pivot (wiersz, kolumna):\t   ", pivot)
            change_base(base, arr, pivot)
            print("Nowa baza (numery zmiennych od 1): ", base)
            recompute_array(arr, pivot)
            input()
        except EndException as e:
            print(e)
            break

    # wartości wewnętrznej macierzy dla zmiennych bazowych powinny tworzyć macierz jednostkową
    # wartości wiersza wskaźnikowego dla zmiennych bazowych powinny być 0
