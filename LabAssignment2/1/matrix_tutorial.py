import numpy as np

def main():
    # Question A
    M = np.arange(2, 27)
    print(M)

    # Question B
    M = M.reshape(5,5)
    print(M)
    
    # Question C
    M[1:4,1:4] *= 0
    print(M)

    # Question D
    M = M @ M
    print(M)

    # Question E
    v = M[0]
    mag = np.sqrt(np.sum(v ** 2))
    print(mag)

if __name__ == "__main__":
    main()
