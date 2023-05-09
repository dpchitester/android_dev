import config

# from config import edgepf


def main():
    global edgepf
    config.edgepf = "Abcdef"
    edgepf ="fedcbA"
    print(config.edgepf, edgepf)
    
if __name__=="__main__":
    main()