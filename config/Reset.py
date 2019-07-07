import os


def delete_dbs():
    dir_name = "../network/"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".db"):
            os.remove(os.path.join(dir_name, item))


delete_dbs()