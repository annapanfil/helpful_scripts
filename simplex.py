import numpy as np

class GoodEndException(Exception):
    pass

class BadEndException(Exception):
    pass


def get_ineqs() -> tuple:
    print("Wszystkie pola oddzielaj spacjami")
    names = input("Nazwy zmiennych: ")
    obj_f = input("Współczynniki przy zmiennych w funkcji celu: ")
    ineqs = []
    print("\nPodaj nierówności w formacie <współczynniki_oddzielone_spacjami> <znak> <prawa_strona>\nnp. 1 2 3 <= 15\n(^D kończy): ")
    print("UWAGA! Na razie obsługiwane są tylko nierówności '<=' z prawą stroną >= 0")
    try:
        while(1):
            ineqs.append(input("> "))
    except EOFError:
        print("^D\n")
        return (names, obj_f, ineqs)


def ineq_to_std(ineq: str, extra_var_counter=0) -> list:
    ineq = ineq.split(" ")
    if float(ineq[-1]) < 0:
        raise NameError("Ten typ nierówności nie jest jeszcze obsługiwany (RHS = "+ ineq[-1]+")")

    if ineq[-2] in ["<=", "≤", "leq"]:
        ineq_list = [np. nan]+[float(x) for x in ineq[:-2]] + [0 for _ in range(extra_var_counter)] + [1] + [float(ineq[-1])]
        extra_var_counter += 1
        return ineq_list, extra_var_counter
    else:
        raise NameError("Ten typ nierówności nie jest jeszcze obsługiwany ("+ineq[-2]+")")

def even_rows_len(rows: list, length: int):
    for row in rows:
        for i in range(length - len(row)):
            row.insert(-1, 0)


def ineqs_to_array(obj_f: str, ineqs: list):
    obj_f = [np. nan] + [float(x) for x in obj_f.split(" ")] + [np.nan]
    extra_var_counter = 0
    processed_list = [obj_f]
    for ineq in ineqs:
        ineq_list, extra_var_counter = ineq_to_std(ineq, extra_var_counter)
        processed_list.append(ineq_list)


    length = len(processed_list[-1])
    even_rows_len(processed_list, length)
    processed_list.append([np.nan]*length)
    print(processed_list)

    arr = np.array(processed_list) # tablica simplex
    base = [] # indeksy zmiennych, które są aktualnie w bazie

    return arr, base

def compute_last_row(arr):
    for col in range(1, arr.shape[1]-1): # wszystkie kolumny oprócz pomocniczej
        products = arr[1:-1, 0] * arr[1:-1, col]
        arr[-1, col] =  products.sum() - arr[0,col]

    products = arr[1:-1, 0] * arr[1:-1, -1]
    arr[-1, -1] =  products.sum()


def find_pivot(arr) -> tuple:
    if(arr[-1, 1:-2].min() >= 0):
        raise GoodEndException("Rozwiązanie optymalne")
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
                raise BadEndException("Rozwiązanie nieograniczone (wartość funkcji celu może być dowolnie duża)")

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
    names, obj_f, ineqs =  get_ineqs()
    print(names, obj_f, ineqs)

    try:
        arr, base = ineqs_to_array(obj_f, ineqs)
    except NameError as e:
        print(e)
        exit(0)

    if names == "": names = ["x1", "x2", "x3", "x4", "x5", "x6", "x7"]

    # PRZYKŁAD 1
    # arr = np.array([[np.nan,1,3,0,0,np.nan],[0,-1,1,1,0,1],[0,1,1,0,1,5], [np.nan]*6]) # 0. wiersz - f. celu, ostatni - pomocniczy 0. kolumna - przepisane z funkcji celu wart zmiennych w bazie
    # base = [3,4]       # zmienne numerowane od 1

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
            print("Nowa baza: ", [names[x-1] for x in base])
            recompute_array(arr, pivot)
            input()
        except BadEndException as e:
            print(e)
            break
        except GoodEndException as e:
            print("")
            print("\n", e, ":", sep="")
            for i in range(1, arr.shape[0]-1):
                print(names[base[i-1]-1], "* = ", arr[i, -1], sep="")
            print("reszta zmiennych = 0")
            print("optymalna wartość funkcji celu =", arr[-1,-1])
            break


    # wartości wewnętrznej macierzy dla zmiennych bazowych powinny tworzyć macierz jednostkową
    # wartości wiersza wskaźnikowego dla zmiennych bazowych powinny być 0
